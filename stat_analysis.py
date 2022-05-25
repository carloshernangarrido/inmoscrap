import numpy as np
import pandas as pd


class ClusterSegmentStats:
    """
    Statistics of a cluster_segment.
    """

    def __init__(self, cluster_segment_df: pd.DataFrame, sup_t_tol: float = np.inf):
        """
        Init function for this class.

        :param cluster_segment_df: an slice of the data frame containing all the items, for a specific  cluster_segment.

        :param sup_t_tol: tolerance in the sup_t (total area of the surface); e.g: if sup_t_tol = 0, only the items with equal sup_t are considered; if sup_t_tol = 1, 100% of dispersion is allowed.
        TODO: use parameter sup_t_tol
        """
        self.cluster_segment_df = cluster_segment_df
        self.cluster_segment_df.insert(loc=self.cluster_segment_df.shape[1], column='precio_rel', value=
                                       self.cluster_segment_df.loc[:, 'precio'].values /
                                       self.cluster_segment_df.loc[:, 'sup_t'].values)
        self.max_price = self.get_max_price()
        # self.min_price = self.get_min_price()
        # self.mean_price = self.get_mean_price()
        # self.median_price = self.get_median_price()
        # self.max_rel_price = self.get_max_rel_price()
        # self.min_rel_price = self.get_min_rel_price()
        # self.mean_rel_price = self.get_mean_rel_price()
        # self.median_rel_price = self.get_median_rel_price()

    def get_max_price(self):
        return np.max(self.cluster_segment_df.loc[:, 'precio'].values)

    def get_min_price(self):
        return np.max(self.cluster_segment_df.loc[:, 'precio'].values)

    def get_mean_price(self):
        return np.max(self.cluster_segment_df.loc[:, 'precio'].values)

    def get_median_price(self):
        return np.max(self.cluster_segment_df.loc[:, 'precio'].values)


def stats_from_items(items_df):
    stats = []
    for cs_index in list(set(items_df.loc[:, 'cluster_segment_index'])):
        stats.append(ClusterSegmentStats(items_df.loc[items_df.loc[:, 'cluster_segment_index'] == cs_index, :]))
    return stats
