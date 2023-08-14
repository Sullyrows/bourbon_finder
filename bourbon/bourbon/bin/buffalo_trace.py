from playwright.async_api import async_playwright
from ..utilities import buffalo_trace_avail 
import asyncio

async def buffalo_trace_main() -> dict: 
    async with async_playwright() as playwright: 
            browser = await playwright.chromium.launch(
                headless=False
            )
            my_context =  await browser.new_context()
            my_page = await my_context.new_page()

            await my_page.goto("https://www.buffalotracedistillery.com/product-availability")
            await my_page.wait_for_load_state('networkidle')
            
            product_data = await buffalo_trace_avail(my_page)

            await my_page.close()
            await my_context.close()
    return product_data

