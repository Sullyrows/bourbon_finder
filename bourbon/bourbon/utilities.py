import logging
from pathlib import Path
from sys import stdout, stderr
import pandas as pd 
from playwright.sync_api import Playwright, Page, expect
from importlib import resources
import datetime as dt 
import re
from .log_fx import setup_log


# test logger config 
with resources.path("bourbon.logs","utility.log") as f: 
    log_path = f.absolute()


logger = setup_log(
    log_path = log_path, 
    logger_name = __name__
)


async def buffalo_trace_avail(my_page: Page) -> pd.DataFrame:

    await my_page.goto("https://www.buffalotracedistillery.com/product-availability")

    await my_page.wait_for_load_state('networkidle')

    await my_page.get_by_role("button", name="Yes").click()

    # selector 
    title_sel = "div.cmp-title > h3"
    avail_sel = "div > div > div.htmlblock.section > div > div.product-availability-text > h4.product-is-available"

    # the time updated
    # the time updated
    update_time = await my_page.locator("#container-eed96a5a0f > div > div:nth-child(2) > div > h2").text_content()
    mid_parse = re.findall(r'(?<=Updated: ).+',update_time, re.DOTALL)[0]
    full_parse = dt.datetime.strptime(mid_parse, "%I:%M %p  %m/%d/%Y")

    # get icon status evaluate 
    js_fx = """(element) =>
    window.getComputedStyle(element).getPropertyValue('background-image')"""
    js_fx_2 = """function css_scrape(element){
    window.getComputedSytle(element).getPropertyValue('background-image')
    }
    """

    # empty fields for dataframe population 
    df_list = []

    # parent selector
    element_sel = "div.container.section.container--justify-center > div.cmp-container.cmp-container__responsive"

    query_ele = my_page.locator(element_sel)
    num_elements = await query_ele.count()
    ele_frame = [query_ele.nth(x) for x in range(0,num_elements)]

    logger.debug(f"There are currently {len(ele_frame)} products.")

    for ind, ele in enumerate(ele_frame): 
        image_prop = ele.locator("div.product-availability-icon")
        await my_page.wait_for_selector(selector="div.product-availability-icon",timeout=2000)
        title_present = await image_prop.is_visible()

        if not title_present:
            continue

        image_prop = ele.locator('div.product-availability-icon')
        image_value = await image_prop.get_attribute("data-asset")
        image_link = f"http://buffalotracedistillery.com{image_value}"

        title = ele.locator(title_sel)

        # get computed for availablility
        avail_frame = ele.locator(".product-availability-icon")
        computed_value = await avail_frame.evaluate(js_fx, {"element": avail_frame})
        product_avail_flag = (computed_value == 'url("https://www.buffalotracedistillery.com/content/dam/buffalotracedistillery/landing-pages/product-availability/images/product-availability-available.png")')

        df_list.append({
            "product_title": await title.inner_text(),
            "product_update_time": full_parse,
            "product_avail": product_avail_flag
        })


    out_df = pd.DataFrame(df_list)
    out_df["data_update_time"] = dt.datetime.now()

    logger.debug(f"output dataframe has size: {out_df.size}")

    return out_df