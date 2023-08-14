import asyncio 
from playwright.async_api import async_playwright
from bourbon.bin.buffalo_trace import buffalo_trace_main

if __name__ == "__main__": 
    my_policy = asyncio.get_event_loop_policy()

    my_loop = my_policy.new_event_loop()

    my_data = my_loop.run_until_complete(buffalo_trace_main())

    my_loop.close()