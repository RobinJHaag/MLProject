import numpy as np
import pandas as pd


class DataSimulator:
    def __init__(self, random_state=None):
        self.random_state = random_state
        self.initial_pharma_stock = 5000000
        self.max_pharma_stock = 10000000
        self.population = 1000000
        self.variance = 5000
        self.restock_amount = 200000
        self.production_delay = 0
        self.production_increase = False
        self.ingredient_stocks = {
            'ingredient_a': 500000,
            'ingredient_b': 500000,
            'ingredient_c': 500000
        }
        self.production_cycle = {
            'ingredient_a': 1,
            'ingredient_b': 1,
            'ingredient_c': 1
        }

    # Simuliert die Verkaufs- und Lagerbestände eines pharmazeutischen Produkts über mehrere Monate.
    # Berücksichtigt saisonale Schwankungen in der Nachfrage, Lagerbestände, mögliche Engpässe
    # und Produktionszyklen. Die Produktion wird angepasst, wenn der Lagerbestand unter
    # bestimmte Schwellen fällt, wobei die Verfügbarkeit von Zutaten und Produktionsverzögerungen
    # ebenfalls eine Rolle spielen. Engpässe werden überwacht und der Lagerbestand wird semi-regelmässig aufgefüllt.

    def simulate_sales_and_stock(self, months_to_simulate=36):
        np.random.seed(self.random_state)

        seasonality = {
            'January': 9, 'February': 8, 'March': 7, 'April': 5, 'May': 3, 'June': 3,
            'July': 4, 'August': 4, 'September': 5, 'October': 7, 'November': 8, 'December': 10
        }

        dates = pd.date_range(start='2024-01-01', periods=months_to_simulate, freq='MS')
        total_sales = []
        total_stock = []
        shortage_status = []
        last_restock_amounts = []
        days_since_last_restock = []
        ingredient_a_stock = []
        ingredient_b_stock = []
        ingredient_c_stock = []

        stock = self.initial_pharma_stock

        for month in range(months_to_simulate):
            month_name = dates[month].strftime('%B')
            seasonality_factor = (seasonality[month_name] - 5) * 0.02
            seasonal_factor = 1 + seasonality_factor
            monthly_demand = (self.population * 0.003 * 30 * seasonal_factor) + np.random.normal(0, self.variance)
            monthly_demand *= 0.95
            monthly_sales = min(stock, monthly_demand)
            stock -= monthly_sales

            total_sales.append(monthly_sales / 1e6)
            total_stock.append(stock / 1e6)

            if stock < (self.max_pharma_stock * 0.1):
                shortage_status.append(10)
            elif stock < (self.max_pharma_stock * 0.2):
                shortage_status.append(9)
            elif stock < (self.max_pharma_stock * 0.3):
                shortage_status.append(8)
            elif stock < (self.max_pharma_stock * 0.4):
                shortage_status.append(7)
            elif stock < (self.max_pharma_stock * 0.5):
                shortage_status.append(6)
            elif stock < (self.max_pharma_stock * 0.6):
                shortage_status.append(5)
            elif stock < (self.max_pharma_stock * 0.7):
                shortage_status.append(4)
            elif stock < (self.max_pharma_stock * 0.8):
                shortage_status.append(3)
            elif stock < (self.max_pharma_stock * 0.9):
                shortage_status.append(2)
            else:
                shortage_status.append(1)

            if shortage_status[-1] > 1:
                if self.production_delay == 0:
                    self.production_increase = True
                    self.production_delay = np.random.randint(1, 4)
                else:
                    self.production_delay -= 1

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
                if month % 6 == 0:
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

                        # Increase restocking for ingredients
                        self.ingredient_stocks['ingredient_a'] += self.restock_amount * 1.0
                        self.ingredient_stocks['ingredient_b'] += self.restock_amount * 1.0
                        self.ingredient_stocks['ingredient_c'] += self.restock_amount * 1.0
                    else:
                        last_restock_amounts.append(0)
                else:
                    last_restock_amounts.append(0)

            days_since_last_restock.append(30 if last_restock_amounts[-1] > 0 else 0)

            ingredient_a_stock.append(self.ingredient_stocks['ingredient_a'] / 1e6)
            ingredient_b_stock.append(self.ingredient_stocks['ingredient_b'] / 1e6)
            ingredient_c_stock.append(self.ingredient_stocks['ingredient_c'] / 1e6)

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

        pd.set_option('display.max_columns', None)

        print(df)

        return df
