import numpy as np
import pandas as pd


class ClusterSegmentStats:
    """
    Statistics of a cluster_segment.
    """

    def __init__(self, cluster_segment_df: pd.DataFrame, sup_t_tol: float = np.inf,
                 res_dict=None,
                 sorted_by: str = 'precio_rel'):
        """
        Init function for this class.

        :param cluster_segment_df: an slice of the data frame containing all the items, for a specific  cluster_segment.

        :param sup_t_tol: tolerance in the sup_t (total area of the surface); e.g: if sup_t_tol = 0, only the items with equal sup_t are considered; if sup_t_tol = 1, 100% of dispersion is allowed.

        :param res_dict: restrictions of luz, agua, gas to include items in the cluster_segment.

        :param sorted_by: str indicating the column of the cluster_segment_df to sort the values
        """
        if res_dict is None:
            res_dict = {'luz': False, 'agua': False, 'gas': False}
        self.res_dict = res_dict
        self.sup_t_tol = sup_t_tol
        self.cluster_segment_df = cluster_segment_df
        self.sup_t_0 = np.median(self.cluster_segment_df.loc[:, 'sup_t'].values)
        self.cluster_segment_df_res = self.cluster_segment_df.copy()
        self.restric_to_sup_t_tol()
        self.restric_to_res_dict()
        if self.cluster_segment_df_res.shape[0] > 0:
            self.max_price = self.get_max_price()
            self.min_price = self.get_min_price()
            self.mean_price = self.get_mean_price()
            self.median_price = self.get_median_price()
            self.max_rel_price = self.get_max_rel_price()
            self.min_rel_price = self.get_min_rel_price()
            self.mean_rel_price = self.get_mean_rel_price()
            self.median_rel_price = self.get_median_rel_price()
            self.arg_min_price = self.get_arg_min_price()
            self.arg_min_rel_price = self.get_arg_min_rel_price()
        else:
            self.max_price = 0
            self.min_price = 0
            self.mean_price = 0
            self.median_price = 0
            self.max_rel_price = 0
            self.min_rel_price = 0
            self.mean_rel_price = 0
            self.median_rel_price = 0
            self.arg_min_price = 0
            self.arg_min_rel_price = 0
        self.cluster_segment_df_res.sort_values(by=sorted_by, inplace=True)

    def restric_to_sup_t_tol(self):
        self.cluster_segment_df_res. \
            drop(self.cluster_segment_df_res[(self.cluster_segment_df_res.sup_t < self.sup_t_0 * (1 - self.sup_t_tol))
                                             |
                                             (self.cluster_segment_df_res.sup_t > self.sup_t_0 * (1 + self.sup_t_tol))]
                 .index, inplace=True)

    def restric_to_res_dict(self):
        if self.res_dict['luz'] is True:
            self.cluster_segment_df_res. \
                drop(self.cluster_segment_df_res[self.cluster_segment_df_res.luz == False].index, inplace=True)
        if self.res_dict['agua'] is True:
            self.cluster_segment_df_res. \
                drop(self.cluster_segment_df_res[self.cluster_segment_df_res.agua == False].index, inplace=True)
        if self.res_dict['gas'] is True:
            self.cluster_segment_df_res. \
                drop(self.cluster_segment_df_res[self.cluster_segment_df_res.gas == False].index, inplace=True)

    def get_max_price(self):
        return np.max(self.cluster_segment_df_res.loc[:, 'precio'].values)

    def get_min_price(self):
        return np.min(self.cluster_segment_df_res.loc[:, 'precio'].values)

    def get_mean_price(self):
        return np.mean(self.cluster_segment_df_res.loc[:, 'precio'].values)

    def get_median_price(self):
        return np.median(self.cluster_segment_df_res.loc[:, 'precio'].values)

    def get_max_rel_price(self):
        return np.max(self.cluster_segment_df_res.loc[:, 'precio_rel'].values)

    def get_min_rel_price(self):
        return np.min(self.cluster_segment_df_res.loc[:, 'precio_rel'].values)

    def get_mean_rel_price(self):
        return np.mean(self.cluster_segment_df_res.loc[:, 'precio_rel'].values)

    def get_median_rel_price(self):
        return np.median(self.cluster_segment_df_res.loc[:, 'precio_rel'].values)

    def get_arg_min_price(self):
        return np.argmin(self.cluster_segment_df_res.loc[:, 'precio'].values)

    def get_arg_min_rel_price(self):
        return np.argmin(self.cluster_segment_df_res.loc[:, 'precio_rel'].values)


def stats_from_items(items_df, sup_t_tol: float = np.inf, res_dict: dict = None):
    stats = []
    for cs_index in list(set(items_df.loc[:, 'cluster_segment_index'])):
        stats.append(ClusterSegmentStats(items_df.loc[items_df.loc[:, 'cluster_segment_index'] == cs_index, :],
                                         sup_t_tol=sup_t_tol, res_dict=res_dict))
    return stats


def summary_from_stats_list(stats_list, cluster_segment_min_size=1, sort_by='relative_rentability'):
    stats_df = pd.DataFrame(np.array([[i for i in range(len(stats_list))],
                                      [stats.cluster_segment_df_res.shape[0] for stats in stats_list],
                                      [stats.min_price for stats in stats_list],
                                      [stats.median_price for stats in stats_list],
                                      [stats.min_rel_price for stats in stats_list],
                                      [stats.median_rel_price for stats in stats_list]]).T,
                            columns=['cluster_segment_index', 'count',
                                     'min_price', 'median_price', 'min_rel_price', 'median_rel_price'])
    stats_df.insert(loc=stats_df.shape[1], column='rentability',
                    value=stats_df.median_price - stats_df.min_price)
    stats_df.insert(loc=stats_df.shape[1], column='relative_rentability',
                    value=stats_df.median_rel_price - stats_df.min_rel_price)
    stats_df = stats_df.drop(stats_df.loc[stats_df.loc[:, 'count'] < cluster_segment_min_size, :].index)
    return stats_df.sort_values(by=sort_by, ascending=False)
