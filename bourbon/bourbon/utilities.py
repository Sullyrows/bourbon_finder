import logging
from pathlib import Path
from sys import stdout, stderr
import pandas as pd 
from playwright.sync_api import Playwright, Page
from importlib import resources
import datetime as dt 
import re

def setup_log(log_path: Path, logger_name = __name__): 
    
    formatter = "[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s"
    stream_fmt = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')

    logging.basicConfig(
        filename = log_path,
        level=logging.DEBUG,
        format=formatter,
        datefmt="%H:%M:%S",
        force=True
    )
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)

    # set up streams for logging stdout and err
    stream = logging.StreamHandler(stdout)
    err_stream = logging.StreamHandler(stderr)
    stream.setLevel(logging.DEBUG)
    err_stream.setLevel(logging.ERROR)
    stream.setFormatter(stream_fmt)
    err_stream.setFormatter(stream_fmt)
    logger.addHandler(stream)
    logger.addHandler(err_stream)


    return logger

# test logger config 
with resources.path("bourbon.logs","utility.log") as f: 
    log_path = f.absolute()
logger = setup_log(
    log_path = log_path, 
    logger_name = __name__
)

# individual run function
def run(playwright: Playwright) -> tuple:
    """run runs playwright to scrape buffalotrace visitor center

    Args:
        playwright (Playwright): the playwright session to use

    Returns:
        tuple: a tuple of (outbound_df, product_info_df)
    """
    logger.debug("Session started")
    browser = playwright.chromium.launch(headless=False)
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

