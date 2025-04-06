async def handle_click(action, page):
    selector = action.get("selector")
    target = action.get("target", "link")
    position = action.get("position", 0)
    results = []

    # Try selector first
    if selector:
        try:
            await page.wait_for_selector(selector, timeout=5000)
            await page.click(selector)
            return f"Executed action: click (selector)"
        except Exception as e:
            results.append(f"Selector failed: {selector}, error: {e}")

    # Map known targets to selectors
    selector_map = {
        "link": "a[href]",
        "video": "ytd-video-renderer a#thumbnail, a[href]",
        "button": "button, [role='button'], input[type='submit']",
        "image": "img",
        "input": "input, textarea",
        "any": "a[href], button, [role='button'], input",
    }

    target_selector = selector_map.get(target, selector_map["any"])
    elements = page.locator(target_selector)
    count = await elements.count()

    if count == 0:
        return f"Failed action: click - no {target} elements found"

    # Handle negative positions like -1 (last)
    if position < 0:
        position = count + position

    if position >= count or position < 0:
        return f"Failed action: click - invalid position ({position}) for {count} elements"

    try:
        element = elements.nth(position)
        await element.scroll_into_view_if_needed()
        await element.click()
        return f"Executed action: click {target} #{position + 1}"
    except Exception as e:
        return f"Failed action: click {target} #{position + 1} - {e}"
