from calendar import month
import calendar
from sre_constants import CATEGORY
from tkinter.tix import Tree
from typing import Counter
from bs4 import BeautifulSoup
from lxml import etree
from lxml import html
import json
from numpy import choose
import requests
from datetime import date, datetime
from requests.structures import CaseInsensitiveDict
def remove_slashes_from_response(response):
    response = response.text.replace("\'", "'")
    response = response.replace("\'", "'")
    response = response.replace("\t", "")
    response = response.replace("\r", "")
    response = response.replace("\n", "") 
    return response
def make_tree(url):
    website = requests.get(url)
    soupe = BeautifulSoup(website.content,"html.parser")
    tree = etree.HTML(str(soupe)) 
    return tree   
if __name__ == "__main__":
    Counter = 1
    website_data = []
    url = 'http://bounceplusllc.com'
    tree =  make_tree(url) 
    categories = tree.xpath('//div[contains(@class,"panel-default")]/div/h3')
    for category in categories:
        category_name = category.text
        if category_name == "Order-by-Date":
            continue

        category_href = category.get("onclick")
        category_href = category_href.split('"')
        category_href = str(category_href[1])
        category_page_url = ("{}{}" .format(url,category_href))
        category_page_tree = make_tree(category_page_url)
        for product in category_page_tree.xpath('//a[@class="more_info_text"]'):
            try:    
                product_href = product.get("href")
                product_href = ("{}{}" .format(url,product_href))
                product_tree = make_tree(product_href)
                product_name = product_tree.xpath("//h1")[0].text
                product_dimentions = product_tree.xpath("//li/span[contains(@class,'actual_size')]/text()")
                product_price = product_tree.xpath("//font[contains(@class,'item_price')]")[0].text
                product_id = product_tree.xpath("//div[contains(@id,'book_button')]")[0].get("id")[12:]
                next_month = dict()
                current_month = dict()
                affter_next_month = dict()
                for i in range(3):
                    month_number = datetime.today().month + i
                    year = datetime.today().year
                    chose_date_url = ('{}{}?render_frame=store.item.calendar&root_path=&cart_itemid=0&mobile_itemid=allaboutfun_id_74231&store_mode=&store_submode=calendar&set_cal_year={}&set_cal_month={}&itemid={}&rnd=0.010081543359742984&ajtype=inner'.format(url,product_href,year,month_number,product_id))
                    Add_to_cart_page_tree = make_tree(chose_date_url)
                    booked_dates =  Add_to_cart_page_tree.xpath("//div[contains(@onmouseout,'bbbbbb')]/text()")
                    booked_dates = [x.strip('\r\n\t\t\t') for x in booked_dates]
                    booked_dates = [x.strip(' ') for x in booked_dates]
                    available_dates = Add_to_cart_page_tree.xpath("//div[contains(@onmouseover,'#c7c9c1')]/text()")
                    available_dates = [x.strip('\r\n    \r\n                                \r\n\t\t') for x in available_dates]
                    available_dates = [x.strip(' ') for x in available_dates]
                    if month_number == datetime.now().month:
                        current_month["Month"] = calendar.month_name[month_number]
                        current_month["available_dates"] = available_dates
                        current_month["Booked_dates"] = booked_dates
                    if month_number == datetime.now().month + 1:
                        next_month["Month"] = calendar.month_name[month_number]
                        next_month["available_dates"] = available_dates
                        next_month["Booked_dates"] = booked_dates
                    if month_number == datetime.now().month + 2:
                        affter_next_month["Month"] = calendar.month_name[month_number]
                        affter_next_month["available_dates"] = available_dates
                        affter_next_month["Booked_dates"] = booked_dates
                website_data.append({
                    "categoy-name" : category_name,
                    "product_name" : product_name,
                    "product_price": product_price,
                    "product_dimentions": product_dimentions,
                    "availability": [current_month,next_month,affter_next_month]

                })
             
            except:
                continue    
            print(Counter)
            Counter = Counter + 1
            
    website_data = json.dumps(website_data)                        
    print(website_data)
