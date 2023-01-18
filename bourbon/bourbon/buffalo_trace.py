from playwright.sync_api import Playwright, sync_playwright
import pandas as pd 
from importlib import resources 
import sqlalchemy 
import logging
from pathlib import Path
import sqlite3
import re
import datetime as dt
from os import environ
from prefect import flow

# removing relative imports because of the staleness of prefect

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


with resources.path("bourbon.logs",f"buffalo_trace_{dt.datetime.now().strftime('%Y%m01')}.log") as f: 
    log_path = f.absolute()

logger = setup_log(log_path=log_path, logger_name = __name__)

# get Chron Schedule
# cron_schedule = Deplo

# total job 
@flow(
    name='buffalo_trace_job',
    description="scrape data on product availability",
    version=environ.get("GIT_COMMIT_SHA")
)
def buffalo_trace_job():
    """buffalo_trace_job generate current supply availability data
    """
    # connect to database 
    with resources.path("bourbon","buffalo_trace.db") as f: 
        native_conn = sqlite3.connect(f)
        my_driver = sqlalchemy.create_engine(f"sqlite:////{f.absolute()}")
        
        latest_date = dt.datetime.strptime(native_conn.execute("select max(update_date) from product_avail").fetchone()[0], '%Y-%m-%d %H:%M:%S.%f')
    logger.debug("connected")

    # build playwright session
    with sync_playwright() as playwright:
        my_data, product_info = run(playwright)

        # determine if I need to push batch to sql 
        run_time = my_data.loc[0,'update_date'].to_pydatetime()
        if run_time != latest_date: 
            my_data.to_sql('product_avail', my_driver, index=False, if_exists='append')
            logger.debug("updated primary dataset")
        else: 
            logger.info("not updating main dataset, already current")

        # update urls for image
        product_info.to_sql('product_ext', my_driver, index=False, if_exists='replace')
        logger.debug("updated product info")
    my_driver.dispose()

if __name__ == "__main__": 
    # execute flow 
    buffalo_trace_job()