```python
import numpy as np
import pandas as pd

class DataSimulator:
    def __init__(self, random_state=None):
        # Initialisiere den Simulator mit Standardwerten
        self.random_state = random_state
        np.random.seed(self.random_state)
        self.production_delay = 0
        self.production_increase = False
        self.restock_amount = 1000
        self.max_pharma_stock = 10000
        self.ingredient_stocks = {
            'ingredient_a': 5000,
            'ingredient_b': 5000,
            'ingredient_c': 5000
        }
        self.production_cycle = {
            'ingredient_a': 1,
            'ingredient_b': 1,
            'ingredient_c': 1
        }

    def simulate_sales_and_stock(self, months_to_simulate):
        # Erzeuge Datumsbereich und zufällige Verkaufs-, Lager- und Engpassstatusdaten
        dates = pd.date_range(start='2020-01-01', periods=months_to_simulate, freq='M')
        total_sales = np.random.randint(500, 1500, size=months_to_simulate)
        total_stock = np.random.randint(1000, 5000, size=months_to_simulate)
        shortage_status = np.random.randint(0, 3, size=months_to_simulate)
        last_restock_amounts = []
        days_since_last_restock = []
        ingredient_a_stock = []
        ingredient_b_stock = []
        ingredient_c_stock = []

        stock = 0
        restock_counter = np.random.randint(6, 10)  # Initialer Nachschub-Countdown

        for month in range(months_to_simulate):
            # Produktions- und Nachschubverwaltung bei Engpässen
            if shortage_status[month] > 1:
                if self.production_delay == 0:
                    self.production_increase = True
                    self.production_delay = np.random.randint(1, 4)
                else:
                    self.production_delay -= 1

            # Produktionszyklus bei Engpässen
            if self.production_increase and self.production_delay == 0:
                can_produce = all(
                    self.ingredient_stocks[ing] >= self.production_cycle[ing] * self.restock_amount
                    for ing in self.production_cycle
                )

                if can_produce:
                    for ingredient, amount in self.production_cycle.items():
                        self.ingredient_stocks[ingredient] -= self.restock_amount * amount

                    stock += self.restock_amount * 1.5
                    stock = min(stock, self.max_pharma_stock)
                    last_restock_amounts.append(self.restock_amount * 1.5 / 1e6)
                    self.production_increase = False
                else:
                    last_restock_amounts.append(0)
            else:
                # Zufälliger Nachschub alle 6-9 Monate
                if restock_counter == 0:
                    can_produce = all(
                        self.ingredient_stocks[ing] >= self.production_cycle[ing] * self.restock_amount
                        for ing in self.production_cycle
                    )

                    if can_produce:
                        for ingredient, amount in self.production_cycle.items():
                            self.ingredient_stocks[ingredient] -= self.restock_amount * amount

                        stock += self.restock_amount
                        stock = min(stock, self.max_pharma_stock)
                        last_restock_amounts.append(self.restock_amount / 1e6)

                        self.ingredient_stocks['ingredient_a'] += self.restock_amount * 1.0
                        self.ingredient_stocks['ingredient_b'] += self.restock_amount * 1.0
                        self.ingredient_stocks['ingredient_c'] += self.restock_amount * 1.0
                    else:
                        last_restock_amounts.append(0)

                    restock_counter = np.random.randint(6, 10)  # Setze den Nachschub-Countdown zurück
                else:
                    last_restock_amounts.append(0)
                    restock_counter -= 1

            days_since_last_restock.append(30 if last_restock_amounts[-1] > 0 else 0)

            ingredient_a_stock.append(self.ingredient_stocks['ingredient_a'] / 1e6)
            ingredient_b_stock.append(self.ingredient_stocks['ingredient_b'] / 1e6)
            ingredient_c_stock.append(self.ingredient_stocks['ingredient_c'] / 1e6)

        # Erstelle DataFrame mit den Ergebnissen
        df = pd.DataFrame({
            'date': dates,
            'sales': total_sales,
            'stock': total_stock,
            'shortage_status': shortage_status,
            'last_restock_amount': last_restock_amounts,
            'days_since_last_restock': days_since_last_restock,
            'ingredient_a_stock': ingredient_a_stock,
            'ingredient_b_stock': ingredient_b_stock,
            'ingredient_c_stock': ingredient_c_stock
        })

        # Setze Anzeigeoptionen, um alle Spalten anzuzeigen, und drucke das DataFrame
        pd.set_option('display.max_columns', None)
        print(df)

        # Rückgabe des DataFrames
        return df