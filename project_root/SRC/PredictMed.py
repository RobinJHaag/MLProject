from sklearn.model_selection import GridSearchCV, TimeSeriesSplit
from sklearn.linear_model import LinearRegression
from sklearn.svm import SVR
from xgboost import XGBRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error
from DB_Setup import TrainingSimulationData, TestingSimulationData


def evaluate_model(testing_df, features, scaler, model, months):
    """
    Evaluate the model for a specific number of months.
    """
    # Filter data for the specified time horizon
    X_test = testing_df[features].iloc[:months]
    y_test = testing_df['shortage_level'].iloc[:months]

    # Normalize the test data (matching the training scaling)
    X_test_scaled = scaler.transform(X_test)

    # Predict shortage levels
    y_pred = model.predict(X_test_scaled)

    # Calculate Mean Squared Error (MSE)
    mse = mean_squared_error(y_test, y_pred)
    return mse


def rolling_forecast_origin(db_manager, model, features, scaler, n_splits=5):
    """
    Perform Rolling Forecast Origin (RFO) validation.
    """
    # Load data directly from the database
    training_df = db_manager.load_simulation_data(TrainingSimulationData)
    testing_df = db_manager.load_simulation_data(TestingSimulationData)

    # Separate features and target variable for training
    X_train = training_df[features]
    y_train = training_df['shortage_level']

    # Normalize / Standardize features for models requiring scaling
    X_train_scaled = scaler.transform(X_train)

    # Initialize TimeSeriesSplit
    tscv = TimeSeriesSplit(n_splits=n_splits)

    rfo_scores = []

    for train_index, test_index in tscv.split(X_train_scaled):
        X_train_fold, X_test_fold = X_train_scaled[train_index], X_train_scaled[test_index]
        y_train_fold, y_test_fold = y_train[train_index], y_train[test_index]

        # Train the model on the training fold
        model.fit(X_train_fold, y_train_fold)

        # Predict on the test fold
        y_pred_fold = model.predict(X_test_fold)

        # Calculate MSE for the test fold
        mse_fold = mean_squared_error(y_test_fold, y_pred_fold)
        rfo_scores.append(mse_fold)

    # Calculate average MSE over all folds
    average_mse = sum(rfo_scores) / len(rfo_scores)
    return average_mse


def train_and_evaluate_models_monthly(db_manager):
    """
    Train on the training dataset and evaluate the testing dataset over 3, 6, 12 months.
    """
    # Load data directly from the database
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

    # Model Definitions
    models = {
        "Linear Regression": LinearRegression(),
        "XGBoost": XGBRegressor(),
        "SVM": SVR()
    }

    # Updated Hyperparameter grids
    param_grids = {
        "Linear Regression": {
            "fit_intercept": [True, False]
        },
        "XGBoost": {
            "n_estimators": [100, 200, 300],
            "learning_rate": [0.01, 0.1, 0.2],
            "max_depth": [3, 4, 5],
            "subsample": [0.8, 1.0],
            "colsample_bytree": [0.8, 1.0],
            "alpha": [0.5, 1, 5],
            "lambda": [2, 5, 10],
            "gamma": [0, 0.1, 0.5]
        },
        "SVM": {
            "C": [0.01, 0.1, 1],
            "epsilon": [0.01, 0.1, 0.5],
            "kernel": ['linear', 'rbf'],
            "gamma": ['scale', 0.1, 0.01]
        }
    }

    mse_scores = {}

    # GridSearch for the best model
    for model_name, model in models.items():
        print(f"Tuning {model_name}...")
        param_grid = param_grids[model_name]

        # TimeSeriesSplit for Rolling Forecast Origin
        tscv = TimeSeriesSplit(n_splits=5)
        grid_search = GridSearchCV(model, param_grid, cv=tscv, n_jobs=-1, scoring='neg_mean_squared_error')
        grid_search.fit(X_train_scaled, y_train)

        print(f"Best parameters for {model_name}: {grid_search.best_params_}")
        best_model = grid_search.best_estimator_

        # Evaluate on different time horizons
        mse_3 = evaluate_model(testing_df, features, scaler, best_model, months=3)
        mse_6 = evaluate_model(testing_df, features, scaler, best_model, months=6)
        mse_12 = evaluate_model(testing_df, features, scaler, best_model, months=12)

        # Perform Rolling Forecast Origin (RFO) validation
        rfo_mse = rolling_forecast_origin(db_manager, best_model, features, scaler)

        # Save model and MSEs in the scores dictionary
        mse_scores[model_name] = {
            "model": best_model,
            "mse_3": mse_3,
            "mse_6": mse_6,
            "mse_12": mse_12,
            "rfo_mse": rfo_mse
        }

    return mse_scores
