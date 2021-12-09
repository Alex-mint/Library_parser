import requests
import os
import json

from bs4 import BeautifulSoup
from urllib.parse import urljoin

from parser_tools import (parse_book_page, download_image,
                          download_txt, create_parser)


def save_book_attributes(book_attributes, json_path):
    os.makedirs(json_path, exist_ok=True)
    filename = os.path.join(json_path, 'description')
    with open(filename, 'w', encoding='utf-8') as json_file:
        json.dump(book_attributes, json_file, ensure_ascii=False, indent=2)


def get_book_urls(page_url, library_url):
    response = requests.get(page_url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'lxml')
    crude_book_urls = soup.select('.ow_px_td .d_book')
    book_urls = [urljoin(library_url, url.select_one('a')['href']) for url in
                 crude_book_urls]
    return book_urls


def download_book_attributes(library_url, book_urls, books_folder,
                             images_folder, skip_imgs, skip_txt):
    all_book_attributes = []
    for book_url in book_urls:
        try:
            book_id = book_url.split('/')[-2].replace('b', '')
            book_attributes = parse_book_page(book_url)
            if not skip_imgs:
                download_image(book_attributes['image_url'], library_url,
                               images_folder)
            if not skip_txt:
                download_txt(library_url, book_attributes['filename'], book_id,
                             books_folder)
        except requests.exceptions.HTTPError:
            continue
        all_book_attributes.append(book_attributes)
    return all_book_attributes


def main():
    library_url = 'https://tululu.org/'
    book_attributes = []

    books_parser = create_parser()
    args = books_parser.parse_args()
    books_folder = os.path.join(args.dest_folder, 'books')
    images_folder = os.path.join(args.dest_folder, 'images')
    skip_imgs = args.skip_imgs
    skip_txt = args.skip_txt

    json_path = os.path.join(args.json_path)
    if not args.json_path:
        json_path = os.path.join(args.dest_folder)

    for page in range(args.start_page, args.end_page):
        page_url = f'{library_url}l55/{page}/'
        if page == 1:
            page_url = f'{library_url}l55/'
        book_urls = get_book_urls(page_url, library_url)
        book_attributes += download_book_attributes(library_url, book_urls,
                                                    books_folder, images_folder,
                                                    skip_imgs, skip_txt)
    save_book_attributes(book_attributes, json_path)


if __name__ == '__main__':
    main()
