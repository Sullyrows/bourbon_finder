import logging
from pathlib import Path
from sys import stdout, stderr
import pandas as pd 
from playwright.sync_api import Playwright, Page
from importlib import resources
import datetime as dt 
import re

def setup_log(log_path: Path, logger_name = __name__): 
    
    log_fmt = logging.Formatter("[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s",datefmt="%H:%M:%S")
    stream_fmt = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')

    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)

    # set up streams for logging stdout and err
    stream = logging.StreamHandler(stdout)
    stream.setLevel(logging.DEBUG)
    stream.setFormatter(stream_fmt)
    logger.addHandler(stream)

    # err formatting for stdout
    err_stream = logging.StreamHandler(stderr)
    err_stream.setLevel(logging.ERROR)
    err_stream.setFormatter(stream_fmt)
    logger.addHandler(err_stream)

    fileHandler = logging.FileHandler(filename='test.log')
    fileHandler.setFormatter(log_fmt)
    fileHandler.setLevel(level=logging.INFO)

    logger.addHandler(fileHandler)

    return logger

# test logger config 
with resources.path("bourbon.logs","utility.log") as f: 
    log_path = f.absolute()
logger = setup_log(
    log_path = log_path, 
    logger_name = __name__
)


async def buffalo_trace_avail(my_page: Playwright): 

    await my_page.goto("https://www.buffalotracedistillery.com/product-availability")


    await my_page.get_by_role("button", name="Yes").click()

    # selector 
    img_sel = "div > div > div.image.section > div > img"
    title_sel = "div > div > div.title.section > div.cmp-title > h3"
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
    product_title = []
    product_image = []
    product_available = []

    # parent selector
    element_sel = "div#product-availability-bottle-container > div > div.container.section"
    my_queried_elements = await my_page.query_selector_all(element_sel)
    for ind, ele in enumerate(my_queried_elements): 
        # image via property 
        image_prop_1 = await ele.query_selector('div > div > div.image.section > div.cmp-image')
        image_prop = image_prop_1.get_attribute('data-asset')
        image_link = f"http://buffalotracedistillery.com{image_prop}"
        title = await ele.query_selector(title_sel)
        title = title.text_content()
        # check url computed value in evaluate loop context
        avail_frame = await ele.query_selector(".product-availability-icon")
        computed_value = await avail_frame.evaluate(js_fx, {"element": avail_frame})
        product_avail_flag = computed_value == 'url("https://www.buffalotracedistillery.com/content/dam/buffalotracedistillery/landing-pages/product-availability/images/product-availability-available.png")'

        product_title.append(title)
        product_image.append(image_link)
        product_available.append(product_avail_flag)

    output_df = pd.DataFrame({
        "product_title": product_title,
        "update_date": full_parse,
        "product_available": product_available
    })

    product_df = pd.DataFrame({
        "product_title": product_title,
        "product_image": product_image
    })

    return(output_df, product_df)


# individual run function
def run(playwright: Playwright) -> tuple:
    """run runs playwright to scrape buffalotrace visitor center

    Args:
        playwright (Playwright): the playwright session to use

    Returns:
        tuple: a tuple of (outbound_df, product_info_df)
    """
    logger.debug("Session started")
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context()

    page = context.new_page()

    page.goto("https://www.buffalotracedistillery.com/product-availability")

    page.get_by_role("button", name="Yes").click()

    # selector 
    img_sel = "div > div > div.image.section > div > img"
    title_sel = "div > div > div.title.section > div.cmp-title > h3"
    avail_sel = "div > div > div.htmlblock.section > div > div.product-availability-text > h4.product-is-available"

    # the time updated
    update_time = page.locator("#container-eed96a5a0f > div > div:nth-child(2) > div > h2").text_content()
    mid_parse = re.findall(r'(?<=Updated: ).+',update_time, re.DOTALL)[0]
    full_parse = dt.datetime.strptime(mid_parse, "%I:%M %p  %m/%d/%Y")

    # empty fields for dataframe population 
    product_title = []
    product_image = []
    product_available = []

    # parent selector
    element_sel = "div#product-availability-bottle-container > div > div.container.section"
    for ind, ele in enumerate(page.query_selector_all(element_sel)): 
        # image via property 
        image_prop = ele.query_selector('div > div > div.image.section > div.cmp-image').get_attribute('data-asset')
        image_link = f"http://buffalotracedistillery.com{image_prop}"
        title = ele.query_selector(title_sel).text_content()
        avail = not ele.query_selector(avail_sel).is_hidden()

        product_title.append(title)
        product_image.append(image_link)
        product_available.append(avail)

    output_df = pd.DataFrame({
        "product_title": product_title,
        "update_date": full_parse,
        "product_available": product_available
    })

    product_df = pd.DataFrame({
        "product_title": product_title,
        "product_image": product_image
    })
    logger.debug("Data assembled")

    # ---------------------
    context.close()
    browser.close()

    return (output_df, product_df)

