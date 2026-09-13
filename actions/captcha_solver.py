import io
import asyncio
from playwright.async_api import Page
from utils.logger import logger

# Pillow and pytesseract are only needed for CAPTCHA solving, which the README
# lists as optional. Importing them at module scope made them a hard dependency
# of the whole app, since actions/goto.py imports this module on startup.
try:
    from PIL import Image, ImageFilter
    import pytesseract

    OCR_AVAILABLE = True
except ImportError:  # pragma: no cover - depends on local install
    Image = ImageFilter = pytesseract = None
    OCR_AVAILABLE = False


async def solve_amazon_captcha(page: Page) -> str:
    """
    Detects and solves CAPTCHA on Amazon pages using OCR (Tesseract).

    Args:
        page (Page): The current Playwright browser page.

    Returns:
        str: Status message indicating CAPTCHA solve result.
    """
    if not OCR_AVAILABLE:
        logger.info("Skipping CAPTCHA solve: pillow/pytesseract are not installed.")
        return "CAPTCHA solving unavailable - install pillow and pytesseract"

    try:
        logger.info("Searching for CAPTCHA image on the page.")

        await page.wait_for_selector("img[src*='captcha']", timeout=10000)
        captcha_img = await page.query_selector("img[src*='captcha']")
        if not captcha_img:
            logger.warning("CAPTCHA image not found on the page.")
            return "CAPTCHA image not found"

        for attempt in range(10):
            logger.info(f"Solving attempt {attempt + 1}/10")

            # Capture screenshot in memory
            img_bytes = await captcha_img.screenshot(type="png")
            img = Image.open(io.BytesIO(img_bytes))

            # Preprocess image
            img = preprocess_image(img)

            # OCR
            config = "--psm 7 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
            captcha_text = pytesseract.image_to_string(img, config=config).strip()
            captcha_text = ''.join(filter(str.isalnum, captcha_text))[:6]

            logger.info(f"OCR result: '{captcha_text}' (length: {len(captcha_text)})")

            if len(captcha_text) == 6:
                input_field = await page.query_selector("#captchacharacters")
                if not input_field:
                    logger.error("CAPTCHA input field not found.")
                    return "CAPTCHA input field not found"

                await input_field.click()
                await asyncio.sleep(0.5)
                await input_field.fill(captcha_text)
                await asyncio.sleep(1)
                await page.keyboard.press("Enter")
                logger.info("Submitted CAPTCHA input.")

                await asyncio.sleep(2)

                if not await page.is_visible("img[src*='captcha']"):
                    logger.info("CAPTCHA solved successfully.")
                    return "CAPTCHA passed"
                else:
                    logger.info("CAPTCHA not cleared, retrying...")
                    captcha_img = await page.query_selector("img[src*='captcha']")

        logger.warning("All CAPTCHA solving attempts failed.")
        return "Failed all CAPTCHA attempts"

    except Exception as e:
        logger.exception("CAPTCHA solver encountered an error.")
        return f"CAPTCHA solver failed: {e}"


def preprocess_image(img: "Image.Image") -> "Image.Image":
    """
    Applies preprocessing to an image to improve OCR accuracy.

    Args:
        img (Image.Image): The raw PIL image.

    Returns:
        Image.Image: The processed image ready for OCR.
    """
    img = img.resize((img.width * 2, img.height * 2), Image.LANCZOS)
    img = img.convert("L")
    img = img.filter(ImageFilter.MedianFilter())
    img = img.point(lambda x: 0 if x < 160 else 255, '1')
    img = img.filter(ImageFilter.SHARPEN)
    return img
