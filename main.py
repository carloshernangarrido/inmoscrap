# This scrip scraps inmoclick.com
import numpy as np
from data_cure import cure_articles_df, representative_points
from scraper import scrap_now
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.cluster import DBSCAN
import matplotlib
import gmplot
import webbrowser


if __name__ == '__main__':
    scrap_web = False
    limit = 3000
    sup_total_min = 50
    sup_total_max = 10000
    precio_min = 1000
    precio_max = 1000000

    url = f"https://www.inmoclick.com.ar/inmuebles/venta-en-lotes-y-terrenos-en-mendoza?favoritos=0&limit={limit}" \
          f"&prevEstadoMap"f"=&amp;lastZoom=13&precio%5Bmin%5D={precio_min}&precio%5Bmax%5D=" \
          f"{precio_max}&moneda=2&sup_cubierta%5Bmin%5D=&sup_cubierta%5Bmax%5D" \
          f"=&sup_total%5Bmin%5D={sup_total_min}&sup_total%5Bmax%5D=" \
          f"{sup_total_max}&precio_pesos_m2%5Bmin%5D=&precio_pesos_m2%5Bmax%5D=&precio_dolares_m2%5Bmin%5D=" \
          f"&precio_dolares_m2%5Bmax%5D=&expensas%5Bmin%5D=&expensas%5Bmax%5D= "
    soup = scrap_now(url, file_name='lotes.html', scrap_web=scrap_web)
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
    df = cure_articles_df(articles_df_raw)

    kms_per_radian = 6371.0088
    radius_km = 0.5
    coords = df.loc[:, ['lat', 'lng']].values
    # print(coords)
    db = DBSCAN(eps=radius_km / kms_per_radian, min_samples=1, algorithm='ball_tree', metric='haversine').\
        fit(np.radians(coords))
    cluster_labels = db.labels_
    n_clusters = len(set(cluster_labels))
    df.insert(loc=len(df.iloc[0, :]), column='cluster', value=cluster_labels)
    print(df.loc[:, ['precio', 'sup_t', 'lat', 'lng', 'luz', 'agua', 'gas', 'cluster']])
    print(f'{n_clusters} clusters')
    # print(cluster_labels)
    rs = representative_points(df, cluster_labels, coords)
    # print(rs)

    # fig, ax = plt.subplots(figsize=[10, 6])
    # rs_scatter = ax.scatter(rs['lng'], rs['lat'], c='#99cc99', edgecolor='None', alpha=0.7, s=120)
    # df_scatter = ax.scatter(df['lng'], df['lat'], c='k', alpha=0.9, s=3)
    # ax.set_title('Full data set vs DBSCAN reduced set')
    # ax.set_xlabel('Longitude')
    # ax.set_ylabel('Latitude')
    # ax.legend([df_scatter, rs_scatter], ['Full set', 'Reduced set'], loc='upper right')
    # plt.show()
    #
    # fig = plt.figure()
    # color_map = cm.get_cmap('hsv', n_clusters)
    # color_map_list = [color_map(1.*i/n_clusters) for i in range(n_clusters)]
    # for i in range(n_clusters):
    #     plt.plot(df['lat'][cluster_labels == i], df['lng'][cluster_labels == i], linestyle='', marker='o',
    #              color=color_map_list[i])
    # plt.show()

    gmap = gmplot.GoogleMapPlotter(df.loc[0, 'lat'], df.loc[0, 'lng'], 13)
    color_map = matplotlib.cm.get_cmap('hsv', n_clusters)
    color_map_list = [matplotlib.colors.rgb2hex(color_map(1.*i/n_clusters)) for i in range(n_clusters)]
    # color_map_list = list(matplotlib.colors.BASE_COLORS.keys())
    for i in range(n_clusters):
        # i_color = i - 8*(i // 8)
        gmap.scatter(
            lats=df.loc[df.loc[:, 'cluster'] == i, 'lat'].to_list(),
            lngs=df.loc[df.loc[:, 'cluster'] == i, 'lng'].to_list(),
            color=color_map_list[i],
            # s=[np.sqrt(sup_t) for sup_t in df.loc[df.loc[:, 'cluster'] == i, 'sup_t'].to_list()],
            s=[precio_rel for precio_rel in (0.1*np.array(df.loc[df.loc[:, 'cluster'] == i, 'precio'].to_list())
               /
               np.array(df.loc[df.loc[:, 'cluster'] == i, 'sup_t'].to_list())).tolist()],
            ew=2,
            marker=False,
            symbol=['o' if gas else 'x' for gas in df.loc[df.loc[:, 'cluster'] == i, 'gas']],
            title='hola', # df.loc[df.loc[:, 'cluster'] == i, 'href'].to_list(),
            label=df.loc[df.loc[:, 'cluster'] == i, 'cluster'].to_list()
        )
    gmap.draw("map.html")
    chrome_path = 'C:/Program Files (x86)/Google/Chrome/Application/chrome.exe %s'
    webbrowser.get(chrome_path).open("file://G:/TRABAJO/Profesional/Python/inmoscrap/map.html")
    print(df.loc[df.loc[:, 'cluster'] == 26, 'precio'].to_list())
