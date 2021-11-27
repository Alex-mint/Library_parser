import requests
import os

def download_books(path):
    url = 'https://tululu.org/txt.php?id=32168'
    links = [url for num in range(10)]

    for link_number, link in enumerate(links, 1):
        response = requests.get(link)
        response.raise_for_status()
        with open(f"{path}/id_{link_number}.tex", "wb") as file:
            file.write(response.content)


def main():
    path = 'books'
    os.makedirs(path, exist_ok=True)
    download_books(path)


if __name__ == '__main__':
    main()