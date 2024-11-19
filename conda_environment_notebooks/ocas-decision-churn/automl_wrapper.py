import logging
import os
from typing import Union, Tuple, Dict
import json
import automl
import matplotlib.pylab as plt
import numpy as np
import pandas as pd
from automl import init

import myutils


class AutomlWrapper:
    """
    Wrapper class for automl library.
    """

    def __init__(self, **kwargs) -> None:
        """
        Initialize AutomlWrapper class.

        :param kwargs: keyword arguments to initialize AutomlWrapper class.
        """

        if not kwargs.get("init", None):
            init(engine='local',
                 loglevel=logging.CRITICAL,
                 engine_opts={'max_timeout': 1000000,
                              'n_jobs': 16})
        else:
            init(**kwargs["init"])

        model_list = ['ExtraTreesClassifier',
                      'LGBMClassifier',
                      'LogisticRegression',
                      'RandomForestClassifier']
        self.model_list = kwargs.get("model_list", model_list)

        eval_metric = kwargs.get("eval_metric", "roc_auc")
        self.aml_trainer = automl.Pipeline(
            task="classification",
            model_list=self.model_list,
            score_metric=eval_metric)

    def fit(self, x_train: pd.DataFrame,
            y_train: pd.Series,
            cv: Union[str, int] = "auto") -> None:
        """
        fit a model to the training data

        :param x_train: pandas dataframe of training data. :param y_train: pandas series of training labels. :param
        cv: cross validation method, can be an integer or str, if set to auto, it will use 5-fold cross validation.
        """
        self.aml_trainer.fit(X=x_train, y=y_train, cv=cv)

        return

    def predict(self, x: pd.DataFrame) -> np.ndarray:
        """
        Predict the class labels for the provided data.
        :param x: pandas dataframe of test data.
        :return: predicted labels for the test data.
        """
        return self.aml_trainer.predict(x)

    def predict_proba(self, X_test: pd.DataFrame) -> np.ndarray:
        """
        Predict the class probabilities for the provided data.

        :param X_test: pandas dataframe of test data.
        :return: predicted class probabilities for the test data.
        """
        return self.aml_trainer.predict_proba(X_test)



    def get_feature_importance(self, df_sample: pd.DataFrame,
                               target: str,
                               path2output: str = "outputs/global_shap.csv") -> Tuple[pd.DataFrame, object]:
        """
        Get global feature importance

        :param df_sample: sample data as pandas dataframe to get feature importance.
        :param target: target column name
        :param path2output: path to save feature importance csv file.
        :return: panda dataframe containing the feature importance and the explain_model object
        """
        self.init_explainer(train_x=df_sample.drop(target, axis=1),
                            train_y=df_sample[target])
        global_shap = self.explain_model()
        feature_importance = global_shap.to_dataframe()
        feature_importance.to_csv(path2output, index=False)

        feature_importance["abs_attribution"] = feature_importance['attribution'].abs()
        feature_importance = feature_importance.sort_values(by="abs_attribution", ascending=False)
        return feature_importance, global_shap

    def init_explainer(self, train_x: pd.DataFrame, train_y: pd.Series, **kwargs) -> None:
        """
        Initialize the explainer object.

        :param train_x: sample data to initialize the explainer
        :param train_y: labels for the sample data
        :param kwargs: other AutoML parameters
        :return:
        """
        self.explainer = automl.MLExplainer(
            self.aml_trainer, X=train_x, y=train_y, task="classification", **kwargs
        )

    def explain_model(self, **kwargs) -> object:
        """
        Explain the model using the AutoML explain_model method

        :param kwargs:
        :return: explain result as an object
        """
        self.explainer.configure_explain_model(tabulator_type="kernel_shap", **kwargs)
        result = self.explainer.explain_model()
        return result

    def explain_prediction(self, x: pd.DataFrame) -> object:
        """
        Get local feature importance for given data point.

        :param x: data point to get local feature importance for.
        :return: local feature importance for given data point as an object
        """
        return self.explainer.explain_prediction(x)

    @staticmethod
    def save_feature_importance(feature_importance: pd.DataFrame,
                                overwrite: bool = False,
                                path2json: str = './outputs/top_features.json') -> None:
        """
        Save the feature importance as a json file.

        :param feature_importance: feature importance as a pandas dataframe.
        :param overwrite: boolean, whether to overwrite the file if it already exists.
        :param path2json: path to save the json file.
        :return:
        """

        top_features = feature_importance['feature'].tolist()
        if os.path.exists(path2json) and not overwrite:
            raise IOError(f"{path2json} exists!")
        with open(path2json, 'w') as f:
            json.dump(top_features, f)

    def evaluation(self, df_eval: pd.DataFrame, target: str) -> Dict[str, float]:
        """
        Evaluate the model given the evaluation data.

        :param df_eval: evaluation data as pandas dataframe
        :param target: target column name
        :return:
        """

        y_proba = self.predict_proba(df_eval.drop([target], axis=1))
        return myutils.binary_metrics(df_eval[target], y_proba[:, 1])

    def print_summary(self) -> None:
        """
        Prints information about the last
        """
        self.aml_trainer.print_summary()
        return

    def selected_features(self) -> list:
        """
        Return names of features selected by the AutoML pipeline.
        """
        return self.aml_trainer.selected_features_names_
