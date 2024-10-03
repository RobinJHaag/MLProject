import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier


class PredictMed:
    def __init__(self, data_simulator):
        """
        Initialisiert PredictMed mit einem DataSimulator.
        :param data_simulator: Eine Instanz des DataSimulators, um Daten zu simulieren.
        """
        self.data_simulator = data_simulator

    def visualize_data(self, df):
        """
        Visualisiert die simulierten Verkaufs- und Lagerbestandsdaten.
        :param df: Der DataFrame mit den simulierten Verkaufs- und Lagerbestandsdaten.
        """
        plt.figure(figsize=(10, 5))
        plt.plot(df['datum'], df['stock'], label='Lagerbestand')
        plt.plot(df['datum'], df['sales'], label='Verkäufe')
        plt.fill_between(df['datum'], 0, df['supply_status'] * df['stock'].max(), color='red', alpha=0.3,
                         label='Knappheitsstufe')
        plt.xlabel('Datum')
        plt.ylabel('Lagerbestand / Verkäufe')
        plt.title('Lagerbestand und Verkaufszahlen für die Schweiz')
        plt.xticks(rotation=45)
        plt.legend()
        plt.tight_layout()
        plt.show()

    def train_model(self, df):
        """
        Trainiert ein Modell zur Vorhersage der Knappheitsstufen.
        :param df: Der DataFrame mit den simulierten Daten.
        :return: Das trainierte Modell.
        """
        # Features und Zielvariable festlegen
        X = df[['sales', 'stock', 'day_of_week', 'month', 'days_since_last_restock']]
        y = df['supply_status']

        # Aufteilen in Trainings- und Testdaten
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        # Trainiere ein RandomForest-Modell zur Vorhersage der Knappheitsstufen
        model = RandomForestClassifier()
        model.fit(X_train, y_train)

        # Bewertung des Modells
        score = model.score(X_test, y_test)
        print(f"Modellbewertung (Genauigkeit): {score}")
        return model
