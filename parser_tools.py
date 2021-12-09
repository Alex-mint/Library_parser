import requests
import os
import argparse

from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
from urllib.parse import urljoin
from urllib import parse


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

