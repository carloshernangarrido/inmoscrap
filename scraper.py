import pandas as pd
import requests
from bs4 import BeautifulSoup
from data_cure import cure_articles_df


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


def soup_to_df(soup):
    articles = soup.find_all(name='article')
    # print(articles[0])
    articles_df_raw = pd.DataFrame(columns=['name', 'usr_id', 'prp_id', 'precio', 'sup_t',
                                            'hasgeolocation', 'lat', 'lng', 'sup_c', 'href', 'luz', 'agua', 'gas'],
                                   index=list(range(len(articles))))
    for i, article in enumerate(articles):
        articles_df_raw.iloc[i]['name'] = article.find('a').get('name')
        articles_df_raw.iloc[i]['usr_id'] = article.get('usr_id')
        articles_df_raw.iloc[i]['prp_id'] = article.get('prp_id')
        articles_df_raw.iloc[i]['precio'] = article.get('precio')
        articles_df_raw.iloc[i]['sup_t'] = article.get('sup_t')
        articles_df_raw.iloc[i]['sup_c'] = article.get('sup_c')
        articles_df_raw.iloc[i]['hasgeolocation'] = article.get('hasgeolocation')
        articles_df_raw.iloc[i]['lng'] = article.get('lng')
        articles_df_raw.iloc[i]['lat'] = article.get('lat')
        for a in article.find_all('a'):
            if a.get('href') is not None:
                articles_df_raw.iloc[i]['href'] = a.get('href')
        if article.find("div", {"class": "icon-luz disable"}):
            articles_df_raw.iloc[i]['luz'] = False
        elif article.find("div", {"class": "icon-luz"}):
            articles_df_raw.iloc[i]['luz'] = True
        else:
            print(f'luz error***{article.find_all("div", {"class": "property-tags"})}')
        if article.find("div", {"class": "icon-agua disable"}):
            articles_df_raw.iloc[i]['agua'] = False
        elif article.find("div", {"class": "icon-agua"}):
            articles_df_raw.iloc[i]['agua'] = True
        else:
            print(f'agua error***{article.find_all("div", {"class": "property-tags"})}')
        if article.find("div", {"class": "icon-gas disable"}):
            articles_df_raw.iloc[i]['gas'] = False
        elif article.find("div", {"class": "icon-gas"}):
            articles_df_raw.iloc[i]['gas'] = True
        else:
            print(f'gas error***{article.find_all("div", {"class": "property-tags"})}')
    pd.set_option('display.max_columns', None)
    return cure_articles_df(articles_df_raw)
