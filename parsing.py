import os
import requests
import pandas as pd
from dotenv import load_dotenv

load_dotenv()


def get_link(type: str, id: int) -> str:
    if type == "product":
        return f"https://www.wildberries.ru/catalog/{id}/detail.aspx"
    elif type == "seller":
        return f"https://www.wildberries.ru/brands/{id}"
    else:
        raise ValueError("Invalid type. Must be 'product' or 'seller'.")


def conv_utf8(text: str) -> str:
    """Преобразование строки в URL-кодированную UTF-8 строку."""
    bytes_utf8 = text.encode('utf-8')
    url_encoded = ''.join(f'%{byte:02X}' for byte in bytes_utf8)
    return url_encoded


def get_data_from_wildberries(query: str):
    """Получение данных с Wildberries по заданному запросу."""
    url = f"{os.getenv('URL_BF')}{conv_utf8(query)}{os.getenv("URL_AF")}"
    headers = {
        "Cookie": os.getenv('COOKIE'),
        "Accept": os.getenv('ACCEPT'),
        "User-Agent": os.getenv('USER_AGENT')
    }
    response = requests.get(url=url, headers=headers)
    return response.json()


def get_catalog(data):
    """Изьятие нужных данных из JSON"""
    results = []
    for product in data['products']:
        info_item = {
            "Ссылка": get_link("product", product["id"]),
            "Артикул": product["id"],
            "Название": product["name"],
            "Цена в рублях": product["sizes"][0]["price"]['product'] / 100,
            "Продавец": product["brand"],
            "Ссылка на продавца": get_link("seller", product['brandId']),
            "Размеры": [x["name"] for x in product["sizes"]],
            "Оценка": product['rating'],
            "Кл Отзывов": product['feedbacks'],
        }
        results.append(info_item)
    return results


if __name__ == "__main__":
    sample_query = "пальто из натуральной шерсти"
    data = get_catalog(get_data_from_wildberries(sample_query))
    df = pd.DataFrame(data)

    try:
        with pd.ExcelWriter('catalog.xlsx') as writer:
            df.to_excel(writer, sheet_name='Каталог', index=False)
        print("Данные сохранены в 'catalog.xlsx'")
    except Exception as e:
        print(f"Ошибка: {e}")
