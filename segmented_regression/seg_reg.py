import numpy as np
from scipy.optimize import minimize
from sklearn.preprocessing import MinMaxScaler
from typing import List


def piece_wise_constant(xy_: List[float], m: float, x_0: float, y_0: float, v_below: float, v_above: float) -> float:
    """ Two dimensional piece-wise constant function
    :param xy_: evaluation point
    :param m: slope of the straight line
    :param x_0: x coordinate of a point beloging to the straight line
    :param y_0: y coordinate of a point beloging to the straight line
    :param v_below: value returned for points below straight line
    :param v_above: value returned for points above straight line
    """
    x_ = xy_[0]
    y_ = xy_[1]
    if y_ - y_0 < m * (x_ - x_0):
        return v_below
    else:
        return v_above


def obj_fun(x: List[float], xyz_cluster_: np.array, p_norm: int = 2) -> float:
    """Objective function, defined as the norm of the error between the given and predicted values.
    :param x: vector containing [slope, point_x, point_y, value_below, value_avobe]
    :param xyz_cluster_: matrix containg a sample [x, y, value] in each row
    :param p_norm: p value to calculate the norm of the error
    """
    z_trial = \
        np.apply_along_axis(
            lambda _: piece_wise_constant(_, m=x[0], x_0=x[1], y_0=x[2], v_below=x[3], v_above=x[4]),
            axis=1, arr=xyz_cluster_[:, 0:2])
    return np.linalg.norm(z_trial.reshape((-1, 1)) - xyz_cluster_[:, 2].reshape((-1, 1)), p_norm)


class PWCSegReg:
    """
    This class allows fiting a piece-wise constant segmented regression as a scalar function of 2 variables
    """
    def __init__(self, p_norm: int=2):
        self.p_norm = p_norm
        self.m = 0.0
        self.x_0 = 0.0
        self.y_0 = 0.0
        self.v_below = 0.0
        self.v_above = 0.0

    def predict_xy(self, xy: List[float]):
        """
        Predicts the value for a given point.

        :param xy: Point as a list of coordinates x and y"""
        return piece_wise_constant(xy_=xy, m=self.m, x_0=self.x_0, y_0=self.y_0,
                                   v_below=self.v_below, v_above=self.v_above)

    def predict(self, xy_matrix: np.array) -> np.array:
        """
        Predicts the values for a set of points given as a matrix of coordinates x and y.

        :param xy_matrix: A matrix containing a point in each row. Column 0 is x, and column 1 is y.

        :returns z_vector: A 1D numpy array with the predicted values
        """
        z_vector = \
            np.apply_along_axis(
                lambda _: self.predict_xy(_), axis=1, arr=xy_matrix)
        return z_vector

    def fit(self, xy_train, z_train):
        xyz_train = np.hstack((xy_train, z_train))
        scaler = MinMaxScaler()
        scaler.fit(xyz_train)
        xyz_train_norm = scaler.transform(xyz_train)
        res = minimize(obj_fun, x0=np.array([0, 0.5, 0.5, 0.5, 0.5]), method='Powell',
                       args=(xyz_train_norm, 2), bounds=[(-1e6, 1e6), (0, 1), (0, 1), (0, 1), (0, 1)])
        # back to original scale
        res_x_os = res.x.copy()
        res_x_os[[1, 2, 3]] = scaler.inverse_transform(np.array([res.x[1], res.x[2], res.x[3]]).reshape(1, -1))
        res_x_os[[1, 2, 4]] = scaler.inverse_transform(np.array([res.x[1], res.x[2], res.x[4]]).reshape(1, -1))
        pto_ini = np.array([res.x[1], res.x[2], 0]).reshape(1, -1)
        pto_fin = np.array([res.x[1], res.x[2], 0]).reshape(1, -1) + np.array([1, res.x[0], 0]).reshape(1, -1)
        pto_ini_os = scaler.inverse_transform(pto_ini)
        pto_fin_os = scaler.inverse_transform(pto_fin)
        res_x_os[0] = (pto_fin_os[0, 1] - pto_ini_os[0, 1]) / (pto_fin_os[0, 0] - pto_ini_os[0, 0])
        self.m = res_x_os[0]
        self.x_0 = res_x_os[1]
        self.y_0 = res_x_os[2]
        self.v_below = res_x_os[3]
        self.v_above = res_x_os[4]

    def classify_xy(self, xy: List[float]):
        """
        Classify whether the point is avobe or below the straight line.

        :param xy: Point as a list of coordinates x and y

        :returns str: Class 0 'below', or 1 'above'
        """
        return piece_wise_constant(xy_=xy, m=self.m, x_0=self.x_0, y_0=self.y_0,
                                   v_below=0, v_above=1)

    def classify(self, xy_matrix: np.array) -> np.array:
        """
        Classify the set of points given as a matrix of coordinates x and y.

        :param xy_matrix: A matrix containing a point in each row. Column 0 is x, and column 1 is y.

        :returns class_vector: A list of strings with the predicted classes
        """
        class_vector = \
            np.apply_along_axis(
                lambda _: self.classify_xy(_), axis=1, arr=xy_matrix)
        return class_vector
