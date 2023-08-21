from playwright.async_api import async_playwright
from bourbon.get_buffalo_trace import buffalo_trace_avail
import asyncio
import pandas as pd
import sqlalchemy
from importlib import resources
from bourbon.log_fx import setup_log

with resources.path("bourbon.logs", "main_buffalo_trace.log") as f:
    logger = setup_log(f, logger_name="main_buffalo_trace")


async def main_buffalo_trace() -> pd.DataFrame:
    """setup browser and download buffalo trace"""
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=True)
        my_context = await browser.new_context()
        my_page = await my_context.new_page()

        product_data = await buffalo_trace_avail(my_page)

        await my_page.close()
        await my_context.close()

    return product_data


if __name__ == "__main__":
    policy = asyncio.get_event_loop_policy()
    loop = policy.get_event_loop()

    new_products = loop.run_until_complete(main_buffalo_trace())

    loop.close()

    # Connect to database
    with resources.path("bourbon", "buffalo_trace.db") as f:
        engine = sqlalchemy.create_engine(f"sqlite:////{f.absolute()}")

        # Test connection
        with engine.connect() as conn:
            with conn.begin():
                sql_version = conn.execute(
                    sqlalchemy.text("select sqlite_version()")
                ).fetchone()[0]

                logger.info(f"Sqlalchemy running on version {sql_version}")

            # get last updated datetime
            update_time_txt = sqlalchemy.text(
                    """select MAX(product_update_time) from buffalo_trace"""
                )
            latest_update_time = conn.execute(
                update_time_txt
            ).fetchone()[0]

            product_time = new_products.loc[0, "product_update_time"]
            new_data_flag = (
                # noqa: E501
                latest_update_time == product_time
            )

            if new_data_flag:
                logger.info("no new rows to upload")
            else:
                logger.info("uploading new rows")

                new_products.to_sql(
                    name="buffalo_trace", con=engine, if_exists="append"
                )
                logger.info(f"wrote {len(new_products.index)} rows")
