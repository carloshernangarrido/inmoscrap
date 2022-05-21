import webbrowser
import matplotlib
import numpy as np
from gmplot import gmplot


def gmplot_df(df):
    cluster_labels_list = list(set(df.loc[:, 'cluster']))
    n_clusters = len(cluster_labels_list)
    gmap = gmplot.GoogleMapPlotter(df.loc[0, 'lat'], df.loc[0, 'lng'], 13)
    color_map = matplotlib.cm.get_cmap('hsv')
    color_map_list = [matplotlib.colors.rgb2hex(color_map(1. * i / n_clusters)) for i in range(n_clusters)]
    # color_map_list = list(matplotlib.colors.BASE_COLORS.keys())
    for i_color, i in enumerate(cluster_labels_list):
        # i_color = i - 8*(i // 8)
        # s = [np.sqrt(sup_t) for sup_t in df.loc[df.loc[:, 'cluster'] == i, 'sup_t'].to_list()],
        s = [precio_rel for precio_rel in (0.1 * np.array(df.loc[df.loc[:, 'cluster'] == i, 'precio'].to_list())
                                           /
                                           np.array(df.loc[df.loc[:, 'cluster'] == i, 'sup_t'].to_list())).tolist()],
        gmap.scatter(
            lats=df.loc[df.loc[:, 'cluster'] == i, 'lat'].to_list(),
            lngs=df.loc[df.loc[:, 'cluster'] == i, 'lng'].to_list(),
            color=color_map_list[i_color],
            s=10,  # s,
            ew=2,
            marker=False,
            symbol='o',  # ['o' if seg == 0 else 'x' for seg in df.loc[df.loc[:, 'cluster'] == i, 'segment']],
            title=df.loc[df.loc[:, 'cluster'] == i, 'href'].to_list(),
            label=df.loc[df.loc[:, 'cluster'] == i, 'cluster'].to_list()
        )
    gmap.draw("map.html")
    chrome_path = 'C:/Program Files (x86)/Google/Chrome/Application/chrome.exe %s'
    webbrowser.get(chrome_path).open("file://G:/TRABAJO/Profesional/Python/inmoscrap/map.html")
