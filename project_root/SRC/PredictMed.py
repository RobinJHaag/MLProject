import pandas as pd
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.svm import SVR
from xgboost import XGBRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error
from DB_Setup import TrainingSimulationData, TestingSimulationData  # Assuming the correct imports for the tables
from DB import DatabaseManager


def train_and_evaluate_models(db_manager):
    """
    Train on the training dataset and evaluate on the testing dataset.
    """
    # Load data directly from the database
    training_df = db_manager.load_simulation_data(TrainingSimulationData)
    testing_df = db_manager.load_simulation_data(TestingSimulationData)

    # Feature set
    features = [
        'sales', 'stock', 'last_restock_amount', 'days_since_last_restock',
        'wirkstoff_stock',  # Combined ingredient stock
        'trend', 'seasonal', 'residual'  # Prophet features
    ]

    # Separating features and target variable
    X_train = training_df[features]
    y_train = training_df['shortage_level']
    X_test = testing_df[features]
    y_test = testing_df['shortage_level']

    # Normalization / Standardization for Linear Regression and SVM
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # Model Definitions
    models = {
        "Linear Regression": LinearRegression(),
        "XGBoost": XGBRegressor(),
        "SVM": SVR()
    }

    # Hyperparameter grids
    param_grids = {
        "Linear Regression": {
            "fit_intercept": [True, False]
        },
        "XGBoost": {
            "n_estimators": [100, 200, 500],
            "learning_rate": [0.01, 0.1, 0.3],
            "max_depth": [3, 6, 10],
            "subsample": [0.7, 0.8, 1.0],
            "colsample_bytree": [0.7, 0.8, 1.0]
        },
        "SVM": {
            "C": [0.1, 1, 10],
            "epsilon": [0.01, 0.1, 0.5],
            "kernel": ['linear', 'rbf'],
            "gamma": ['scale', 'auto', 0.1]
        }
    }

    # GridSearch for each model
    for model_name in models:
        print(f"Tuning {model_name}...")

        model = models[model_name]
        param_grid = param_grids[model_name]

        grid_search = GridSearchCV(model, param_grid, cv=5, n_jobs=-1, scoring='neg_mean_squared_error')
        grid_search.fit(X_train_scaled, y_train)

        print(f"Best parameters for {model_name}: {grid_search.best_params_}")

        # Best model
        best_model = grid_search.best_estimator_

        # Prediction
        y_pred = best_model.predict(X_test_scaled)
        mse = mean_squared_error(y_test, y_pred)
        print(f"{model_name} MSE: {mse}")

    return grid_search.best_params_
