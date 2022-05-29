# This scrip scraps inmoclick.com
from data_cure import geographical_clusterization, price_segmentation
from gmplots import gmplot_df
from scraper import scrap_now, soup_to_df
from stat_analysis import stats_from_items, summary_from_stats_list
import pandas as pd
import numpy as np
import pickle


if __name__ == '__main__':
    scrap_web_flag = True
    analize_flag = True
    limit = 3000
    sup_total_min = 50
    sup_total_max = 10000
    precio_min = 1000
    precio_max = 1000000
    cluster_radius_km = 0.5
    sup_t_tol = 1.0
    cluster_segment_max_size = 20
    cluster_segment_min_size = 10
    number_of_oportunities = 50
    file_name_html = 'lotes.html'
    url = f"https://www.inmoclick.com.ar/inmuebles/venta-en-lotes-y-terrenos-en-mendoza?favoritos=0&limit={limit}" \
          f"&prevEstadoMap"f"=&amp;lastZoom=13&precio%5Bmin%5D={precio_min}&precio%5Bmax%5D=" \
          f"{precio_max}&moneda=2&sup_cubierta%5Bmin%5D=&sup_cubierta%5Bmax%5D" \
          f"=&sup_total%5Bmin%5D={sup_total_min}&sup_total%5Bmax%5D=" \
          f"{sup_total_max}&precio_pesos_m2%5Bmin%5D=&precio_pesos_m2%5Bmax%5D=&precio_dolares_m2%5Bmin%5D=" \
          f"&precio_dolares_m2%5Bmax%5D=&expensas%5Bmin%5D=&expensas%5Bmax%5D= "
    if analize_flag:
        items_df = soup_to_df(scrap_now(url, file_name=file_name_html, scrap_web=scrap_web_flag))
        items_df = geographical_clusterization(items_df, cluster_radius_km)
        items_df, cluster_segment_dict = price_segmentation(items_df, cluster_segment_max_size)
        # gmplot_df(items_df, plt_flag=False)
        # gmplot_df(items_df, as_per='cluster', plt_flag=False)
        stats_list = stats_from_items(items_df, sup_t_tol=sup_t_tol)
        stats_summary_df = summary_from_stats_list(stats_list, cluster_segment_min_size=cluster_segment_min_size,
                                                   sort_by='relative_rentability')
        outfile = open('items_df.pickle', 'wb')
        pickle.dump(items_df, outfile)
        outfile.close()
        outfile = open('stats_list.pickle', 'wb')
        pickle.dump(stats_list, outfile)
        outfile.close()
        outfile = open('stats_summary_df.pickle', 'wb')
        pickle.dump(stats_summary_df, outfile)
        outfile.close()
    else:
        infile = open('items_df.pickle', 'rb')
        items_df = pickle.load(infile)
        infile.close()
        infile = open('stats_list.pickle', 'rb')
        stats_list = pickle.load(infile)
        infile.close()
        infile = open('stats_summary_df.pickle', 'rb')
        stats_summary_df = pickle.load(infile)
        infile.close()
    # Visualization
    print('*** Summary of Oportunities ***')
    print(stats_summary_df)
    bests_cluster_segment_index = \
        [int(i) for i in stats_summary_df.iloc[0:number_of_oportunities, :]['cluster_segment_index'].values]
    print('*** Best Oportunities ***')
    oportunities = items_df.iloc[0:0, :]
    for oportunity_index in bests_cluster_segment_index:
        oportunity = stats_list[oportunity_index].cluster_segment_df_res
        oportunities = pd.concat([oportunities, oportunity])
        print(f'\ncluster_segment_index = {oportunity_index}')
        print(oportunity)
    pass
    gmplot_df(oportunities, as_per='cluster_segment_index', plt_flag=False)

