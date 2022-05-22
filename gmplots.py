import webbrowser
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from gmplot import gmplot


def gmplot_df(df, plt_flag=False):
    cluster_labels_list = list(set(df.loc[:, 'cluster']))
    n_clusters = len(cluster_labels_list)
    gmap = gmplot.GoogleMapPlotter(df.iloc[0, 5], df.iloc[0, 6], 13)
    color_map = matplotlib.cm.get_cmap('hsv')
    color_map_list = [matplotlib.colors.rgb2hex(color_map(1. * i / n_clusters)) for i in range(n_clusters)]
    # color_map_list = list(matplotlib.colors.BASE_COLORS.keys())
    if plt_flag:
        plt.figure()
    for i_color, i in enumerate(cluster_labels_list):
        # i_color = i - 8*(i // 8)
        # s = [np.sqrt(sup_t) for sup_t in df.loc[df.loc[:, 'cluster'] == i, 'sup_t'].to_list()],
        s = [precio_rel for precio_rel in (0.1 * np.array(df.loc[df.loc[:, 'cluster'] == i, 'precio'].to_list())
                                           /
                                           np.array(df.loc[df.loc[:, 'cluster'] == i, 'sup_t'].to_list())).tolist()]
        # symbol = ['o' if seg == 0 else 'x' for seg in df.loc[df.loc[:, 'cluster'] == i, 'segment']]
        symbol = matplotlib.markers.MarkerStyle.filled_markers
        if plt_flag:
            for i_segment, xy in enumerate(zip(df.loc[df.loc[:, 'cluster'] == i, 'lat'].to_list(),
                                               df.loc[df.loc[:, 'cluster'] == i, 'lng'].to_list())):
                plt.scatter(xy[0], xy[1], color=color_map_list[i_color],
                            s=10*s[i_segment], marker=symbol[(i_segment + 1) % len(symbol)])
        else:
            gmap.scatter(
                lats=df.loc[df.loc[:, 'cluster'] == i, 'lat'].to_list(),
                lngs=df.loc[df.loc[:, 'cluster'] == i, 'lng'].to_list(),
                color=color_map_list[i_color],
                s=s,
                ew=2,
                marker=False,
                symbol=symbol,
                title=df.loc[df.loc[:, 'cluster'] == i, 'href'].to_list(),
                label=df.loc[df.loc[:, 'cluster'] == i, 'cluster'].to_list()
            )
    if plt_flag:
        plt.show()
    else:
        gmap.draw("map.html")
        chrome_path = 'C:/Program Files (x86)/Google/Chrome/Application/chrome.exe %s'
        webbrowser.get(chrome_path).open("file://G:/TRABAJO/Profesional/Python/inmoscrap/map.html")
