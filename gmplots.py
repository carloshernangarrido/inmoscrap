import webbrowser
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from gmplot import gmplot


def gmplot_df(df, plt_flag=False, as_per='cluster_segment_index'):
    labels_list = list(set(df.loc[:, as_per]))
    n_clusters = len(labels_list)
    gmap = gmplot.GoogleMapPlotter(df.iloc[0, 5], df.iloc[0, 6], 13)
    color_map = matplotlib.cm.get_cmap('hsv')
    color_map_list = [matplotlib.colors.rgb2hex(color_map(1. * i / n_clusters)) for i in range(n_clusters)]
    if plt_flag:
        plt.figure()
    for i_color, i in enumerate(labels_list):
        precio_rel_list = [precio_rel for precio_rel in
                           (0.1 * np.array(df.loc[df.loc[:, as_per] == i, 'precio'].to_list())
                            /
                            np.array(df.loc[df.loc[:, as_per] == i, 'sup_t'].to_list())).tolist()]
        segment_list = df.loc[df.loc[:, as_per] == i, 'segment'].to_list()
        if plt_flag:
            symbols = matplotlib.markers.MarkerStyle.filled_markers
            for i_item, xy in enumerate(zip(df.loc[df.loc[:, as_per] == i, 'lat'].to_list(),
                                            df.loc[df.loc[:, as_per] == i, 'lng'].to_list())):
                plt.scatter(xy[0], xy[1], color=color_map_list[i_color],
                            s=10 * precio_rel_list[i_item],
                            marker=symbols[(segment_list[i_item] + 1) % len(symbols)])
        else:
            symbols = ['o', 'x', '+']
            site_name = 'https://www.inmoclick.com.ar'
            best_precio_rel = df.loc[df.loc[:, as_per] == i].sort_values(by='precio_rel', ascending=True)
            best_precio = df.loc[df.loc[:, as_per] == i].sort_values(by='precio', ascending=True)
            best = pd.concat([best_precio_rel.iloc[0:1, :], best_precio.iloc[0:1, :]])
            info_windows = []
            for i_info in range(2):
                relativo = 'Relativo' if i_info == 0 else ''
                info_windows.append(
                    f'<h3><strong>Mejor Precio {relativo}</strong></h3>'
                    f'\n<p><strong>Precio:</strong> US$ {best.iloc[i_info]["precio"]}</p>'
                    f'\n<p><strong>Superficie:</strong> {best.iloc[i_info]["sup_t"]} m<sup>2</sup></p>'
                    f'\n<p><strong>Precio relativo:</strong> {round(best.iloc[i_info]["precio_rel"], 2)} US$/m<sup>2</sup></p>'
                    f'\n<p style="text-align: left;"><a href="{site_name + best.iloc[i_info]["href"]}">link</a></p>')
            for lat_, lng_, info_windows_, color_ in \
                    zip(best.iloc[:]['lat'].to_list(), best.iloc[:]['lng'].to_list(), info_windows, ['red', 'cyan']):
                gmap.marker(lat=lat_,
                            lng=lng_,
                            info_window=info_windows_,
                            color=color_)
            gmap.scatter(
                lats=df.loc[df.loc[:, as_per] == i, 'lat'].to_list(),
                lngs=df.loc[df.loc[:, as_per] == i, 'lng'].to_list(),
                color=color_map_list[i_color],
                s=precio_rel_list,
                ew=2,
                marker=False,
                symbol=[symbols[(segment_list[i_item] + 1) % len(symbols)] for i_item
                        in range(len(df.loc[df.loc[:, as_per] == i, 'lat'].to_list()))],
                title=df.loc[df.loc[:, as_per] == i, 'href'].to_list(),
                label=df.loc[df.loc[:, as_per] == i, as_per].to_list()
            )
    if plt_flag:
        plt.show()
    else:
        gmap.draw("map.html")
        chrome_path = 'C:/Program Files (x86)/Google/Chrome/Application/chrome.exe %s'
        webbrowser.get(chrome_path).open("file://G:/TRABAJO/Profesional/Python/inmoscrap/map.html")
