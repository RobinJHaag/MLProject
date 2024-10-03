from DataSimulator import DataSimulator
from PredictMed import PredictMed


def main():
    # Erstelle den DataSimulator für die zentrale Lagerstelle
    data_simulator = DataSimulator(population=8500000, initial_stock=5000000, restock_amount=5000000, variance=0.2)

    # Simuliere monatliche Verkaufszahlen, Lagerbestände und Knappheitsstufen
    df_aggregated = data_simulator.simulate_sales_and_stock(months_to_simulate=12)

    # Ausgabe der simulierten und aggregierten Daten
    print(df_aggregated.head(12))  # Zeige die ersten 12 Monate


if __name__ == "__main__":
    main()
