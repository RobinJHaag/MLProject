import numpy as np
import pandas as pd

class DataSimulator:
    def __init__(self, population=8.5, initial_stock=5.0, restock_amount=3.0, variance=0.1, random_state=42):
        """
        Simuliert monatliche Verkaufszahlen, Lagerbestände und Knappheitsstufen für eine zentrale Lagerstelle.
        :param population: Bevölkerung in Millionen
        :param initial_stock: Startlagerbestand in Millionen
        :param restock_amount: Standard-Nachschubmenge in Millionen
        :param variance: Schwankungen in den Verkaufszahlen
        :param random_state: Seed für die Reproduzierbarkeit
        """
        self.population = population * 1e6  # Bevölkerungsgröße
        self.initial_stock = initial_stock * 1e6  # Initialer Lagerbestand in echten Zahlen
        self.restock_amount = restock_amount * 1e6  # Nachschub in echten Zahlen
        self.variance = variance
        self.random_state = random_state
        self.increased_production_next_month = False  # Flag zur Erhöhung der Produktion nach einer Knappheit

    def simulate_sales_and_stock(self, months_to_simulate=12):
        """
        Simuliert monatliche Verkaufszahlen, Lagerbestand und mehrstufige Klassifikationsstufen für eine zentrale Lagerstelle.
        :param months_to_simulate: Anzahl der zu simulierenden Monate.
        :return: Ein DataFrame mit Datum, Verkaufszahlen, Lagerbestand und Knappheitsstufen.
        """
        np.random.seed(self.random_state)

        # Simuliere den monatlichen Bedarf basierend auf der Bevölkerung
        monthly_demand_per_person = 0.007 * 30  # 0.7% der Bevölkerung braucht monatlich Hustensaft
        total_monthly_demand = self.population * monthly_demand_per_person

        # Initialisiere Listen für Verkäufe, Lagerbestand und Daten
        total_sales = []
        total_stock = []
        stock = self.initial_stock  # Initialer Lagerbestand

        # Erstelle Monatsdaten
        dates = pd.date_range(start='2024-01-01', periods=months_to_simulate, freq='M')

        # Zielvariable: 0 = Keine Knappheit, 1 = Moderate Knappheit, 2 = Extreme Knappheit
        supply_status = []

        for month in range(1, months_to_simulate + 1):
            current_month = dates[month - 1].month
            seasonality_factor = 1.0
            restock_multiplier = 1.0

            # Erhöhte Nachfrage und reduzierter Nachschub im Winter
            if current_month in [11, 12, 1, 2]:  # Winter-Saison
                seasonality_factor = 2.5  # Stärkere Nachfrage im Winter
                restock_multiplier = 0.8  # Leicht reduzierter Nachschub im Winter
            else:
                restock_multiplier = 0.6  # Stärker reduzierter Nachschub im Sommer

            # Erhöhte Produktion nach Knappheit im letzten Monat
            if self.increased_production_next_month:
                restock_multiplier += 0.5  # Produktion wird um 50% erhöht nach einer Knappheit
                self.increased_production_next_month = False  # Zurücksetzen des Flags

            # Simuliere monatliche Verkaufszahlen mit Schwankungen
            monthly_sales = max(0, total_monthly_demand * seasonality_factor + np.random.normal(0, self.variance * total_monthly_demand))
            total_sales.append(monthly_sales / 1e6)  # Verkäufe in Millionen darstellen

            # Reduziere den Lagerbestand
            stock = max(0, stock - monthly_sales)
            total_stock.append(stock / 1e6)  # Lagerbestand in Millionen darstellen

            # Bestimme die Knappheit basierend auf dem verbleibenden Lagerbestand
            if stock < total_monthly_demand * 0.1:  # Extreme Knappheit
                supply_status.append(2)
                self.increased_production_next_month = True  # Markiere den nächsten Monat für erhöhte Produktion
            elif stock < total_monthly_demand * 0.3:  # Moderate Knappheit
                supply_status.append(1)
                self.increased_production_next_month = True  # Markiere den nächsten Monat für erhöhte Produktion
            else:  # Keine Knappheit
                supply_status.append(0)

            # Variabler Nachschub, aber mit Reaktion auf Knappheit
            restock = self.restock_amount * restock_multiplier * np.random.uniform(0.5, 0.8)
            stock += restock

            print(f"Monat {month}:")
            print(f"  Verkauf: {monthly_sales / 1e6:.1f} Mio, Lagerbestand nach Verkauf: {stock / 1e6:.1f} Mio")
            print(f"  Nachschub: {restock / 1e6:.1f} Mio, Lagerbestand nach Nachschub: {stock / 1e6:.1f} Mio")

        # Erstelle einen DataFrame aus den simulierten Daten
        df = pd.DataFrame({
            'datum': dates,
            'sales': total_sales,
            'stock': total_stock,
            'supply_status': supply_status
        })

        # Setze die Ausgabe so, dass sie nicht in wissenschaftlicher Notation erscheint
        pd.options.display.float_format = '{:.1f}'.format  # Zeige die Werte mit einer Nachkommastelle an

        return df
