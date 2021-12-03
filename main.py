import requests
import os
import sys
import argparse

from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
from urllib.parse import urljoin
from urllib import parse


def create_parser():
    books_parser = argparse.ArgumentParser(description='Параметры запуска скрипта')
    books_parser.add_argument('--start_page', default=1, type=int)
    books_parser.add_argument('--end_page', default=766, type=int)
    return books_parser


def check_for_redirect(response):
    if response.history:
        raise requests.exceptions.HTTPError


def download_txt(response, filename, book_id, folder='books/'):
    filename = sanitize_filename(filename)
    with open(f"{folder}/{book_id}. {filename}.txt", "w",
              encoding='utf8') as file:
        file.write(response.text)


def download_image(url, filename, book_id, folder='images/'):
    unquoted_url = parse.unquote(url)
    path = parse.urlparse(unquoted_url).path
    extension = os.path.splitext(path)[-1]
    response = requests.get(url)
    check_for_redirect(response)
    response.raise_for_status()
    with open(f"{folder}/{book_id}. {filename}.{extension}", "wb") as file:
        file.write(response.content)


def parse_book_page(library_url, book_id):
    url = f'{library_url}b{book_id}/'
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'lxml')
    title, author = soup.find('h1').text.split('::')
    chopped_image_url = soup.find('div', class_='bookimage').find('img')['src']
    image_url = urljoin(library_url, chopped_image_url)
    crude_comments = soup.find_all('div', class_='texts')
    comments = [comment.find('span', class_='black').text for comment in
                crude_comments]
    crude_genres = soup.find('span', class_='d_book').find_all('a')
    genres = [genre.text for genre in crude_genres]
    book_attributes = {
        'filename': title.strip(),
        'image_url': image_url,
        'comments': comments,
        'genres': genres
    }
    return book_attributes


def main():
    books_parser = create_parser()
    args = books_parser.parse_args()
    txt_folder = 'books'
    images_folder = 'images'
    library_url = 'https://tululu.org/'

    os.makedirs(txt_folder, exist_ok=True)
    os.makedirs(images_folder, exist_ok=True)

    for book_id in range(args.start_page, args.end_page + 1):
        payload = {'id': book_id}
        response = requests.get(f'{library_url}txt.php', params=payload)
        response.raise_for_status()
        try:
            check_for_redirect(response)
            book_attributes = parse_book_page(
                library_url, book_id)
            download_txt(response, book_attributes['filename'], book_id)
            download_image(book_attributes['image_url'],
                           book_attributes['filename'], book_id)
        except requests.exceptions.HTTPError:
            continue


if __name__ == '__main__':
    main()
