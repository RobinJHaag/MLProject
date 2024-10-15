from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error


def train_and_evaluate_models(df):
    # Bereite die Merkmalsmatrix und den Zielvektor vor
    X = df[['sales', 'stock', 'shortage_status', 'ingredient_a_stock', 'ingredient_b_stock', 'ingredient_c_stock']]
    y = df['last_restock_amount']

    # Teile die Daten in Trainings- und Testsets auf
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Trainiere ein lineares Regressionsmodell
    linear_model = LinearRegression()
    linear_model.fit(X_train, y_train)
    y_pred_linear = linear_model.predict(X_test)

    # Trainiere ein Random Forest Regressor Modell
    rf_model = RandomForestRegressor(random_state=42)
    rf_model.fit(X_train, y_train)
    y_pred_rf = rf_model.predict(X_test)

    # Drucke den Mean Squared Error für beide Modelle
    print(f"Linear Regression MSE: {mean_squared_error(y_test, y_pred_linear)}")
    print(f"Random Forest Regression MSE: {mean_squared_error(y_test, y_pred_rf)}")

    # Rückgabe der tatsächlichen und vorhergesagten Werte für beide Modelle
    return y_test, y_pred_linear, y_pred_rf
