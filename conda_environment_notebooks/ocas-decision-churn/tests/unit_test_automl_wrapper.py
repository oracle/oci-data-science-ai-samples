import unittest
import automl_wrapper
import pandas as pd
import numpy as np
from automl_wrapper import AutomlWrapper
import random
import os


class TestAutoMLWrapper(unittest.TestCase):
    def setUp(self):
        n_train = 20
        rnd_list = lambda n: [random.random() for _ in range(n)]
        rndint_list = lambda n: [random.randint(0, 1) for _ in range(n)]

        self.X_train = pd.DataFrame({'col1': rnd_list(n_train), 'col2': rnd_list(n_train)})
        self.y_train = pd.Series(rndint_list(n_train))

        self.n_test = 10
        self.X_test = pd.DataFrame({'col1': rnd_list(self.n_test), 'col2': rnd_list(self.n_test)})

        self.sample = 10
        self.df_sample = pd.DataFrame(
            {'col1': rnd_list(self.sample), 'col2': rnd_list(self.sample), 'target': rndint_list(self.sample)})
        self.target = 'target'

        self.eval_data = pd.DataFrame(
            {'col1': rnd_list(self.sample), 'col2': rnd_list(self.sample), 'target': rndint_list(self.sample)})

    def test_fit(self):
        model = AutomlWrapper()
        model.fit(self.X_train, self.y_train)
        self.assertIsNotNone(model.aml_trainer)

    def test_predict(self):
        model = AutomlWrapper()
        model.fit(self.X_train, self.y_train)
        y_pred = model.predict(self.X_test)
        self.assertIsInstance(y_pred, np.ndarray)
        self.assertEqual(y_pred.shape, (self.n_test,))

    def test_predict_proba(self):
        model = AutomlWrapper()
        model.fit(self.X_train, self.y_train)
        y_pred_proba = model.predict_proba(self.X_test)
        self.assertIsInstance(y_pred_proba, np.ndarray)
        self.assertEqual(y_pred_proba.shape, (self.n_test, 2))

    def test_get_feature_importance(self):
        model = AutomlWrapper()
        model.fit(self.X_train, self.y_train)
        feature_importance, global_shap = model.get_feature_importance(self.df_sample, self.target)
        self.assertIsNotNone(feature_importance)
        self.assertIsNotNone(global_shap)

    def test_save_feature_importance(self):
        feature_importance = pd.DataFrame({'feature': ['col1', 'col2'], 'attribution': [0.5, 0.4]})
        os.makedirs("test_outputs", exist_ok=True)
        path2json = './test_outputs/top_features.json'
        AutomlWrapper.save_feature_importance(feature_importance, True, path2json)
        self.assertTrue(os.path.exists(path2json))
        os.remove(path2json)
        os.removedirs("test_outputs")

    def test_evaluation(self):
        model = AutomlWrapper()
        model.fit(self.X_train, self.y_train)
        metrics = model.evaluation(self.eval_data, self.target)
        self.assertIsNotNone(metrics)
        self.assertIsInstance(metrics, dict)

