from dataclasses import dataclass
import requests
from importlib import resources
from bs4 import BeautifulSoup
import re
import json
import pandas as pd
from urllib.parse import unquote_plus, quote_plus

# regexs for script 
_match_ele = r"(?<=decodeURIComponent\()(.+)(?=\"\)\)\;)"
_correct_ele_reg = r"([\ ]*e\ =\ document\.createElement\(\'ch-elements\.search-results\'\);)"


# helper functions to trim quotes 
def trim_quotes(my_string: str): 
    # trim leading and trailing quotes
    my_string =re.sub(pattern=r"([\'|\"]*)$", string=my_string, repl='')
    my_string = re.sub(pattern=r"^([\'|\"]*)", string=my_string, repl='')

    return my_string

def get_bourbons(bourbon_name: str = 'jack daniels', skip:int = None) -> pd.DataFrame: 
    """get_bourbons returns one page of bourbon details for the name provided

    Args:
        bourbon_name (str, optional): the name of the bourbon to check . Defaults to 'jack daniels'.
        skip (int, optional): the number of rows to skip for paging. Defaults to None.

    Raises:
        f: _description_

    Returns:
        pd.DataFrame: dataframe of bottle results
    """

    query_c = quote_plus(bourbon_name)
    skip_c = f"&skip={skip}" if skip is not None or skip != 0 else ''

    my_url = f"https://corkdorkswine.com/shop?ch-query={query_c}{skip_c}"
    get_page = requests.get(my_url)

    if get_page.status_code != 200: 
        raise f'ERROR {get_page.status_code}: {get_page.content.get("message")}'

    my_soup = BeautifulSoup(get_page.text, features='html.parser')

    for script in my_soup.select('script'): 

        # Check for previous element declared 
        correct_ele = bool(re.findall(_correct_ele_reg, script.text, flags=re.DOTALL))

        if correct_ele:
            match_data = re.findall(pattern=_match_ele, string=script.text, flags=re.DOTALL)
            my_text = trim_quotes(unquote_plus(match_data[0]))
            my_json = json.loads(my_text)
    
    # Product details 
    detail_frame = []
    for product in my_json.get("products"): 
        product_name = product.get("name")
        # merchant frame 
        merchant_frame = product.get("merchants")[0].get("product_options")[0]
        product_qty = merchant_frame.get("quantity")
        product_price = merchant_frame.get("price")
        original_price = merchant_frame.get("original_price")
        product_rating = product.get("product_rating")
        num_ratings = product.get("number_of_product_ratings")
        
        detail_frame.append(pd.DataFrame({
            "name": [product_name],
            "quantity": [product_qty],
            "price": [product_price],
            "original_price": [original_price],
            "rating": [product_rating],
            "number_ratings": [num_ratings]
        }))

    full_frame = pd.concat(detail_frame).reset_index(drop=True) if len(detail_frame) != 0 else pd.DataFrame
    return full_frame
 


def get_all_bourbons(bourbon_name: str = "jack daniels"): 
    """get_all_bourbons get all the bourbons on a page

    Args:
        bourbon_name (str, optional): the name to search for. Defaults to "jack daniels".

    Returns:
        _type_: _description_
    """

    _out_data = []
    new_data = get_bourbons(bourbon_name=bourbon_name)

    if new_data.empty: 
        return pd.DataFrame()

    _out_data.append(new_data)

    # now recursion over dataset
    skip_count = 0
    while len(new_data.index) == 18: 
        skip_count += 18
        new_data = get_bourbons(bourbon_name = bourbon_name, skip=skip_count)
        _out_data.append(new_data)

    flatten_df = pd.concat(_out_data).reset_index(drop=True)
    return flatten_df

if __name__ == "__main__": 
    test_bourbons = get_all_bourbons('blantons')
    print(test_bourbons)
