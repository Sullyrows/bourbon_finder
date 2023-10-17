import asyncio 
from playwright.async_api import async_playwright
from bourbon.bin.run_buffalo_trace import main_buffalo_trace

if __name__ == "__main__": 
    my_policy = asyncio.get_event_loop_policy()

    my_loop = my_policy.new_event_loop()

    my_data = my_loop.run_until_complete(main_buffalo_trace())

    my_loop.close()