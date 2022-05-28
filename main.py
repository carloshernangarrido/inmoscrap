# This scrip scraps inmoclick.com
from data_cure import geographical_clusterization, price_segmentation
from gmplots import gmplot_df
from scraper import scrap_now, soup_to_df
from stat_analysis import stats_from_items
import pandas as pd
import numpy as np


if __name__ == '__main__':
    scrap_web_flag = True
    limit = 3000
    sup_total_min = 50
    sup_total_max = 10000
    precio_min = 1000
    precio_max = 1000000
    cluster_radius_km = 0.5
    cluster_segment_max_size = 20
    cluster_segment_min_size = 10
    number_of_oportunities = 5
    file_name = 'lotes.html'
    url = f"https://www.inmoclick.com.ar/inmuebles/venta-en-lotes-y-terrenos-en-mendoza?favoritos=0&limit={limit}" \
          f"&prevEstadoMap"f"=&amp;lastZoom=13&precio%5Bmin%5D={precio_min}&precio%5Bmax%5D=" \
          f"{precio_max}&moneda=2&sup_cubierta%5Bmin%5D=&sup_cubierta%5Bmax%5D" \
          f"=&sup_total%5Bmin%5D={sup_total_min}&sup_total%5Bmax%5D=" \
          f"{sup_total_max}&precio_pesos_m2%5Bmin%5D=&precio_pesos_m2%5Bmax%5D=&precio_dolares_m2%5Bmin%5D=" \
          f"&precio_dolares_m2%5Bmax%5D=&expensas%5Bmin%5D=&expensas%5Bmax%5D= "
    items_df = soup_to_df(scrap_now(url, file_name=file_name, scrap_web=scrap_web_flag))
    items_df = geographical_clusterization(items_df, cluster_radius_km)
    items_df, cluster_segment_dict = price_segmentation(items_df, cluster_segment_max_size)
    # gmplot_df(items_df, plt_flag=False)
    # gmplot_df(items_df, as_per='cluster', plt_flag=False)
    stats_list = stats_from_items(items_df, sup_t_tol=0.25)
    stats_df = pd.DataFrame(np.array([[i for i in range(len(stats_list))],
                                      [stats.min_price for stats in stats_list],
                                      [stats.median_price for stats in stats_list],
                                      [stats.cluster_segment_df_res.shape[0] for stats in stats_list]]).T,
                            columns=['cluster_segment_index', 'min_price', 'median_price', 'count'])
    stats_df.insert(loc=stats_df.shape[1], column='rentability', value=stats_df.median_price - stats_df.min_price)
    stats_df = stats_df.sort_values(by='rentability', ascending=False)
    stats_drop_min_df = stats_df.drop(stats_df.loc[stats_df.loc[:, 'count'] < cluster_segment_min_size, :].index)
    stats_drop_min_df = stats_drop_min_df.sort_values(by='rentability', ascending=False)
    # Visualization
    print(stats_drop_min_df)
    bests_cluster_segment_index = \
        [int(i) for i in stats_drop_min_df.iloc[0:number_of_oportunities, :]['cluster_segment_index'].values]
    print('*** Oportunities ***')
    for oportunity_index in bests_cluster_segment_index:
        print(f'\ncluster_segment_index = {oportunity_index}')
        oportunity = stats_list[oportunity_index].cluster_segment_df_res
        print(oportunity)
        gmplot_df(oportunity, plt_flag=False)


