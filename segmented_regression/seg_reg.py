import numpy as np
from scipy.optimize import minimize
from sklearn.preprocessing import MinMaxScaler
from typing import List


def piece_wise_constant(xy_: List[float], atanm: float, x_0: float, y_0: float, v_below: float, v_above: float) -> float:
    """
    Two dimensional piece-wise constant function.

    :param xy_: evaluation point
    :param atanm: atan(slope) of the straight line
    :param x_0: x coordinate of a point beloging to the straight line
    :param y_0: y coordinate of a point beloging to the straight line
    :param v_below: value returned for points below straight line
    :param v_above: value returned for points above straight line

    :returns: v_below if evaluation point is below the straight line and viceversa.
    """
    x_ = xy_[0]
    y_ = xy_[1]
    m = np.tan(atanm)
    if y_ - y_0 < m * (x_ - x_0):
        return v_below
    else:
        return v_above


def obj_fun(x: List[float], xyz_cluster_: np.array, p_norm: int = 2) -> float:
    """
    Objective function, defined as the norm of the error between the given and predicted values.

    :param x: vector containing [atan(slope), point_x, point_y, value_below, value_avobe]
    :param xyz_cluster_: matrix containg a sample [x, y, value] in each row
    :param p_norm: p value to calculate the norm of the error.

    :returns: The current value of the objective function.
    """
    z_trial = \
        np.apply_along_axis(
            lambda _: piece_wise_constant(_, atanm=x[0], x_0=x[1], y_0=x[2], v_below=x[3], v_above=x[4]),
            axis=1, arr=xyz_cluster_[:, 0:2])
    return np.linalg.norm(z_trial.reshape((-1, 1)) - xyz_cluster_[:, 2].reshape((-1, 1)), p_norm)


class PWCSegReg:
    """
    This class allows fiting a piece-wise constant segmented regression as a scalar function of 2 variables
    """

    def __init__(self, p_norm: int = 2):
        self.p_norm = p_norm
        self.m = 0.0
        self.x_0 = 0.0
        self.y_0 = 0.0
        self.v_below = 0.0
        self.v_above = 0.0

    def predict_xy(self, xy: List[float]):
        """
        Predicts the value for a given point.

        :param xy: Point as a list of coordinates x and y.
        """
        return piece_wise_constant(xy_=xy, atanm=np.arctan(self.m), x_0=self.x_0, y_0=self.y_0,
                                   v_below=self.v_below, v_above=self.v_above)

    def predict(self, xy_matrix: np.array) -> np.array:
        """
        Predicts the values for a set of points given as a matrix of coordinates x and y.

        :param xy_matrix: A matrix containing a point in each row. Column 0 is x, and column 1 is y.

        :returns: A 1D numpy array with the predicted values.
        """
        z_vector = \
            np.apply_along_axis(
                lambda _: self.predict_xy(_), axis=1, arr=xy_matrix)
        return z_vector

    def fit(self, xy_train, z_train):
        """
        Fit the model to the data given.

        :param xy_train: A matrix of m_samples rows. First column is x coordinate and second column is y coordinate.
        :param z_train: A vector of Values of the training data for the corresponding xy_points.

        :returns: None
        """
        xyz_train = np.hstack((xy_train, z_train))
        scaler = MinMaxScaler(feature_range=(-1, 1))
        scaler.fit(xyz_train)
        xyz_train_norm = scaler.transform(xyz_train)
        res = minimize(obj_fun, x0=np.array([0.0, 0.0, 0.0, 0.0, 0.0]), method='Nelder-Mead',
                       args=(xyz_train_norm, 2), bounds=[(-1.57, 1.57), (-1., 1), (-1., 1.), (-1., 1.), (-1., 1.)],
                       options={'fatol': 0.01, 'xatol': 0.01, 'maxfev': 1000, 'maxiter': 100})
        # back to original scale
        res_x_os = res.x.copy()
        res_x_os[[1, 2, 3]] = scaler.inverse_transform(np.array([res.x[1], res.x[2], res.x[3]]).reshape(1, -1))
        res_x_os[[1, 2, 4]] = scaler.inverse_transform(np.array([res.x[1], res.x[2], res.x[4]]).reshape(1, -1))
        pto_ini = np.array([res.x[1], res.x[2], 0]).reshape(1, -1)
        pto_fin = np.array([res.x[1], res.x[2], 0]).reshape(1, -1) + np.array([1, np.tan(res.x[0]), 0]).reshape(1, -1)
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
        return piece_wise_constant(xy_=xy, atanm=np.arctan(self.m), x_0=self.x_0, y_0=self.y_0,
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


class PWCSegRegMultiple:
    """
    This class allows fiting a piece-wise constant segmented regression as a scalar function of 2 variables,
    using multiple classes, which are leaves of a regression binary tree.
    """

    def __init__(self, p_norm: int = 2, max_items_per_class: int = float('inf')):
        self.p_norm = p_norm
        self.max_items_per_class = max_items_per_class
        self.split_list = []
        self.pwcsr_list = []
        self.classes = None
        self.classes_labels = None

    def _fit(self, xy_train, z_train):
        # print(f'***\n{self.classes}')
        if self.classes is None:
            self.classes = (0 * z_train.astype(int)).reshape((-1,))
        self.classes_labels = np.unique(self.classes)
        for class_label in self.classes_labels:
            xy_train_ = xy_train[self.classes == class_label, :]
            z_train_ = z_train[self.classes == class_label]
            # print(f'*** class N {class_label} ***')
            # print(np.hstack((xy_train_, z_train_)))
            if xy_train_.shape[0] > self.max_items_per_class:
                # print(f'*{self.classes_labels}**{class_label}')
                max_class_ = max(self.classes)
                self.pwcsr_list.append(PWCSegReg(p_norm=self.p_norm))
                self.pwcsr_list[-1].fit(xy_train_, z_train_)
                self.classes[self.classes == class_label] = \
                    self.classes[self.classes == class_label] + \
                    (max_class_ - class_label + 1) * self.pwcsr_list[-1].classify(xy_train_)

    def fit(self, xy_train, z_train):
        if self.classes is None:
            self.classes = (0 * z_train.astype(int)).reshape((-1,))
        max_class = None
        while max(self.classes) != max_class:
            max_class = max(self.classes)
            self._fit(xy_train, z_train)

