from playwright.sync_api import Playwright, sync_playwright, expect, Page
import pandas as pd 
from importlib import resources 
from bs4 import BeautifulSoup

def check_invisible_ele(page: Page): 
    ele_avail = page.eval_on_selector(
        selector="textarea", # Modify the selector to fit yours.
        expression="(el) => el.style.display = 'inline-block'",
    )
    return ele_avail


def old_run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()

    page = context.new_page()

    page.goto("https://www.buffalotracedistillery.com/product-availability")

    page.get_by_role("button", name="Yes").click()

    # list selector 
    img_selector = "img[class=\"cmp-image__image\"]"
    title_selector = "div > div.title.section > div > h3"
    avail_selector = "div.cmp-htmlblock > div.product-availability-text > h4.product-is-available"


    page.wait_for_selector(title_selector, timeout=6*1000)

    # get elements 
    update_time = page.locator("#container-eed96a5a0f > div > div:nth-child(2) > div > h2").text_content()
    titles = [x.text_content() for x in page.query_selector_all(title_selector)]
    img_comp = [f'http://buffalotracedistillery.com/{x.get_attribute("src")}' for x in page.query_selector_all(img_selector)]

    # determine availability
    product_availability = [not x.is_hidden() for x in page.query_selector_all(avail_selector)]

    page.get_by_role("heading", name="Sold Out").first.dblclick()

    # ---------------------
    context.close()
    browser.close()


def run(playwright: Playwright) -> None:
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

    # empty fields for dataframe population 
    product_title = []
    product_image = []
    product_available = []

    # parent selector
    element_sel = "div#product-availability-bottle-container > div > div.container.section"
    for ind, ele in enumerate(page.query_selector_all(element_sel)): 
        # image via property 
        image_prop = ele.query_selector('div > div > div.image.section > div.cmp-image').get_attribute('data-asset')
        image_link = f"http://buffalotracedistillery.com/{image_prop}"
        title = ele.query_selector(title_sel).text_content()
        avail = not ele.query_selector(avail_sel).is_hidden()

        product_title.append(title)
        product_image.append(product_image)
        product_available.append(avail)

    output_df = pd.DataFrame({
        "product_title": product_title,
        "product_image": product_image,
        "product_available": product_available
    })

    # ---------------------
    context.close()
    browser.close()

    return output_df


if __name__ == "__main__": 

    with sync_playwright() as playwright:
        my_data = run(playwright)
