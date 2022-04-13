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
import sqlalchemy
from sqlalchemy import create_engine,true
from sqlalchemy.orm import sessionmaker,scoped_session


engine = create_engine('mysql://root:@localhost/party_scrapers_db')
con = engine.connect()
# import pdb;pdb.set_trace()
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
    category_id = 29
    Counter = 1
    website_data = []
    url = 'http://bounceplusllc.com'
   
    tree =  make_tree(url) 
    categories = tree.xpath('//div[contains(@class,"panel-default")]/div/h3')
    
    for category in categories:
        category_name = category.text
        if category_name == "Order-by-Date":
            continue
        category_id += 1
        # import pdb;pdb.set_trace()
        category_query = """INSERT INTO category(name,source) VALUES("{}",'bounceplusllc.com')""" .format(category_name)
        con.execute(category_query)
        # con.execute("INSERT INTO category(name,source) VALUES(%s,'allaboutfunga')" ,(category_name))

        category_href = category.get("onclick")
        category_href = category_href.split('"')
        category_href = str(category_href[1])
        category_page_url = ("{}{}" .format(url,category_href))
        category_page_tree = make_tree(category_page_url)
        for product in category_page_tree.xpath('//a[@class="more_info_text"]'):
            try:
                product_href = product.get("href")
                link = '{}{}'.format(url,product_href)
                product_page = requests.get(link)
                product_soupe = BeautifulSoup(product_page.content,"html.parser")
                product_tree = etree.HTML(str(product_soupe))
                product_name = product_tree.xpath("//h1")[0].text
                # import pdb;pdb.set_trace()
               
                if (product_tree.xpath("//li/span[contains(@class,'show_actual_size')]/text()")) :
                    product_dimentions = product_tree.xpath("//li/span[contains(@class,'show_actual_size')]/text()")
                    print(product_dimentions)
                elif(product_tree.xpath("//li/span[contains(@class,'show_setup_area')]/text()")):
                    product_dimentions = product_tree.xpath("//li/span[contains(@class,'show_setup_area')]/text()")
                    print(product_dimentions)
                else:
                    product_dimentions = "not found"
                
                product_price = product_tree.xpath("//font[contains(@class,'item_price')]")[0].text
                product_image = product_tree.xpath("//div[contains(@class,'col-xs-12 col')]/img")[0].get("src")
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
               
                
                if(con.execute("INSERT INTO product(name,price,url,img,dimensions,current_month_calendar,next_month_calendar,after_next_month_calendar,category_id,source) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,'bounceplusllc.com')" ,(product_name,product_price,link,product_image,product_dimentions,json.dumps(current_month),json.dumps(next_month),json.dumps(affter_next_month),category_id))):
                    print("data saved")
                else:
                    print("database query is not working")
                # except:
            
            except:
                continue   #     print("Add to cart button not found")
            
  
