import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error


def train_and_evaluate_models(df):
    from sklearn.model_selection import train_test_split
    from sklearn.linear_model import LinearRegression
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.metrics import mean_squared_error

    # Define features and target variable
    X = df[['sales', 'stock', 'last_restock_amount', 'days_since_last_restock', 'ingredient_a_stock', 'ingredient_b_stock', 'ingredient_c_stock']]
    y = df['shortage_status']

    # Split data into training and test sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Train Linear Regression
    linear_reg = LinearRegression()
    linear_reg.fit(X_train, y_train)
    y_pred_linear = linear_reg.predict(X_test)
    mse_linear = mean_squared_error(y_test, y_pred_linear)
    print(f'Linear Regression MSE: {mse_linear}')

    # Train Random Forest Regression
    rf_reg = RandomForestRegressor(random_state=42)
    rf_reg.fit(X_train, y_train)
    y_pred_rf = rf_reg.predict(X_test)
    mse_rf = mean_squared_error(y_test, y_pred_rf)
    print(f'Random Forest Regression MSE: {mse_rf}')

    return y_test, y_pred_linear, y_pred_rf
