import requests
import os
import json
import argparse

from urllib.parse import urljoin
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename


def save_book_attributes(book_attributes, json_path):
    os.makedirs(json_path, exist_ok=True)
    filename = os.path.join(json_path, 'description.json')
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


def get_last_page():
    url = 'https://tululu.org/l55/'
    response = requests.get(url)
    check_for_redirect(response)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'lxml')
    last_page = int(soup.select_one('.npage:last-child').text)
    return last_page


def create_parser():
    books_parser = argparse.ArgumentParser(description='Параметры запуска скрипта')
    books_parser.add_argument('--start_page', default=1, type=int)
    books_parser.add_argument('--end_page', default=get_last_page(), type=int)
    books_parser.add_argument('--dest_folder', default='downloads', type=str)
    books_parser.add_argument('--json_path', default='', type=str)
    books_parser.add_argument('--skip_imgs', action='store_true')
    books_parser.add_argument('--skip_txt', action='store_true')
    return books_parser


def check_for_redirect(response):
    if response.history:
        raise requests.exceptions.HTTPError


def download_txt(library_url, filename, book_id, books_folder):
    os.makedirs(books_folder, exist_ok=True)
    payload = {'id': book_id}
    response = requests.get(f'{library_url}txt.php', params=payload)
    check_for_redirect(response)
    response.raise_for_status()
    filename = os.path.join(books_folder, sanitize_filename(filename))
    with open(f'{filename}.txt', 'w', encoding='utf8') as file:
        file.write(response.text)


def download_image(chopped_image_url, library_url, images_folder):
    os.makedirs(images_folder, exist_ok=True)
    if chopped_image_url == 'nopic.gif':
        image_url = f'{library_url}/images/{chopped_image_url}'
    else:
        image_url = f'{library_url}/shots/{chopped_image_url}'
    response = requests.get(image_url)
    check_for_redirect(response)
    response.raise_for_status()
    filename = os.path.join(images_folder, chopped_image_url)
    with open(filename, "wb") as file:
        file.write(response.content)


def parse_book_page(book_url):
    response = requests.get(book_url)
    check_for_redirect(response)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'lxml')
    title, author = soup.select_one('h1').text.split('::')
    chopped_image_url = soup.select_one('.bookimage img')['src']
    crude_comments = soup.select('.texts .black')
    comments = [comment.text for comment in crude_comments]
    crude_genres = soup.select('span.d_book a')
    genres = [genre.text for genre in crude_genres]
    book_attributes = {
        'filename': title.strip(),
        'image_url': chopped_image_url.split('/')[-1],
        'comments': comments,
        'genres': genres
    }
    return book_attributes


def main():
    library_url = 'https://tululu.org/'
    all_book_attributes = []

    books_parser = create_parser()
    args = books_parser.parse_args()
    books_folder = os.path.join(args.dest_folder, 'books')
    images_folder = os.path.join(args.dest_folder, 'images')
    skip_imgs = args.skip_imgs
    skip_txt = args.skip_txt

    json_path = args.json_path
    if not args.json_path:
        json_path = args.dest_folder

    for page in range(args.start_page, args.end_page):
        page_url = f'{library_url}l55/{page}/'
        if page == 1:
            page_url = 'https://tululu.org/l55/1/'
        book_urls = get_book_urls(page_url, library_url)
        all_book_attributes = []
        for book_url in book_urls:
            try:
                book_id = book_url.split('/')[-2].replace('b', '')
                book_attributes = parse_book_page(book_url)
                if not skip_imgs:
                    download_image(book_attributes['image_url'], library_url,
                                   images_folder)
                if not skip_txt:
                    download_txt(library_url, book_attributes['filename'],
                                 book_id,
                                 books_folder)
            except requests.exceptions.HTTPError:
                continue
            all_book_attributes.append(book_attributes)
    save_book_attributes(all_book_attributes, json_path)


if __name__ == '__main__':
    main()
