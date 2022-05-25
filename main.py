# This scrip scraps inmoclick.com
from data_cure import geographical_clusterization, price_segmentation
from gmplots import gmplot_df
from scraper import scrap_now, soup_to_df
from stat_analysis import stats_from_items

if __name__ == '__main__':
    scrap_web_flag = False
    limit = 3000
    sup_total_min = 50
    sup_total_max = 10000
    precio_min = 1000
    precio_max = 1000000
    cluster_radius_km = 0.5
    cluster_segment_max_size = 50
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
    gmplot_df(items_df, plt_flag=False)
    gmplot_df(items_df, as_per='cluster', plt_flag=False)
    # stats_list = stats_from_items(items_df)
    a = 1

