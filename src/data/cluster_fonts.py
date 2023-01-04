import os
import pickle
import sys
from enum import Enum
from multiprocessing.pool import ThreadPool
from typing import List
import numpy as np
import cachetools
import pandas
import pandas as pd
from cachetools import LRUCache
import scipy as sp
from sklearn.cluster import DBSCAN
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
np.random.seed(1)

from sklearn.metrics import pairwise_distances_argmin

def find_num_clusters(df, n_clusters = 10, rseed=2):
    sil_score_max = -1 
    for n_clusters in range(2,20):
        model = KMeans(n_clusters = n_clusters, init='k-means++', max_iter=100, n_init=1)
        labels = model.fit_predict(df)
        sil_score = silhouette_score(df, labels)
        if sil_score > sil_score_max:
            sil_score_max = sil_score
            best_n_clusters = n_clusters
        return best_n_clusters

class DBSCANWrapper(DBSCAN):
    def __init__(self,     
                 eps=0.5,
                 min_samples=5,
                 metric='euclidean',
                 metric_params=None,
                 algorithm='auto',
                 leaf_size=30,
                 p=None,
                 n_jobs=None):
        super().__init__(eps = eps, min_samples = min_samples, metric = metric, metric_params = metric_params, algorithm = algorithm, leaf_size = leaf_size, p = p, n_jobs = n_jobs)
    

    def predict(self, X_new, metric=sp.spatial.distance.cosine):
        # Result is noise by default
        y_new = np.ones(shape=len(X_new), dtype=int)*-1 

        # Iterate all input samples for a label
        for j, x_new in enumerate(X_new):
            # Find a core sample closer than EPS
            for i, x_core in enumerate(self.components_): 
                if metric(x_new, x_core) < self.eps:
                    # Assign label of x_core to x_new
                    y_new[j] = self.labels_[self.core_sample_indices_[i]]
                    break

        return y_new

class ModelType(Enum):
    """
    Class for selecting a cluster model type

    The class supports two types of models:
    K-means (see: https://scikit-learn.org/stable/modules/generated/sklearn.cluster.KMeans.html)
    DBSCAN (see: https://scikit-learn.org/stable/modules/generated/sklearn.cluster.DBSCAN.html)
    """
    KMeans = 0
    DBSCAN = 1


class ModelWrapper:
    """
    Class that packs into the logic of a cluster model for anomalous wafers

    Parameters
    ----------

    model : Sklearn based model
    """

    def __init__(self, model_type: ModelType):

        self.model_type = model_type

    def perp(self, data):
        """
        Pre-processing data for ml model

        Parameters
        ----------

        data : pd.DataFrame
        """
        return data.fillna(0)._get_numeric_data()

    def build_model(self, data):
        """
        Build a cluster model for the Outliers wafers.

        Parameters
        ----------

        data : pd.DataFrame
            the data is the Outliers table with cols pre ZONEi_HBj (e.g. Zscore_Z4_HB21)

        Return:
            None

        See Also:
            The method trains the model, predicts the clusters on the training set
        """
        data_prep = self.perp(data)
        if self.model_type == ModelType.KMeans:
            self.model = KMeans(n_clusters=find_num_clusters(data_prep), random_state=0, init='k-means++', max_iter=100, n_init=1)
        else:
            self.model = DBSCANWrapper(eps=2)

        self.model.fit(data_prep)
        self.fill_missing_columns = data_prep.median()
        self.feature_names_list = data_prep.columns
    def predict(self, data):
        """
        The inference method

         Parameters
        ----------

        data : pd.DataFrame
            the data is the Outliers table with cols pre ZONEi_HBj (e.g. Zscore_Z4_HB21)
        Return:
            list
            list of cluster_names for each wafer in the data

        See Also:
            The method verifies that the columns in the new data are identical
            to the data the model was trained on and handles in case any mismatch is detected:
                If there is another column: it is discarded
                If an existing column is missing: The method creates such a column and fills it with the median value of the training set
        """

        def match_features(data):
            missing_features = list(set(self.feature_names_list) - set(list(data)))
            if missing_features:
                print('In new data missing', len(missing_features), 'features (fill with median from tarin data)')
                for item in missing_features: data[item] = self.fill_missing_columns[item]
            return data[self.feature_names_list]

        return self.model.predict(self.perp(match_features(data))[self.feature_names_list])


def train_model(df: pandas.DataFrame, model_type: ModelType):
    model = ModelWrapper(model_type)
    model.build_model(df)
    return model
