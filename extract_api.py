from fastapi import APIRouter, Request
from playwright.async_api import Page

router = APIRouter()

async def extract_elements(page: Page):
    clickable_elements = await page.query_selector_all("a, button, input[type='submit'], img")

    extracted = []
    for el in clickable_elements:
        try:
            tag = await el.evaluate("e => e.tagName")
            text = await el.inner_text() or ""
            alt = await el.get_attribute("alt") or ""
            src = await el.get_attribute("src") or ""
            href = await el.get_attribute("href") or ""
            selector = await page.evaluate("el => el.outerHTML", el)

            extracted.append({
                "tag": tag,
                "text": text.strip(),
                "alt": alt.strip(),
                "src": src,
                "href": href,
                "selector_snippet": selector[:150]  
            })
        except Exception as e:
            continue

    return extracted

@router.post("/extract")
async def extract_api(request: Request):
    page = request.app.state.page

    if not page:
        return {"error": "No active browser page"}

    extracted = await extract_elements(page)
    return {"elements": extracted, "count": len(extracted)}
