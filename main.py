import os

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import csv
import re

from db.commands import create_meta, create_category, create_product
from db.engine import start_engine
from models import Category, Product

load_dotenv()

headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
    'Cache-Control': 'max-age=0',
    'Connection': 'keep-alive',
    'Content-Type': 'application/x-www-form-urlencoded',
    'Origin': 'https://www.makoffmarket.ru',
    'Referer': 'https://www.makoffmarket.ru/client_account/session/new',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-User': '?1',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36',
    'sec-ch-ua': '"Google Chrome";v="117", "Not;A=Brand";v="8", "Chromium";v="117"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
}


def get_cookie():
    data = {}
    data['DATA_EMAIL'] = os.getenv('EMAIL')
    data['DATA_PASSWORD'] = os.getenv('PASSWORD')
    data['commit'] = ''
    response = requests.post('https://www.makoffmarket.ru/client_account/session', headers=headers, data=data)
    return response.cookies


def parser(url: str):
    engine = start_engine()
    create_meta(engine)
    parse_category(engine, url, cookies=get_cookie())


def parse_category(engine, url: str, cookies, parent_category_id=None):
    # Заходим по ссылке
    res = requests.get(url, cookies)
    soup = BeautifulSoup(res.text, "lxml")
    catalog_cards = soup.select('div.product-card-inner:not(.product-list-card-inner)')
    product_cards = soup.select('div.product-card-inner.product-list-card-inner')
    print()
    for product in product_cards:
        name = product.find("a", class_="product-link").text.strip()
        url = product.find("a", class_="product-link")["href"]
        img_url = ""
        price = product.find("div", class_="price").text.strip()
        price = price.replace("&nbsp;", "").replace(",", ".")
        price = re.sub(r'\D', '', price)
        print(f"Продукт добавлен {name}, цена{price}")
        prod = Product(name=name, category_id=parent_category_id, url=url, price=price)
        create_product(engine, name, price, url, img_url, parent_category_id)

    for category in catalog_cards:
        href = category.find("a")["href"].strip()
        name = category.find('a', {'class': 'product-link'}).text.strip()
        img_url = category.find('img', {'class': 'product-card-image'})['src']

        print(f"Категория найдена {name}")

        id = create_category(engine, parent_category_id, name, href, img_url)

        parse_category(engine, os.getenv('BASE_URL') + href, cookies, parent_category_id=id)

    return


def remove_non_latin_cyrillic(text):
    # Оставляем только символы латиницы и кириллицы
    pattern = r'[^a-zA-Zа-яА-Я]+'
    return re.sub(pattern, '', text)


def save_data_to_file(categories, products, filename):
    with open(filename, "w") as f:
        # Write categories to file
        f.write("Categories:\n")
        for category in categories:
            f.write(
                f"Id:{category.id}, Категория: {category.name}, Ссылка на картинку:{category.img_url}, Ссылка на категорию:{category.url},\n")

        # Write products to file
        f.write("\nProducts:\n")
        for product in products:
            f.write(
                f"Название продукта:{product.name}, {product.category_id}, Цена:{product.price}, Ссылка:{product.url}\n")


if __name__ == '__main__':
    load_dotenv()
    parser(url=os.getenv('tabaco_url'))

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
