from PIL import Image, ImageFilter
import pytesseract
import asyncio
import io

async def solve_amazon_captcha(page):
    try:
        print("🔍 Looking for Amazon CAPTCHA...")

        await page.wait_for_selector("img[src*='captcha']", timeout=10000)
        captcha_img = await page.query_selector("img[src*='captcha']")
        if not captcha_img:
            return "❌ CAPTCHA image not found"

        for attempt in range(3):
            print(f"🔁 Attempt {attempt + 1}/3")

            # Get screenshot in memory (bytes)
            img_bytes = await captcha_img.screenshot(type="png")
            img = Image.open(io.BytesIO(img_bytes))

            # Preprocess
            img = img.resize((img.width * 2, img.height * 2), Image.LANCZOS)
            img = img.convert("L")
            img = img.filter(ImageFilter.MedianFilter())
            img = img.point(lambda x: 0 if x < 160 else 255, '1')
            img = img.filter(ImageFilter.SHARPEN)

            # OCR
            config = "--psm 7 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
            captcha_text = pytesseract.image_to_string(img, config=config).strip()
            captcha_text = ''.join(filter(str.isalnum, captcha_text))[:6]

            print(f"🔤 OCR result: '{captcha_text}' (len: {len(captcha_text)})")

            if len(captcha_text) == 6:
                input_field = await page.query_selector("#captchacharacters")
                if not input_field:
                    return "❌ CAPTCHA input field not found"

                await input_field.click()
                await asyncio.sleep(0.5)
                await input_field.fill(captcha_text)
                await asyncio.sleep(1)
                await page.keyboard.press("Enter")
                print("📩 Submitted CAPTCHA attempt")

                await asyncio.sleep(2)

                if not await page.is_visible("img[src*='captcha']"):
                    return "✅ CAPTCHA passed!"
                else:
                    print("🔁 CAPTCHA failed, retrying...")
                    captcha_img = await page.query_selector("img[src*='captcha']")  # refresh

        return "❌ Failed all CAPTCHA attempts"

    except Exception as e:
        return f"🚨 CAPTCHA solver failed: {e}"
