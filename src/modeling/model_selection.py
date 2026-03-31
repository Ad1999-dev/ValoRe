import numpy as np
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LinearRegression
from sklearn.metrics import make_scorer, mean_squared_error
from sklearn.model_selection import GridSearchCV, KFold
from sklearn.neighbors import KNeighborsRegressor
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from xgboost import XGBRegressor


DEFAULT_PARAM_GRIDS = {
    "dummy": {
        "model__strategy": ["mean", "median"],
    },
    "linear_regression": {},
    "knn": {
        "model__n_neighbors": [5, 9, 15],
        "model__weights": ["uniform", "distance"],
    },
    "random_forest": {
        "model__n_estimators": [300, 500],
        "model__max_depth": [None, 10, 20],
        "model__min_samples_leaf": [1, 2],
    },
    "xgboost": {
        "model__n_estimators": [300, 500],
        "model__learning_rate": [0.05, 0.1, 0.2],
        "model__max_depth": [4, 6, 8],
    },
}


def rmse(y_true, y_pred):
    return float(np.sqrt(mean_squared_error(y_true, y_pred)))


RMSE_SCORER = make_scorer(rmse, greater_is_better=False)


def build_preprocess(X):
    """
    Build the preprocessing block used for the current project.
    For now we only keep numeric columns, which is consistent
    with the milestone 1 setup.
    """
    numeric_cols = X.select_dtypes(include=[np.number]).columns.tolist()

    numeric_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )

    preprocess = ColumnTransformer(
        transformers=[
            ("num", numeric_pipeline, numeric_cols),
        ],
        remainder="drop",
    )

    return preprocess, numeric_cols


def build_model(model_name, random_state=42):
    """
    Return one model object based on the chosen name.
    """
    model_name = model_name.lower()

    if model_name == "dummy":
        return DummyRegressor()

    if model_name == "linear_regression":
        return LinearRegression()

    if model_name == "knn":
        return KNeighborsRegressor()

    if model_name == "random_forest":
        return RandomForestRegressor(
            random_state=random_state,
            n_jobs=-1,
        )

    if model_name == "xgboost":
        return XGBRegressor(
            objective="reg:squarederror",
            random_state=random_state,
            n_jobs=-1,
        )

    raise ValueError("Unsupported model_name: {}".format(model_name))


def run_grid_search(
    train_df,
    target_col,
    model_name="xgboost",
    random_state=42,
    cv_folds=5,
    param_grid=None,
):
    """
    Run GridSearchCV on the chosen model using the train dataframe.
    """
    if target_col not in train_df.columns:
        raise ValueError("Target column '{}' not found in train_df".format(target_col))

    X_train = train_df.drop(columns=[target_col])
    y_train = train_df[target_col]

    preprocess, kept_columns = build_preprocess(X_train)
    X_train = X_train[kept_columns]

    model = build_model(model_name=model_name, random_state=random_state)

    pipe = Pipeline(
        steps=[
            ("preprocess", preprocess),
            ("model", model),
        ]
    )

    if param_grid is None:
        param_grid = DEFAULT_PARAM_GRIDS.get(model_name, {})

    if not param_grid:
        pipe.fit(X_train, y_train)
        return {
            "best_estimator": pipe,
            "best_params": {},
            "best_cv_rmse": None,
            "kept_columns": kept_columns,
            "cv_results": None,
        }

    cv = KFold(
        n_splits=cv_folds,
        shuffle=True,
        random_state=random_state,
    )

    search = GridSearchCV(
        estimator=pipe,
        param_grid=param_grid,
        scoring=RMSE_SCORER,
        cv=cv,
        n_jobs=-1,
        verbose=1,
        return_train_score=False,
    )

    search.fit(X_train, y_train)

    return {
        "best_estimator": search.best_estimator_,
        "best_params": search.best_params_,
        "best_cv_rmse": float(-search.best_score_),
        "kept_columns": kept_columns,
        "cv_results": search.cv_results_,
    }