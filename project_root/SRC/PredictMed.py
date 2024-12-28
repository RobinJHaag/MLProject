import pandas as pd
import numpy as np
from sklearn.model_selection import GridSearchCV
from sklearn.linear_model import LinearRegression
from sklearn.svm import SVR
from xgboost import XGBRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error
from DB_Setup import TrainingSimulationData, TestingSimulationData


def evaluate_rolling_forecast(testing_df, features, scaler, model, steps=12):
    """
    Evaluate the model using a rolling forecast for the next `steps` months.
    """
    mse_list = []
    X_test = testing_df[features]
    y_test = testing_df['shortage_level']

    for i in range(steps):
        # Ensure we don't exceed available test data
        if i >= len(X_test):
            break

        # Scale the current test row
        X_test_scaled = scaler.transform(pd.DataFrame([X_test.iloc[i]], columns=features))
        y_pred = model.predict(X_test_scaled)[0]

        # Get the actual value and calculate MSE for this step
        y_actual = y_test.iloc[i]
        mse = (y_actual - y_pred) ** 2
        mse_list.append(mse)

    # Calculate average MSE over all steps
    avg_mse = np.mean(mse_list)
    return avg_mse, mse_list


def train_and_evaluate_rolling_forecast(db_manager):
    """
    Train models and evaluate their rolling forecast performance over 12 months with hyperparameter tuning.
    """
    # Load data from the database
    training_df = db_manager.load_simulation_data(TrainingSimulationData)
    testing_df = db_manager.load_simulation_data(TestingSimulationData)

    # Feature set
    features = [
        'sales', 'stock', 'last_restock_amount', 'days_since_last_restock',
        'wirkstoff_stock', 'trend', 'seasonal',
    ]

    # Separate features and target variable for training
    X_train = training_df[features]
    y_train = training_df['shortage_level']

    # Normalize / Standardize features for models requiring scaling
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)

    # Define hyperparameter grids for each model
    param_grids = {
        "Linear Regression": {
            "fit_intercept": [True, False]
        },
        "XGBoost": {
            "n_estimators": [50, 100, 200],
            "learning_rate": [0.01, 0.1, 0.2],
            "max_depth": [3, 5, 7],
            "subsample": [0.8, 1.0],
        },
        "SVM": {
            "C": [0.1, 1, 10],
            "epsilon": [0.01, 0.1, 0.5],
            "kernel": ["linear", "rbf"],
        },
    }

    rolling_steps = 12  # Number of months to forecast
    mse_scores = {}

    for model_name, model in {"Linear Regression": LinearRegression(), "XGBoost": XGBRegressor(), "SVM": SVR()}.items():
        print(f"Tuning {model_name}...")
        param_grid = param_grids[model_name]
        grid_search = GridSearchCV(model, param_grid, cv=3, scoring="neg_mean_squared_error", n_jobs=-1)
        grid_search.fit(X_train_scaled, y_train)

        print(f"Best parameters for {model_name}: {grid_search.best_params_}")
        best_model = grid_search.best_estimator_

        print(f"Training {model_name} with best parameters...")
        avg_mse, mse_list = evaluate_rolling_forecast(testing_df, features, scaler, best_model, steps=rolling_steps)
        mse_scores[model_name] = {
            "average_mse": avg_mse,
            "mse_list": mse_list
        }

    return mse_scores
