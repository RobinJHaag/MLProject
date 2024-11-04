import numpy as np
import pandas as pd


class DataSimulator:
    def __init__(self, random_state=None, restock_interval=3, base_restock_amount=500000):
        self.random_state = random_state
        self.initial_pharma_stock = 5000000
        self.max_pharma_stock = 10000000
        self.population = 1000000
        self.variance = 100000  # Variability for demand and sales
        self.base_restock_amount = base_restock_amount
        self.restock_interval = restock_interval
        self.scaled_production_active = False
        self.scaled_production_multiplier = 1
        self.production_ramp_up_delay = 2  # Delay before ramping up production after a shortage
        self.ingredient_stocks = {
            'ingredient_a': 5000000,
            'ingredient_b': 5000000,
            'ingredient_c': 5000000
        }
        self.production_cycle = {
            'ingredient_a': 1,
            'ingredient_b': 1,
            'ingredient_c': 1
        }
        self.ingredient_restock_rate = 120000  # Slightly boosted restock rate
        self.boost_ingredient_restock = False
        self.boost_duration = 3  # Duration for restocking boost after a shortage
        self.boost_counter = 0
        self.ingredient_ramp_up_delay = 4  # 3-month delay for ingredient restocking ramp-up

        self.ingredient_restock_delays = {
            'ingredient_a': -1,
            'ingredient_b': -1,
            'ingredient_c': -1
        }

    def can_produce(self, restock_amount):
        """
        Checks if there are enough ingredients available to produce the required restock amount.
        """
        return all(
            self.ingredient_stocks[ing] >= self.production_cycle[ing] * restock_amount
            for ing in self.production_cycle
        )

    def simulate_sales_and_stock(self, months_to_simulate=36):
        """
        Simulates sales and stock over a specified period.
        Sales amounts vary based on seasonality and random demand spikes.
        """
        np.random.seed(self.random_state)

        seasonality = {
            'January': 9, 'February': 8, 'March': 7, 'April': 5, 'May': 2, 'June': 2,
            'July': 3, 'August': 4, 'September': 5, 'October': 7, 'November': 8, 'December': 10
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
        restock_amount = self.base_restock_amount
        last_restock_time = 0

        for month in range(months_to_simulate):
            """
            Calculates monthly demand based on seasonality and randomness.
            There’s a 30% chance for a demand spike, doubling sales.
            """
            month_name = dates[month].strftime('%B')
            seasonality_factor = (seasonality[month_name] - 5) * 0.1
            seasonal_factor = 1 + seasonality_factor
            monthly_demand = (self.population * 0.005 * 30 * seasonal_factor) + np.random.normal(0, self.variance)
            monthly_demand = max(0, monthly_demand)
            if np.random.random() < 0.3:
                monthly_demand *= 2
            monthly_sales = min(stock, monthly_demand)
            stock -= monthly_sales

            total_sales.append(monthly_sales / 1e6)
            total_stock.append(stock / 1e6)

            """
            Determines the shortage status on a 1-10 scale based on current stock levels
            and sales volume. This controls whether production will ramp up.
            """
            if stock < self.max_pharma_stock * 0.1:
                if monthly_sales > self.max_pharma_stock * 0.1:
                    shortage_status.append(10)
                else:
                    shortage_status.append(9)
            elif stock < self.max_pharma_stock * 0.2:
                shortage_status.append(7 if monthly_sales > self.max_pharma_stock * 0.2 else 8)
            elif stock < self.max_pharma_stock * 0.3:
                shortage_status.append(5 if monthly_sales > self.max_pharma_stock * 0.3 else 6)
            elif stock < self.max_pharma_stock * 0.5:
                shortage_status.append(3 if monthly_sales > self.max_pharma_stock * 0.5 else 4)
            else:
                shortage_status.append(1 if stock >= self.max_pharma_stock * 0.6 else 2)

            """
            Introduces random delays in restocking ingredients (10% probability).
            When a delay occurs, the ingredient is restocked more slowly until the delay ends.
            """
            for ingredient in self.ingredient_stocks:
                if np.random.random() < 0.1:
                    print(f"Warning: Restocking failure for {ingredient} in {month_name} {dates[month].year}!")
                    self.ingredient_stocks[ingredient] -= self.ingredient_restock_rate * np.random.uniform(0.4, 0.9)
                    self.ingredient_restock_delays[ingredient] = month + self.ingredient_ramp_up_delay
                else:
                    if month >= self.ingredient_restock_delays[ingredient]:
                        print(f"Boosting {ingredient} restocking after shortage in {month_name} {dates[month].year}!")
                        self.ingredient_stocks[ingredient] += self.ingredient_restock_rate * np.random.uniform(1.0, 1.5)
                    else:
                        self.ingredient_stocks[ingredient] += self.ingredient_restock_rate * np.random.uniform(0.5, 1.0)

            """
            Regular restocking at fixed intervals, if enough ingredients are available.
            Otherwise, tracks the interval since the last restock.
            """
            if month % self.restock_interval == 0 and self.can_produce(restock_amount):
                stock += restock_amount
                self.ingredient_stocks['ingredient_a'] -= restock_amount * self.production_cycle['ingredient_a']
                self.ingredient_stocks['ingredient_b'] -= restock_amount * self.production_cycle['ingredient_b']
                self.ingredient_stocks['ingredient_c'] -= restock_amount * self.production_cycle['ingredient_c']
                last_restock_amounts.append(restock_amount / 1e6)
                days_since_last_restock.append(0)
                last_restock_time = month
            else:
                last_restock_amounts.append(0)
                days_since_last_restock.append(month - last_restock_time)

            """
            Ramping up production during shortages (starting from level 7). This happens after a delay
            before production is increased.
            """
            if shortage_status[-1] >= 7 and not self.scaled_production_active:
                if month - last_restock_time >= self.production_ramp_up_delay:
                    self.scaled_production_active = True
                    self.scaled_production_multiplier = 4

            if self.scaled_production_active and shortage_status[-1] < 7:
                self.scaled_production_active = False
                self.scaled_production_multiplier = 1

            if self.scaled_production_active and self.can_produce(restock_amount * self.scaled_production_multiplier):
                stock += restock_amount * self.scaled_production_multiplier
                self.ingredient_stocks['ingredient_a'] -= restock_amount * self.production_cycle['ingredient_a'] * self.scaled_production_multiplier
                self.ingredient_stocks['ingredient_b'] -= restock_amount * self.production_cycle['ingredient_b'] * self.scaled_production_multiplier
                self.ingredient_stocks['ingredient_c'] -= restock_amount * self.production_cycle['ingredient_c'] * self.scaled_production_multiplier
                last_restock_time = month

            ingredient_a_stock.append(self.ingredient_stocks['ingredient_a'] / 1e6)
            ingredient_b_stock.append(self.ingredient_stocks['ingredient_b'] / 1e6)
            ingredient_c_stock.append(self.ingredient_stocks['ingredient_c'] / 1e6)

        # Structured DataFrame with all relevant information side by side
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

        return df
