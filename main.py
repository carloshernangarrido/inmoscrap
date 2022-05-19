# This scrip scraps inmoclick.com
import numpy as np
from data_cure import cure_articles_df, representative_points
from gmplots import gmplot_df
from scraper import scrap_now, soup_to_df
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.cluster import DBSCAN
import matplotlib
import gmplot
import webbrowser
from scipy.optimize import minimize


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
    df = soup_to_df(soup)

    kms_per_radian = 6371.0088
    radius_km = 0.5
    coords = df.loc[:, ['lat', 'lng']].values
    # print(coords)
    db = DBSCAN(eps=radius_km / kms_per_radian, min_samples=1, algorithm='ball_tree', metric='haversine').\
        fit(np.radians(coords))
    cluster_labels = db.labels_
    n_clusters = len(set(cluster_labels))
    df.insert(loc=len(df.iloc[0, :]), column='cluster', value=cluster_labels)
    # print(df.loc[:, ['precio', 'sup_t', 'lat', 'lng', 'luz', 'agua', 'gas', 'cluster']])
    # print(f'{n_clusters} clusters')
    # print(cluster_labels)
    rs = representative_points(df, cluster_labels, coords)
    # print(rs)
    cluster_labels_list = list(set(cluster_labels))
    gmplot_df(df, cluster_labels_list=cluster_labels_list)
    # print(df.loc[df.loc[:, 'cluster'] == 26, 'precio'].to_list())

#  Segmentation of geographical clusters by relative price
#     Find the larguest cluster
    cluster_list = [df.loc[df.loc[:, 'cluster'] == i, :].copy() for i in range(n_clusters)]
    cluster_sizes = [len(cluster_) for cluster_ in cluster_list]
    largest_cluster = cluster_list[np.argmax(cluster_sizes)]
    cluster = largest_cluster
    #
    # xy_cluster = np.hstack((np.array(cluster.loc[:, 'lat'].values).reshape((-1, 1)),
    #                         np.array(cluster.loc[:, 'lng'].values).reshape((-1, 1))))
    # z_cluster = (np.array(cluster.loc[:, 'precio'].values) / np.array(cluster.loc[:, 'sup_t'].values)).reshape((-1, 1))
    #
    # def piece_wise_constant(x_, y_, m, y_0, v_below, v_above):
    #     if y_ < m*x_ + y_0:
    #         return v_below
    #     else:
    #         return v_above
    #
    # def obj_fun(x, xy_cluster, z_cluster):
    #     for xy_, z_ in zip(xy_cluster, z_cluster)
    #     piece_wise_constant(x_, y_, m=x[0], y_0=x[1], v_below=x[2], v_above=[3])
    #     np.apply_along_axis()


    # res = minimize(fun, x0, method='SLSQP', args=(c, m_, 2), bounds=bounds)
    #
    # pass
#
