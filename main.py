import requests
import os


def check_for_redirect(response):
    if response.history:
        raise requests.exceptions.HTTPError


def download_books(path, books_quantity):
    for book_id in range(1, books_quantity+1):
        payload = {'id': book_id}
        url = 'https://tululu.org/txt.php'
        response = requests.get(url, params=payload)
        response.raise_for_status()
        try:
            check_for_redirect(response)
        except requests.exceptions.HTTPError:
            continue
        with open(f"{path}/id_{book_id}.tex", "wb") as file:
            file.write(response.content)
        book_id += 1


def main():
    books_quantity = 10
    path = 'books'
    os.makedirs(path, exist_ok=True)
    download_books(path, books_quantity)


if __name__ == '__main__':
    main()