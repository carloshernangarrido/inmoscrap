# This scrip scraps inmoclick.com
import numpy as np
from sklearn.preprocessing import MinMaxScaler

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
    db = DBSCAN(eps=radius_km / kms_per_radian, min_samples=1, algorithm='ball_tree', metric='haversine'). \
        fit(np.radians(coords))
    cluster_labels = db.labels_
    n_clusters = len(set(cluster_labels))
    df.insert(loc=len(df.iloc[0, :]), column='cluster', value=cluster_labels)
    # print(df.loc[:, ['precio', 'sup_t', 'lat', 'lng', 'luz', 'agua', 'gas', 'cluster']])
    # print(f'{n_clusters} clusters')
    rs = representative_points(df, cluster_labels, coords)
    cluster_labels_list = list(set(cluster_labels))
    # gmplot_df(df, cluster_labels_list=cluster_labels_list)

    ##  Segmentation of geographical clusters by relative price
    #     Find the larguest cluster
    cluster_list = [df.loc[df.loc[:, 'cluster'] == i, :].copy() for i in range(n_clusters)]
    cluster_sizes = [len(cluster_) for cluster_ in cluster_list]
    largest_cluster = cluster_list[np.argmax(cluster_sizes)]
    cluster = largest_cluster
    # cluster = cluster_list[0]
    xyz_cluster = np.hstack((np.array(cluster.loc[:, 'lat'].values).reshape((-1, 1)),
                             np.array(cluster.loc[:, 'lng'].values).reshape((-1, 1)),
                             (np.array(cluster.loc[:, 'precio'].values) / np.array(
                                 cluster.loc[:, 'sup_t'].values)).reshape(-1, 1)))


    def piece_wise_constant(xy_, m, x_0, y_0, v_below, v_above):
        x_ = xy_[0]
        y_ = xy_[1]
        if y_ - y_0 < m * (x_ - x_0):
            return v_below
        else:
            return v_above


    def obj_fun(x, xyz_cluster_, p_norm):
        z_trial = \
            np.apply_along_axis(
                lambda _: piece_wise_constant(_, m=x[0], x_0=x[1], y_0=x[2], v_below=x[3], v_above=x[4]),
                axis=1, arr=xyz_cluster_[:, 0:2])
        return np.linalg.norm(z_trial.reshape((-1, 1)) - xyz_cluster_[:, 2].reshape((-1, 1)), p_norm)


    scaler = MinMaxScaler()
    scaler.fit(xyz_cluster)
    xyz_cluster_norm = scaler.transform(xyz_cluster)
    res = minimize(obj_fun, x0=np.array([0, 0.5, 0.5, 0.5, 0.5]), method='Powell',
                   args=(xyz_cluster_norm, 2), bounds=[(-1e6, 1e6), (0, 1), (0, 1), (0, 1), (0, 1)])
    # back to original scale
    res_x_os = res.x.copy()
    res_x_os[[1, 2, 3]] = scaler.inverse_transform(np.array([res.x[1], res.x[2], res.x[3]]).reshape(1, -1))
    res_x_os[[1, 2, 4]] = scaler.inverse_transform(np.array([res.x[1], res.x[2], res.x[4]]).reshape(1, -1))
    pto_ini = np.array([res.x[1], res.x[2], 0]).reshape(1, -1)
    pto_fin = np.array([res.x[1], res.x[2], 0]).reshape(1, -1) + np.array([1, res.x[0], 0]).reshape(1, -1)
    pto_ini_os = scaler.inverse_transform(pto_ini)
    pto_fin_os = scaler.inverse_transform(pto_fin)
    res_x_os[0] = (pto_fin_os[0, 1] - pto_ini_os[0, 1]) / (pto_fin_os[0, 0] - pto_ini_os[0, 0])
    pass
    fig, ax = plt.subplots(1, 2)
    ax[0].scatter(xyz_cluster_norm[:, 0], xyz_cluster_norm[:, 1], 100 * xyz_cluster_norm[:, 2])
    x_plot = np.linspace(-1, 1, 100)
    ax[0].plot(x_plot, res.x[0] * (x_plot - res.x[1]) + res.x[2])
    ax[1].scatter(xyz_cluster[:, 0], xyz_cluster[:, 1], 100 * (res.x[4]/res_x_os[4]) * xyz_cluster[:, 2])
    x_plot = np.linspace(-100, 100, 100)
    ax[1].plot(x_plot, res_x_os[0] * (x_plot - res_x_os[1]) + res_x_os[2])
    plt.show()
    #
    pass
#
