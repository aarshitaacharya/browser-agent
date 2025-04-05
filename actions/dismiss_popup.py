async def handle_dismiss_popup(action, page):
    # Try default page elements first
    common_texts = [
        "Accept", "I agree", "Reject", "Stay signed out",
        "No thanks", "Dismiss", "Got it", "Continue without signing in"
    ]

    for text in common_texts:
        try:
            element = page.locator(f"text={text}")
            if await element.is_visible():
                await element.click()
                return f"Executed action: dismiss_popup ({text})"
        except:
            continue

    try:
        for frame in page.frames:
            for text in common_texts:
                try:
                    element = frame.locator(f"text={text}")
                    if await element.is_visible():
                        await element.click()
                        return f"Executed action: dismiss_popup (iframe - {text})"
                except:
                    continue
    except:
        pass

    return "Failed action: dismiss_popup - no known elements matched (iframe-aware)"
