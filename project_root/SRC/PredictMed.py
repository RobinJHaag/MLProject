import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
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

    features = [
        'sales', 'stock', 'last_restock_amount', 'days_since_last_restock',
        'wirkstoff_stock',  # Combined ingredient stock
        'trend', 'seasonal', 'residual'  # Prophet features
    ]
    X_train = training_df[features]
    y_train = training_df['shortage_level']  # Updated goal variable to shortage level
    X_test = testing_df[features]
    y_test = testing_df['shortage_level']

    # Linear Regression
    linear_reg = LinearRegression()
    linear_reg.fit(X_train, y_train)
    y_pred_linear = linear_reg.predict(X_test)
    mse_linear = mean_squared_error(y_test, y_pred_linear)
    print(f'Linear Regression MSE: {mse_linear}')

    # Random Forest
    rf_reg = RandomForestRegressor(random_state=42)
    rf_reg.fit(X_train, y_train)
    y_pred_rf = rf_reg.predict(X_test)
    mse_rf = mean_squared_error(y_test, y_pred_rf)
    print(f'Random Forest Regression MSE: {mse_rf}')

    return y_test, y_pred_linear, y_pred_rf
