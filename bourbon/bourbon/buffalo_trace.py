from playwright.sync_api import Playwright, sync_playwright
from playwright.async_api import async_playwright, expect
import pandas as pd 
from sys import stdout, stderr
from importlib import resources 
import sqlalchemy 
import logging
from pathlib import Path
import sqlite3
import re
import datetime as dt
from bourbon.utilities import setup_log, run
from os import environ
from prefect import flow

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