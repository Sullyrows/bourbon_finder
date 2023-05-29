from playwright.async_api import async_playwright
from bourbon.utilities import buffalo_trace_avail
import asyncio

async def _main(): 
    async with async_playwright() as playwright: 
            browser = await playwright.chromium.launch(
                headless=False
            )
            my_context =  await browser.new_context()
            my_page = await my_context.new_page()

            product_data, product_info = await buffalo_trace_avail(my_page)

            await my_page.close()
            await my_context.close()

if __name__ == "__main__": 
    asyncio.get_event_loop().run_until_complete(_main())