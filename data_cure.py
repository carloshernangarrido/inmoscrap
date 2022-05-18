from geopy.distance import great_circle
from shapely.geometry import MultiPoint
import pandas as pd


def cure_articles_df(articles_df_raw):
    articles_df_loc = articles_df_raw.drop(articles_df_raw[articles_df_raw.hasgeolocation != 'true'].index)
    articles_df_loc.drop('hasgeolocation', axis='columns', inplace=True)
    articles_df_loc['lat'] = articles_df_loc['lat'].apply(lambda x: float(x))
    articles_df_loc['lng'] = articles_df_loc['lng'].apply(lambda x: float(x))
    articles_df_loc_usd = articles_df_loc[articles_df_loc['precio'].str.contains('US')].copy()
    articles_df_loc_usd.loc[:, 'precio'] = articles_df_loc_usd.loc[:, 'precio'].apply(lambda x: int(x[4:].replace('.', '')))
    articles_df_loc_usd.loc[:, 'sup_c'] = articles_df_loc_usd.loc[:, 'sup_c'].apply(lambda x: (int(x) if x.isnumeric() else 0))
    articles_df_loc_usd.loc[:, 'sup_t'] = articles_df_loc_usd.loc[:, 'sup_t'].apply(lambda x: int(x))
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
