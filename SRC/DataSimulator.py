import numpy as np
import pandas as pd

class DataSimulator:
    def __init__(self, random_state=None, population=1e6, variance=1000, initial_pharma_stock=1e6, restock_amount=1e6, max_pharma_stock=1e6):
        self.random_state = random_state  # Seed for reproducibility
        self.population = population
        self.variance = variance
        self.initial_pharma_stock = initial_pharma_stock
        self.restock_amount = restock_amount
        self.max_pharma_stock = max_pharma_stock  # Maximum storage capacity

        # Initialize ingredient stocks
        self.ingredient_stocks = {
            'ingredient_a': 4.5e6,
            'ingredient_b': 4.5e6,
            'ingredient_c': 4.5e6
        }

        # Initialize production cycle settings
        self.production_cycle = {
            'ingredient_a': 0.5,  # Reduced units needed per production
            'ingredient_b': 1.5,  # Increased units needed per production
            'ingredient_c': 0.75
        }

        # Initialize state variables
        self.production_increase = False
        self.production_delay = 0

    def simulate_sales_and_stock(self, months_to_simulate=36):
        np.random.seed(self.random_state)  # Set the random seed for reproducibility

        # Define seasonality values for each month (1-10 scale, 5 is default with no change)
        seasonality = {
            'January': 9, 'February': 8, 'March': 7, 'April': 5, 'May': 3, 'June': 3,
            'July': 4, 'August': 4, 'September': 5, 'October': 7, 'November': 8, 'December': 10
        }

        # Prepare lists to store simulation results
        dates = pd.date_range(start='2024-01-01', periods=months_to_simulate, freq='MS')
        total_sales = []
        total_stock = []
        shortage_status = []
        last_restock_amounts = []
        days_since_last_restock = []
        ingredient_a_stock = []
        ingredient_b_stock = []
        ingredient_c_stock = []

        stock = self.initial_pharma_stock  # Start with initial stock

        for month in range(months_to_simulate):
            # Get the month name
            month_name = dates[month].strftime('%B')
            # Simulate seasonal demand variation
            seasonality_factor = (seasonality[month_name] - 5) * 0.02
            seasonal_factor = 1 + seasonality_factor
            monthly_demand = (self.population * 0.006 * 30 * seasonal_factor) + np.random.normal(0, self.variance)
            monthly_demand *= 0.95  # Decrease demand by 5%
            monthly_sales = min(stock, monthly_demand)  # Sales cannot exceed stock
            stock -= monthly_sales  # Update stock after sales

            # Track sales
            total_sales.append(monthly_sales / 1e6)
            total_stock.append(stock / 1e6)

            # Determine shortage status
            if stock < (self.max_pharma_stock * 0.1):  # Extreme shortage threshold
                shortage_status.append(3)  # Extreme shortage
            elif stock < (self.max_pharma_stock * 0.3):  # Moderate shortage threshold
                shortage_status.append(2)  # Moderate shortage
            elif stock < (self.max_pharma_stock * 0.5):  # Minor shortage threshold
                shortage_status.append(1)  # Minor shortage
            else:
                shortage_status.append(0)  # No shortage

            # Handle production and restocking
            if shortage_status[-1] > 0:  # If there's a shortage
                if self.production_delay == 0:
                    self.production_increase = True  # Trigger production increase
                    self.production_delay = np.random.randint(1, 4)  # Set reaction delay of 1-3 months
                else:
                    self.production_delay -= 1  # Decrease the reaction delay counter

            # Production cycle
            if self.production_increase and self.production_delay == 0:
                # Check if enough ingredients are available for production
                can_produce = all(
                    self.ingredient_stocks[ing] >= self.production_cycle[ing] * self.restock_amount
                    for ing in self.production_cycle
                )

                if can_produce:
                    # Deduct ingredient stocks and increase pharmaceutical stock
                    for ingredient, amount in self.production_cycle.items():
                        self.ingredient_stocks[ingredient] -= self.restock_amount * amount

                    stock += self.restock_amount * 1.5  # Increase pharmaceutical stock by 1.5 times the restock amount
                    stock = min(stock, self.max_pharma_stock)  # Ensure stock does not exceed max storage
                    last_restock_amounts.append(self.restock_amount * 1.5 / 1e6)  # Record the amount restocked
                    self.production_increase = False  # Reset production increase trigger after restocking
                else:
                    last_restock_amounts.append(0)  # No production if ingredients are insufficient
            else:
                # Regular restocking outside of shortages
                if month % 6 == 0:  # Restock every 6 months
                    can_produce = all(
                        self.ingredient_stocks[ing] >= self.production_cycle[ing] * self.restock_amount
                        for ing in self.production_cycle
                    )

                    if can_produce:
                        for ingredient, amount in self.production_cycle.items():
                            self.ingredient_stocks[ingredient] -= self.restock_amount * amount

                        stock += self.restock_amount  # Increase pharmaceutical stock by restock amount
                        stock = min(stock, self.max_pharma_stock)  # Ensure stock does not exceed max storage
                        last_restock_amounts.append(self.restock_amount / 1e6)  # Record the amount restocked

                        # Increase restocking for ingredients
                        self.ingredient_stocks['ingredient_a'] += self.restock_amount * 1.0
                        self.ingredient_stocks['ingredient_b'] += self.restock_amount * 3.5  # Increased restock amount for ingredient_b
                        self.ingredient_stocks['ingredient_c'] += self.restock_amount * 1.0
                    else:
                        last_restock_amounts.append(0)  # No production if ingredients are insufficient
                else:
                    last_restock_amounts.append(0)  # No restock happened

            days_since_last_restock.append(30 if last_restock_amounts[-1] > 0 else 0)  # Update days since last restock

            # Track ingredient stocks
            ingredient_a_stock.append(self.ingredient_stocks['ingredient_a'] / 1e6)
            ingredient_b_stock.append(self.ingredient_stocks['ingredient_b'] / 1e6)
            ingredient_c_stock.append(self.ingredient_stocks['ingredient_c'] / 1e6)

        # Create DataFrame with results
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

        # Set display options to show all columns
        pd.set_option('display.max_columns', None)

        # Assuming `df` is your DataFrame
        print(df)