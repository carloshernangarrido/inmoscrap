# This scrip scraps inmoclick.com
import numpy as np
from data_cure import representative_points
from gmplots import gmplot_df
from scraper import scrap_now, soup_to_df
# import pandas as pd
import matplotlib.pyplot as plt
from sklearn.cluster import DBSCAN
import webbrowser
from segmented_regression.seg_reg import PWSegReg


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
    del soup
    df = df[1:500, :]
    kms_per_radian = 6371.0088
    radius_km = 0.5
    coords = df.loc[:, ['lat', 'lng']].values
    # print(coords)
    db = DBSCAN(eps=radius_km / kms_per_radian, min_samples=1, algorithm='ball_tree', metric='haversine'). \
        fit(np.radians(coords))
    cluster_labels = db.labels_
    n_clusters = len(set(cluster_labels))
    df.insert(loc=len(df.iloc[0, :]), column='cluster', value=cluster_labels)
    # print(df.loc[:, ['precio', 'sup_t', 'lat', 'lng', 'luz', 'agua', 'gas', 'cluster']])
    # print(f'{n_clusters} clusters')
    # rs = representative_points(df, cluster_labels, coords)
    # Segmentation of geographical clusters by relative price
    df.insert(loc=len(df.iloc[0, :]), column='segment', value=0)
    cluster_list = [df.loc[df.loc[:, 'cluster'] == i, :].copy() for i in range(n_clusters)]
    cluster_sizes = [len(cluster_) for cluster_ in cluster_list]
    max_cluster_size = 20
    for cluster, cluster_size in zip(cluster_list, cluster_sizes):
        if cluster_size > max_cluster_size:
            xyz_cluster = np.hstack((np.array(cluster.loc[:, 'lat'].values).reshape((-1, 1)),
                                     np.array(cluster.loc[:, 'lng'].values).reshape((-1, 1)),
                                     (np.array(cluster.loc[:, 'precio'].values) / np.array(
                                         cluster.loc[:, 'sup_t'].values)).reshape(-1, 1)))
            pwsr = PWSegReg(p_norm=2)
            pwsr.fit(xy_train=xyz_cluster[:, [0, 1]], z_train=xyz_cluster[:, [2]])
            df.loc[cluster.index, 'segment'] = pwsr.classify(xyz_cluster[:, [0, 1]])
    gmplot_df(df)
    print(df)

    # largest_cluster = cluster_list[np.argmax(cluster_sizes)]
    # cluster = largest_cluster
    # # cluster = cluster_list[0]
    # xyz_cluster = np.hstack((np.array(cluster.loc[:, 'lat'].values).reshape((-1, 1)),
    #                          np.array(cluster.loc[:, 'lng'].values).reshape((-1, 1)),
    #                          (np.array(cluster.loc[:, 'precio'].values) / np.array(
    #                              cluster.loc[:, 'sup_t'].values)).reshape(-1, 1)))
    # pwsr = PWSegReg(p_norm=2)
    # pwsr.fit(xy_train=xyz_cluster[:, [0, 1]], z_train=xyz_cluster[:, [2]])
    # pass
    # fig, ax = plt.subplots(1, 1)
    # if type(ax) is not list:
    #     ax = [ax]
    # ax[0].scatter(xyz_cluster[:, 0], xyz_cluster[:, 1], xyz_cluster[:, 2], marker='o')
    # x_plot = np.linspace(-100, 100, 100)
    # ax[0].plot(x_plot, pwsr.m * (x_plot - pwsr.x_0) + pwsr.y_0)
    # ax[0].scatter(xyz_cluster[:, 0], xyz_cluster[:, 1], pwsr.predict(xyz_cluster[:, [0, 1]]), marker='x')
    # ax[0].set_xlim((min(xyz_cluster[:, 0]), max(xyz_cluster[:, 0])))
    # ax[0].set_ylim((min(xyz_cluster[:, 1]), max(xyz_cluster[:, 1])))
    # plt.show()
    #
#
