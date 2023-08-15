import pytest
import pytest_asyncio
import pandas as pd
import asyncio
from playwright.async_api import async_playwright, expect
from get_buffalo_trace import buffalo_trace_avail

# required asyncio event loop fixture 
@pytest.fixture(scope="session")
def event_loop():
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def browser_context(headless:bool = True): 
    """browser_context 
    
    develop asyncronous browser context 

    Yields:
        page: Playwright context
    """
    async with async_playwright() as playwright: 
        browser = await playwright.chromium.launch(
            headless=headless
        )
        my_context =  await browser.new_context()
        my_page = await my_context.new_page()
        yield my_page
        await my_page.close()
        await my_context.close()


@pytest.mark.asyncio
async def test_main_fx(browser_context): 
    my_page = browser_context
    # run function

    await buffalo_trace_avail(my_page)

    assert my_page.url == "https://www.buffalotracedistillery.com/product-availability"