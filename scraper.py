import pickle
import sys

import requests
from bs4 import BeautifulSoup


def scrap_now(url: str, file_name: str = '', scrap_web: bool = True):
    """Scraps the given url and looks for 'lotes en venta'
    :argument url:
    :param file_name: Optional. If specified, it works with a local file copy of the html file.
    :param scrap_web: Flag to indicate is actual WEB sccraping is required o just open local file
    :returns soup:
    """
    if scrap_web:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/39.0.2171.95 Safari/537.36'}
        page = requests.get(url, headers=headers)
        soup = BeautifulSoup(page.text, "html.parser")
        try:
            with open(file_name, 'w', encoding='utf-8') as f:
                f.write(page.text)
        except EnvironmentError:
            print(f'File {file_name} not found.')
        return soup
    else:
        try:
            # Read the soup object from a file
            with open(file_name, "r", encoding='utf-8') as f:
                soup = BeautifulSoup(f.read(), "html.parser")
                return soup
        except EnvironmentError:
            print(f'File {file_name} not found and scrap_web = False.')
