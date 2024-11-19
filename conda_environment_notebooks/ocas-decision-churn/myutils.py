import os.path
import random
from typing import Dict, List

import matplotlib.pylab as plt
import numpy as np
import pandas as pd
import seaborn as sns
import sklearn.metrics
from sklearn.pipeline import Pipeline
from sklearn import preprocessing
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.dummy import DummyClassifier
from sklearn.metrics import roc_curve, precision_recall_curve
from sklearn.metrics import RocCurveDisplay, PrecisionRecallDisplay


def mypreprocessing(dfx, missing_value=None):
    """
    This function is used to preprocess the dataframe.
    :param dfx: a pandas dataframe containing the input data
    :param missing_value: the value to fill missing values in the dataframe
    :return: a pre-processed pandas dataframe
    """

    # de-duplicate data
    dfx = dfx.drop_duplicates()

    # filling missing values
    if missing_value:
        dfx = dfx.fillna(value=missing_value)

    print(f"data size after pre-processing: {dfx.shape}")
    return dfx


def plot_roc_pr(y_test: pd.Series, y_preds: dict) -> None:
    """
    Plot ROC and PR curves.
    :param y_test: an array or pandas series of true labels
    :param y_preds: a dict containing the predicted probabilities for each model
    :return:
    """

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 3))

    fpr, tpr, _ = roc_curve(y_test, y_preds['automl'])
    roc_auc = sklearn.metrics.auc(fpr, tpr)
    RocCurveDisplay(fpr=fpr, tpr=tpr,
                    roc_auc=roc_auc,
                    estimator_name="AutoMLx").plot(ax=ax1)

    fpr, tpr, _ = roc_curve(y_test, y_preds['most_frequent'])
    roc_auc = sklearn.metrics.auc(fpr, tpr)
    RocCurveDisplay(fpr=fpr, tpr=tpr,
                    roc_auc=roc_auc,
                    estimator_name="most_frequent").plot(ax=ax1)

    ax1.grid()
    ax1.set_title("ROC Curve")

    precision, recall, _ = precision_recall_curve(y_test, y_preds['automl'])
    disp = PrecisionRecallDisplay(precision=precision,
                                  recall=recall,
                                  estimator_name="AutoMLx")
    disp.plot(ax=ax2)

    precision, recall, _ = precision_recall_curve(y_test, y_preds['most_frequent'])
    disp = PrecisionRecallDisplay(precision=precision,
                                  recall=recall,
                                  estimator_name="most_frequent")
    disp.plot(ax=ax2)
    ax2.grid()
    ax2.set_title("Precision-Recall Curve")


def loading_data(**kwargs) -> pd.DataFrame:
    """
    Loads the data from the given path and returns it as a pandas dataframe.
    :param kwargs: keyword arguments containing the path to the data, columns data types, delimiter, target column
    :return: a pandas dataframe containing the data
    """
    if not os.path.exists(kwargs.get('path2csv')):
        raise IOError(f"File {kwargs.get('path2csv')} not found")

    df = pd.read_csv(kwargs.get('path2csv'),
                     dtype=kwargs.get('columns_dtype', None),
                     delimiter=kwargs.get('delimiter', ","))

    missing_cols = [f for f in kwargs.get('columns_dtype', {}) if f not in df]
    if missing_cols:
        raise IOError(f"missing columns: {missing_cols}")

    df[kwargs.get('target')] = (df[kwargs.get('target')] == kwargs.get('churn_value', 1)).astype('uint8')
    print("data size:", df.shape)

    return df


def get_baselines(df_train, df_test, target, columns_dtype):
    """
    Get baseline metrics using the given train and test datasets.

    :param df_train: a pandas dataframe containing the training data
    :param df_test: a pandas dataframe containing the test data
    :param target: a string, target column name
    :param columns_dtype: a dict containing the categorical columns names and types, used for proper encoding.
    :return:
    a dictionary containing the baseline metrics
    a dictionary containing the baseline predictions
    """

    strategies = ["most_frequent", "stratified", "uniform", "LogisticRegression"]
    metrics_list = []
    y_preds = {}

    for st in strategies:
        print(st)
        x_train = df_train.drop([target], axis=1)
        y_train = df_train[target]

        enc = Pipeline(steps=[("encoder", preprocessing.OrdinalEncoder(handle_unknown='use_encoded_value',
                                                                       unknown_value=np.nan)),
                              ("imputer", SimpleImputer(strategy="constant", fill_value=-1))])

        cat_cols = [c for c in columns_dtype if (columns_dtype[c] in ("category") and c in x_train)]
        x_train[cat_cols] = enc.fit_transform(x_train[cat_cols])
        x_train = x_train.fillna(0)
        keep_cols = [c for c in x_train if x_train[c].dtype not in ('O', object)]
        x_train = x_train[keep_cols]

        X_test = df_test.drop([target], axis=1)
        X_test[cat_cols] = enc.transform(X_test[cat_cols])
        X_test = X_test.fillna(0)
        X_test = X_test[keep_cols]
        y_test = df_test[target]

        clf = None
        if st in ("LogisticRegression"):
            clf = LogisticRegression(random_state=0)
        else:
            clf = DummyClassifier(strategy=st)

        clf.fit(X=x_train, y=y_train)
        y_pred = clf.predict(X=X_test).astype("uint8")
        y_preds[st] = y_pred

        metrics = binary_metrics(y_test, y_pred)
        metrics_list.append(metrics)

    metrics_df = pd.DataFrame(metrics_list).T
    metrics_df.columns = strategies

    return metrics_df, y_preds


def binary_metrics(target_col: np.ndarray, pred_col: np.ndarray) -> Dict[str, float]:
    """
    A lightweight version of model performance metrics calculation for binary classification model with probability
    prediction.

    Parameters
    ----------
    target_col, pred_col: numpy arrays containing the ground truth label, and prediction probabilities respectively

    Returns
    -------
    A dict containing the following metrics: mean_target, mean_pred, bias_ratio, AUC, logloss, logloss_reduction
    """
    mean_target = target_col.mean()
    mean_pred = pred_col.mean()
    bias_ratio = mean_pred / mean_target - 1
    logloss = (
        roc_auc
    ) = logloss_redc = accuracy = p = r = t = recall2 = precision2 = best_f1 = float(
        "nan"
    )
    try:
        roc_auc = sklearn.metrics.roc_auc_score(target_col, pred_col)
    except ValueError as e:
        print(f"Failed to calculate roc_auc: {e}")

    try:
        logloss = sklearn.metrics.log_loss(target_col, pred_col)
    except ValueError as e:
        print(f"Failed to calculate logloss: {e}")

    try:
        logloss_baseline = sklearn.metrics.log_loss(
            target_col, np.repeat(mean_target, len(target_col))
        )
        logloss_redc = 1 - logloss / logloss_baseline
    except ValueError as e:
        print(f"Failed to calculate logloss_baseline: {e}")

    try:
        precision, recall, thresh = sklearn.metrics.precision_recall_curve(
            target_col, pred_col
        )
        p, r, t = max(
            zip(precision, recall, thresh),
            key=(
                lambda prt: (
                    0 if max(prt[:2]) <= 0 else 2 * prt[0] * prt[1] / (prt[0] + prt[1])
                )
            ),
        )
    except ValueError as e:
        print(f"Failed to calculate precision-recall curve: {e}")

    try:
        best_f1 = (2 * p * r) / (p + r)
    except ValueError as e:
        print(f"Failed to calculate best_f1: {e}")

    try:
        pred = pred_col > t
    except ValueError as e:
        print(f"Failed to calculate pred: {e}")

    try:
        accuracy = (pred == target_col).mean()
    except ValueError as e:
        print(f"Failed to calculate accuracy: {e}")

    try:
        M = sklearn.metrics.confusion_matrix(target_col, pred)
        recall2 = M[1, 1] / (
                M[1, 1] + M[1, 0]
        )  # = weird-specificity in the lateral problem
        precision2 = M[1, 1] / (
                M[1, 1] + M[0, 1]
        )  # = negative-predicted-value in the lateral problem
    except (ValueError, IndexError) as e:
        print(f"Failed to calculate recall2, precision2: {e}")


    return {
        "mean_target": round(mean_target, 2),
        "mean_pred": round(mean_pred, 2),
        "roc_auc": round(roc_auc, 2),
        "logloss": round(logloss, 2),
        "best_accuracy": round(accuracy, 2),
        "best_precision": round(p, 2),
        "best_recall": round(r, 2),
        "best_thresh": round(t, 2),
        "best_f1": round(best_f1, 2),
    }


def plot_importance(importance: pd.DataFrame,
                    n: int = 10,
                    shap_column: str = "abs_attribution",
                    title: str = "Absolute SHAP values"):
    """
    Plot the global SHAP values for the n important features.

    :param importance: pandas dataframe containing the global SHAP feature importance values
    :param n: number of features to plot the feature importance
    :param shap_column: column name in the dataframe containing the SHAP values
    :param title: title of the plot
    :return:
    """
    fac = max(1, int(n / 10))
    plt.figure(figsize=(10 * fac, 5 * fac))
    x = importance[shap_column].iloc[:n]
    y = range(n, 0, -1)
    y_ticks = importance.feature[:n]
    plt.barh(y, x)

    plt.yticks(range(n, 0, -1), y_ticks)
    plt.tight_layout()
    plt.title(title)



def get_hist_overlap(dfx: pd.DataFrame, col: str, target: str, n: int = 10, path2fig: str = None):
    """
    Plot histogram/barchar of positive/nagative cases for a column in a pandas dataframe

    :param dfx: dataset as a pandas dataframe
    :param col: column name
    :param target: target variable
    :param n: maximum number of bars to plot for a barchart
    :param path2fig: path to save the figure after ploting
    :return:
    """

    cond = dfx[target] == 1
    plt.figure(figsize=(12, 3))
    if str(dfx[col].dtype) in ('object'):
        counts = dfx[cond][col].value_counts()
        x = [c[:30] for c in counts.index[:n]]
        plt.bar(x, counts.values[:n], alpha=0.1, label="churned", color="b", edgecolor='black')
        plt.xticks(rotation=-45)
    else:
        q1, q2 = dfx[cond][col].quantile(.01), dfx[cond][col].quantile(.99)
        dfx[cond][col].hist(range=[q1, q2], alpha=0.1, label="churned", color="b", edgecolor='black')
    # plt.title(f"dist of {col} for positive cases")

    cond = dfx[target] == 0
    if str(dfx[col].dtype) in ('object'):
        counts = dfx[cond][col].value_counts()
        x = [c[:30] for c in counts.index[:n]]
        plt.bar(x, counts.values[:n], alpha=0.3, label="not-churned", color="b", edgecolor='black')
        plt.xticks(rotation=-45)
    else:
        q1, q2 = dfx[cond][col].quantile(.01), dfx[cond][col].quantile(.99)
        dfx[cond][col].hist(range=[q1, q2], alpha=0.3, label="not-churned", color="b", edgecolor='black')
    plt.title(f"dist of {col} for positive/negative cases")
    plt.tight_layout()
    plt.legend()
    if path2fig:
        plt.savefig(path2fig)
    plt.show()
    print("-" * 100)
    print("-" * 100)


def plot_pie_chart(counts: Dict[str, int]) -> None:
    """
    plot pie chart for a dict of label and counts

    :param counts: a dict of {label: count}
    :return:
    """

    labels_dict = {0: "not-churned",
                   1: "churned"}
    labels = [labels_dict[k] for k in counts.keys()]
    sizes = list(counts.values)
    explode = [0.1 * random.random()] * len(sizes)
    fig1, ax1 = plt.subplots()
    ax1.pie(sizes, explode=explode, labels=labels, autopct='%1.1f%%',
            shadow=True, startangle=90)
    ax1.axis('equal')
    plt.show()


def correlation(df: pd.DataFrame, cols: List[str], dpi: int = 100) -> None:
    """
    Plot the correlation heatmap between the columns in the dataframe

    :param df: pandas dataframe
    :param cols: list of column names
    :param dpi: resolution of the plot, default to 100
    :return:
    """

    df_corr = df[cols].corr()
    corr = df_corr.iloc[1:, :-1].copy()
    mask = np.triu(np.ones_like(df_corr, dtype=np.bool))
    mask = mask[1:, :-1]

    fig, ax = plt.subplots(dpi=dpi)
    sns.heatmap(corr,
                mask=mask,
                annot=True, fmt=".2f",
                cmap='coolwarm',
                linewidth=0.3, cbar_kws={"shrink": .8})
    plt.show()
