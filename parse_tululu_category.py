import requests
import os
import json

from bs4 import BeautifulSoup
from urllib.parse import urljoin

from main import parse_book_page, download_image, download_txt


def save_book_attributes(book_attributes):

    with open('description', 'w', encoding='utf-8') as json_file:
        json.dump(book_attributes, json_file, ensure_ascii=False, indent=2)


def get_book_urls(page_url, library_url):
    response = requests.get(page_url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'lxml')
    crude_book_urls = soup.find('td', class_='ow_px_td').find_all('table',
                                                                   class_='d_book')
    book_urls = [urljoin(library_url, url.find('a')['href']) for url in crude_book_urls]
    return book_urls


def download_book_attributes(library_url, book_urls):
    all_book_attributes = []
    for book_url in book_urls:
        try:
            book_id = book_url.split('/')[-2].replace('b', '')
            book_attributes = parse_book_page(book_url)
            download_image(book_attributes['image_url'], library_url)
            download_txt(library_url, book_attributes['filename'], book_id)
        except requests.exceptions.HTTPError:
            continue
        all_book_attributes.append(book_attributes)
    return all_book_attributes


def main():
    library_url = 'https://tululu.org/'
    book_attributes = []
    for page in range(1, 3):
        page_url = f'{library_url}l55/{page}/'
        if page == 1:
            page_url = f'{library_url}l55/'
        book_urls = get_book_urls(page_url, library_url)
        book_attributes += download_book_attributes(library_url, book_urls)
    save_book_attributes(book_attributes)


if __name__ == '__main__':
    main()