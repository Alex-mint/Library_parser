import requests
import os

from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
from urllib.parse import urljoin
from urllib import parse


def check_for_redirect(response):
    if response.history:
        raise requests.exceptions.HTTPError


def download_txt(url, filename, book_id, folder='books/'):
    filename = sanitize_filename(filename)
    response = requests.get(url)
    response.raise_for_status()
    with open(f"{folder}/{book_id}. {filename}.tex", "wb") as file:
        file.write(response.content)


def download_image(url=12, filename=12, book_id=12, folder='images/'):
    unquoted_url = parse.unquote(url)
    path = parse.urlparse(unquoted_url).path
    extension = os.path.splitext(path)[-1]
    response = requests.get(url)
    response.raise_for_status()
    with open(f"{folder}/{book_id}. {filename}.{extension}", "wb") as file:
        file.write(response.content)


def parse_book_page(library_url, book_id):
    url = f'{library_url}b{book_id}/'
    comments = []
    genres = []
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'lxml')
    title, author = soup.find('h1').text.split('::')
    chopped_image_url = soup.find('div', class_='bookimage').find('img')['src']
    image_url = urljoin(library_url, chopped_image_url)
    crude_comments = soup.find_all('div', class_='texts')
    for comment in crude_comments:
        comments.append(comment.find('span', class_='black').text)
    crude_genres = soup.find('span', class_='d_book').find_all('a')
    for genre in crude_genres:
        genres.append(genre.text)
    print(comments)
    print(genres)
    return title.strip(), image_url


def main():
    books_quantity = 10
    txt_path = 'books'
    images_path = 'images'
    library_url = 'https://tululu.org/'
    os.makedirs(txt_path, exist_ok=True)
    os.makedirs(images_path, exist_ok=True)
    for book_id in range(1, books_quantity+1):
        payload = {'id': book_id}
        response = requests.get(f'{library_url}txt.php', params=payload)
        response.raise_for_status()
        txt_url = response.url
        try:
            check_for_redirect(response)
        except requests.exceptions.HTTPError:
            continue
        filename, image_url = parse_book_page(library_url, book_id)
        download_txt(txt_url, filename, book_id)
        download_image(image_url, filename, book_id)
        book_id += 1


if __name__ == '__main__':
    main()