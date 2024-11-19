import unittest
import numpy as np
import myutils
import pandas as pd
import matplotlib.pyplot as plt
import os
from unittest.mock import patch
from io import StringIO


class TestMyutils(unittest.TestCase):

    def setUp(self):
        self.importance = pd.DataFrame({'feature': ['A', 'B', 'C', 'D', 'E'],
                                        'abs_attribution': [0.3, 0.2, 0.1, 0.05, 0.01]})

        self.dfx = pd.DataFrame({'col1': ['A', 'B', 'C', 'D', 'E'],
                                 'col2': [1, 2, 3, 4, 5],
                                 'target': [0, 1, 0, 1, 0]})
        self.col = 'col1'
        self.target = 'target'
        self.n = 3
        self.path2fig = 'test.png'

    def test_plot_importance(self):
        myutils.plot_importance(self.importance, n=3, shap_column='abs_attribution', title='Test Plot')
        self.assertEqual(len(plt.gca().patches), 3)
        self.assertEqual(plt.gca().get_title(), 'Test Plot')
        self.assertEqual(list(plt.yticks()[0]), [3, 2, 1])

    def test_binary_metrics(self):
        target = np.array([0, 0, 1, 1])
        prediction = np.array([0, 0, 1, 1])
        res = myutils.binary_metrics(target, prediction)
        expected = {'mean_target': 0.5,
                    'mean_pred': 0.5,
                    'bias_ratio': 0.0,
                    'roc_auc': 1.0,
                    'logloss': 0.0,
                    'best_accuracy': 0.5,
                    'best_precision': 1.0,
                    'best_recall': 1.0,
                    'best_thresh': 1,
                    'best_f1': 1.0}

        for k, v in expected.items():
            if v:
                self.assertEqual(res[k], v)

    def tearDown(self):
        if os.path.exists(self.path2fig):
            os.remove(self.path2fig)

    def test_get_hist_overlap(self):
        # Test case where the column type is object
        with patch('sys.stdout', new=StringIO()) as fake_out:
            myutils.get_hist_overlap(self.dfx, self.col, self.target, self.n, self.path2fig)
        self.assertTrue(os.path.exists(self.path2fig))

        # Test case where the column type is not object
        self.col = 'col2'
        with patch('sys.stdout', new=StringIO()) as fake_out:
            myutils.get_hist_overlap(self.dfx, self.col, self.target, self.n, self.path2fig)
        self.assertTrue(os.path.exists(self.path2fig))

    def test_plot_pie_chart(self):
        # Setup
        counts = pd.Series({0: 25, 1: 75})
        expected_labels = ["not-churned", "churned"]
        expected_sizes = [25, 75]

        # Call function
        myutils.plot_pie_chart(counts)
        plt.close()

    def test_correlation(self):
        df = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6], 'C': [7, 8, 9]})
        cols = ['A', 'B', 'C']

        myutils.correlation(df, cols)
        plt.close()
