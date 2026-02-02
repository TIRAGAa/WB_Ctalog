# import requests
import json
import pandas as pd


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
    url = f"https://www.wildberries.ru/__internal/u-search/exactmatch/ru/common/v18/search?ab_testing=false&appType=1&curr=rub&dest=-1257786&hide_dtype=9&hide_vflags=4294967296&inheritFilters=false&lang=ru&query={conv_utf8(query)}&resultset=catalog&sort=popular&spp=30&suppressSpellcheck=false"
    headers = {
        "User-Agent": "0",
        "Authorization": "0",
        "Cookie": "0",
        "X-API-Key": "0",
        "Accept": "*/*",
        "Content-Type": "0"
        }
    response = requests.get(url=url, headers=headers)
    print(response.status_code)
    print(response.url)
    return response


def get_catalog():
    """Чтение данных из локального JSON файла."""
    with open("detal.json", "r", encoding="utf-8") as file:
        data = json.load(file)

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
    # sample_query = "пальто из натуральной шерсти"
    # data = get_data_from_wildberries(sample_query)
    data = get_catalog()
    df = pd.DataFrame(data)

    try:
        with pd.ExcelWriter('товары.xlsx') as writer:
            df.to_excel(writer, sheet_name='Каталог', index=False)
        print("Данные сохранены в 'catalog.xlsx'")
    except Exception as e:
        print(f"Ошибка: {e}")
