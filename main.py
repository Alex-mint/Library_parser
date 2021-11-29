import requests
import os
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename


def check_for_redirect(response):
    if response.history:
        raise requests.exceptions.HTTPError


def download_txt(url, filename, folder='books/'):
    filename = sanitize_filename(filename)
    response = requests.get(url)
    response.raise_for_status()
    with open(f"{folder}/{filename}.tex", "wb") as file:
        file.write(response.content)


def get_book_title(library_url, book_id):
    url = f'{library_url}b{book_id}/'
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'lxml')
    title, author = soup.find('h1').text.split('::')
    return title.strip()


def main():
    books_quantity = 10
    path = 'books'
    library_url = 'https://tululu.org/'
    os.makedirs(path, exist_ok=True)
    for book_id in range(1, books_quantity+1):
        payload = {'id': book_id}
        response = requests.get(f'{library_url}txt.php', params=payload)
        response.raise_for_status()
        txt_url = response.url
        try:
            check_for_redirect(response)
        except requests.exceptions.HTTPError:
            continue
        filename = get_book_title(library_url, book_id)
        download_txt(txt_url, filename)
        book_id += 1


if __name__ == '__main__':
    main()