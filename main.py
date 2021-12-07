import requests
import os
import argparse

from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
from urllib.parse import urljoin
from urllib import parse


def create_parser():
    books_parser = argparse.ArgumentParser(description='Параметры запуска скрипта')
    books_parser.add_argument('--start_id', default=1, type=int)
    books_parser.add_argument('--end_id', default=766, type=int)
    return books_parser


def check_for_redirect(response):
    if response.history:
        raise requests.exceptions.HTTPError


def download_txt(library_url, filename, book_id, txt_folder='books/'):
    os.makedirs(txt_folder, exist_ok=True)
    payload = {'id': book_id}
    response = requests.get(f'{library_url}txt.php', params=payload)
    check_for_redirect(response)
    response.raise_for_status()
    filename = sanitize_filename(filename)
    with open(f"{txt_folder}/{filename}.txt", "w",
              encoding='utf8') as file:
        file.write(response.text)


def download_image(chopped_image_url, library_url, images_folder='images/'):
    os.makedirs(images_folder, exist_ok=True)
    if chopped_image_url == 'nopic.gif':
        image_url = f'{library_url}/images/{chopped_image_url}'
    else:
        image_url = f'{library_url}/shots/{chopped_image_url}'
    response = requests.get(image_url)
    check_for_redirect(response)
    response.raise_for_status()
    with open(f"{images_folder}/{chopped_image_url}", "wb") as file:
        file.write(response.content)


def parse_book_page(book_url):
    response = requests.get(book_url)
    check_for_redirect(response)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'lxml')
    title, author = soup.find('h1').text.split('::')
    chopped_image_url = soup.find('div', class_='bookimage').find('img')['src']
    crude_comments = soup.find_all('div', class_='texts')
    comments = [comment.find('span', class_='black').text for comment in
                crude_comments]
    crude_genres = soup.find('span', class_='d_book').find_all('a')
    genres = [genre.text for genre in crude_genres]
    book_attributes = {
        'filename': title.strip(),
        'image_url': chopped_image_url.split('/')[-1],
        'comments': comments,
        'genres': genres
    }
    return book_attributes


def main():
    books_parser = create_parser()
    args = books_parser.parse_args()
    library_url = 'https://tululu.org/'

    for book_id in range(args.start_id, args.end_id + 1):
        book_url = f'{library_url}b{book_id}/'
        try:
            book_attributes = parse_book_page(book_url)
            download_txt(library_url, book_attributes['filename'], book_id)
            download_image(book_attributes['image_url'], library_url)
        except requests.exceptions.HTTPError:
            continue


if __name__ == '__main__':
    main()
