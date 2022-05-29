import numpy as np
from geopy.distance import great_circle
from shapely.geometry import MultiPoint
import pandas as pd
from sklearn.cluster import DBSCAN

from segmented_regression.seg_reg import PWCSegRegMultiple


def cure_articles_df(articles_df_raw):
    articles_df_loc = articles_df_raw.drop(articles_df_raw[articles_df_raw.hasgeolocation != 'true'].index)
    articles_df_loc.drop('hasgeolocation', axis='columns', inplace=True)
    articles_df_loc['lat'] = articles_df_loc['lat'].apply(lambda x: float(x))
    articles_df_loc['lng'] = articles_df_loc['lng'].apply(lambda x: float(x))
    articles_df_loc_usd = articles_df_loc[articles_df_loc['precio'].str.contains('US')].copy()
    articles_df_loc_usd.loc[:, 'precio'] = articles_df_loc_usd.loc[:, 'precio'].apply(
        lambda x: int(x[4:].replace('.', '')))
    articles_df_loc_usd.loc[:, 'sup_c'] = articles_df_loc_usd.loc[:, 'sup_c'].apply(
        lambda x: (int(x) if x.isnumeric() else 0))
    articles_df_loc_usd.loc[:, 'sup_t'] = articles_df_loc_usd.loc[:, 'sup_t'].apply(lambda x: int(x))
    articles_df_loc_usd.insert(loc=articles_df_loc_usd.shape[1], column='precio_rel',
                               value=
                               articles_df_loc_usd.loc[:, 'precio'].values / articles_df_loc_usd.loc[:, 'sup_t'].values)
    # print(articles_df_raw.iloc[:, 1:-2])
    # print(articles_df_loc.iloc[:, 1:-2])
    # print(articles_df_loc_usd.iloc[:, 1:-2])
    return articles_df_loc_usd


def get_centermost_point(cluster):
    centroid = (MultiPoint(cluster).centroid.x, MultiPoint(cluster).centroid.y)
    centermost_point = min(cluster, key=lambda point: great_circle(point, centroid).m)
    return tuple(centermost_point)


def representative_points(df, cluster_labels, coords):
    num_clusters = len(set(cluster_labels))
    clusters = pd.Series([coords[cluster_labels == n] for n in range(num_clusters)])
    centermost_points = clusters.map(get_centermost_point)
    lats, lngs = zip(*centermost_points)
    rep_points = pd.DataFrame({'lng': lngs, 'lat': lats})
    return rep_points.apply(lambda row: df[(df['lat'] == row['lat']) & (df['lng'] == row['lng'])].iloc[0], axis=1)


def geographical_clusterization(df, cluster_radius_km):
    """
    Geographical clusterization of items.
    :param df:
    :return df:
    """
    kms_per_radian = 6371.0088
    coords = df.loc[:, ['lat', 'lng']].values
    db = DBSCAN(eps=cluster_radius_km / kms_per_radian, min_samples=1, algorithm='ball_tree', metric='haversine'). \
        fit(np.radians(coords))
    cluster_labels = db.labels_
    df.insert(loc=len(df.iloc[0, :]), column='cluster', value=cluster_labels)
    return df


def price_segmentation(df, cluster_segment_max_size):
    """
    Segmentation of geographical clusters by relative price
    :param cluster_segment_max_size:
    :param df:
    :return df, cluster_segment_dict:
    """
    cluster_labels = df.loc[:, 'cluster']
    n_clusters = len(set(cluster_labels))
    df.insert(loc=len(df.iloc[0, :]), column='segment', value=0)
    df.insert(loc=len(df.iloc[0, :]), column='cluster_segment', value=df.loc[0, 'cluster'])
    df.insert(loc=df.shape[1], column='cluster_segment_index', value=0)
    cluster_list = [df.loc[df.loc[:, 'cluster'] == i, :].copy() for i in range(n_clusters)]
    cluster_sizes = [len(cluster_) for cluster_ in cluster_list]
    for cluster, cluster_size in zip(cluster_list, cluster_sizes):
        if cluster_size > cluster_segment_max_size:
            xyz_cluster = np.hstack((np.array(cluster.loc[:, 'lat'].values).reshape((-1, 1)),
                                     np.array(cluster.loc[:, 'lng'].values).reshape((-1, 1)),
                                     (np.array(cluster.loc[:, 'precio'].values) / np.array(
                                         cluster.loc[:, 'sup_t'].values)).reshape(-1, 1)))
            pwcsrm = PWCSegRegMultiple(p_norm=2, max_items_per_class=cluster_segment_max_size)
            pwcsrm.fit(xy_train=xyz_cluster[:, [0, 1]], z_train=xyz_cluster[:, [2]])
            df.loc[cluster.index, 'segment'] = pwcsrm.classes
    df.loc[:, 'cluster_segment'] = \
        [str(cluster_) + '-' + str(segment_) for cluster_, segment_ in zip(df.loc[:, 'cluster'], df.loc[:, 'segment'])]
    cluster_segment_set = set(df.loc[:, 'cluster_segment'])
    cluster_segment_list = list(cluster_segment_set)
    cluster_segment_dict = dict(zip(cluster_segment_list, range(len(cluster_segment_list))))
    df.loc[:, 'cluster_segment_index'] = [cluster_segment_dict[cs] for cs in df.loc[:, 'cluster_segment']]
    return df, cluster_segment_dict
