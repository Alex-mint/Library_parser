# Парсер книг

Парсер скачивает с сайта [tululu.org](http://tululu.org/) книги научной фантастики с обложками, названиями и информацией.

### Как установить

- Python3 должен быть уже установлен.
- Установите зависимости:
```commandline
pip install -r requirements.txt
```

### Запуск

Для запуска программы необходимо написать в терминале следующее:
```commandline
python3 parse_tululu_category.py
```

Также у скрипта есть два необязательны аргумента:
- ```--start_page``` Начальная страница книг для загрузки default=1.
- ```--end_page``` Конечная страница книг для загрузки, по умолчанию все страницы категории.
- ```--dest_folder``` Путь к каталогу с результатами парсинга: картинкам, книгам, JSON, default='downloads'.
- ```--json_path``` Путь к *.json файлу с результатами, default='downloads'.
- ```--skip_imgs``` Не скачивать обложки книг, default=False.
- ```--skip_txt``` Не скачивать содержимое книг, default=False.
### Примеры ввода

```commandline
python3 parse_tululu_category.py --start_page 700 --end_page 701
python3 parse_tululu_category.py --start_page 700
python3 parse_tululu_category.py --start_page 1 --dest_folder folder_name
python3 parse_tululu_category.py --start_page 1 --skip_txt
python3 parse_tululu_category.py --start_page 1 --skip_imgs
python3 parse_tululu_category.py --start_page 1 --json_path folder_name
```
