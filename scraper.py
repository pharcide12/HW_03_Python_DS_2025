import requests
import time
from bs4 import BeautifulSoup

# Настройки с отключением предупреждений SSL
requests.packages.urllib3.disable_warnings()


def get_book_data(url):
    """Получает данные об одной книге"""
    try:
        r = requests.get(url, verify=False, timeout=10)
        r.raise_for_status()
    except Exception as e:
        print("Ошибка загрузки книги:", e)
        return None

    soup = BeautifulSoup(r.text, "html.parser")

    title = soup.find("h1").text.strip() if soup.find("h1") else "Нет названия"
    price = soup.find("p", class_="price_color").text.strip() if soup.find("p", class_="price_color") else "Нет цены"
    avail = soup.find("p", class_="instock availability").text.strip() if soup.find("p", class_="instock availability") else "Нет данных"

    rating_tag = soup.find("p", class_="star-rating")
    rating = rating_tag["class"][1] if rating_tag and len(rating_tag["class"]) > 1 else "No rating"

    return {
        "title": title,
        "price": price,
        "availability": avail,
        "rating": rating
    }


def scrape_books(pages=3, is_save=True):
    """Парсит страницы каталога (новый стабильный сайт)"""
    base = "http://books.toscrape.com/catalogue/page-{}.html"
    all_books = []

    for p in range(1, pages + 1):
        print("Страница:", p)
        try:
            r = requests.get(base.format(p), timeout=10)
            r.raise_for_status()
        except Exception as e:
            print("Не удалось загрузить страницу:", e)
            continue

        soup = BeautifulSoup(r.text, "html.parser")
        links = []

        for a in soup.select("h3 a"):
            href = a.get("href").replace("../../", "")
            links.append("http://books.toscrape.com/catalogue/" + href)

        for link in links:
            data = get_book_data(link)
            if data:
                all_books.append(data)

        time.sleep(1)

    if is_save:
        with open("books_data.txt", "w", encoding="utf-8") as f:
            for b in all_books:
                f.write(str(b) + "\n")

    print("Всего книг собрано:", len(all_books))
    return all_books
