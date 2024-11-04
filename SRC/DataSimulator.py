import numpy as np
import pandas as pd


class DataSimulator:
    def __init__(self, random_state=None, restock_interval=3, base_restock_amount=550000):
        self.random_state = random_state
        self.initial_pharma_stock = 5000000
        self.max_pharma_stock = 10000000
        self.population = 1000000
        self.variance = 100000  # Variability for demand and sales
        self.base_restock_amount = base_restock_amount
        self.restock_interval = restock_interval
        self.scaled_production_active = False
        self.scaled_production_multiplier = 1
        self.production_ramp_up_delay = 3  # Delay before ramping up production after a shortage

        # Single ingredient setup
        self.wirkstoff_stock = 5000000
        self.production_cycle = 1
        self.wirkstoff_restock_rate = 120000  # Restock rate for Wirkstoff
        self.wirkstoff_ramp_up_delay = 3  # Delay for restocking ramp-up

        self.wirkstoff_restock_delay = -1

    def can_produce(self, restock_amount):
        """
        Checks if there is enough Wirkstoff available to produce the required restock amount.
        """
        return self.wirkstoff_stock >= self.production_cycle * restock_amount

    def simulate_sales_and_stock(self, months_to_simulate=48):
        """
        Simulates sales and stock over a specified period.
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
        wirkstoff_stock_over_time = []
        demand_spike_indicator = []
        rolling_variance_sales = []
        avg_monthly_sales_6m = []
        shortage_status_lag_2m = []
        stock_to_demand_ratio = []
        cumulative_restock_6m = []
        restocking_failure_count_6m = []
        production_ramp_up_status = []
        time_since_last_shortage_event = []

        restocking_failure_history = []
        last_shortage_event = -1  # Initialize with -1 to indicate no shortage has occurred yet

        stock = self.initial_pharma_stock
        restock_amount = self.base_restock_amount
        last_restock_time = 0

        for month in range(months_to_simulate):
            month_name = dates[month].strftime('%B')
            seasonality_factor = (seasonality[month_name] - 5) * 0.1
            seasonal_factor = 1 + seasonality_factor
            monthly_demand = (self.population * 0.005 * 30 * seasonal_factor) + np.random.normal(0, self.variance)
            monthly_demand = max(0, monthly_demand)

            # Check for demand spike
            if np.random.random() < 0.3:
                monthly_demand *= 2
                demand_spike_indicator.append(1)  # Demand spike occurred
            else:
                demand_spike_indicator.append(0)  # No demand spike

            monthly_sales = min(stock, monthly_demand)
            stock -= monthly_sales

            # Calculate stock-to-demand ratio
            if monthly_demand > 0:
                stock_to_demand_ratio.append(stock / monthly_demand)
            else:
                stock_to_demand_ratio.append(np.nan)  # Handle division by zero

            total_sales.append(monthly_sales / 1e6)
            total_stock.append(stock / 1e6)

            # Determine shortage status
            if stock < self.max_pharma_stock * 0.1:
                status = 10 if monthly_sales > self.max_pharma_stock * 0.1 else 9
            elif stock < self.max_pharma_stock * 0.2:
                status = 7 if monthly_sales > self.max_pharma_stock * 0.2 else 8
            elif stock < self.max_pharma_stock * 0.3:
                status = 5 if monthly_sales > self.max_pharma_stock * 0.3 else 6
            elif stock < self.max_pharma_stock * 0.5:
                status = 3 if monthly_sales > self.max_pharma_stock * 0.5 else 4
            else:
                status = 1 if stock >= self.max_pharma_stock * 0.6 else 2

            shortage_status.append(status)

            # Time since last shortage event
            if status >= 7:
                last_shortage_event = month  # Update the last shortage event month

            if last_shortage_event >= 0:
                time_since_last_shortage_event.append(month - last_shortage_event)
            else:
                time_since_last_shortage_event.append(np.nan)  # No shortage has occurred yet

            # Restocking failure
            restocking_failure = 0
            if np.random.random() < 0.04:
                print(f"Warning: Restocking failure for Wirkstoff in {month_name} {dates[month].year}!")
                self.wirkstoff_stock -= self.wirkstoff_restock_rate * np.random.uniform(0.4, 0.9)
                self.wirkstoff_restock_delay = month + self.wirkstoff_ramp_up_delay
                restocking_failure = 1
            else:
                if month >= self.wirkstoff_restock_delay:
                    self.wirkstoff_stock += self.wirkstoff_restock_rate * np.random.uniform(1.0, 1.5)
                else:
                    self.wirkstoff_stock += self.wirkstoff_restock_rate * np.random.uniform(0.5, 1.0)

            restocking_failure_history.append(restocking_failure)

            # Restock logic
            if month % self.restock_interval == 0 and self.can_produce(restock_amount):
                stock += restock_amount
                self.wirkstoff_stock -= restock_amount * self.production_cycle
                last_restock_amounts.append(restock_amount / 1e6)
                days_since_last_restock.append(0)
                last_restock_time = month
            else:
                last_restock_amounts.append(0)
                days_since_last_restock.append(month - last_restock_time)

            # Production ramp-up status
            if shortage_status[-1] >= 7 and not self.scaled_production_active:
                if month - last_restock_time >= self.production_ramp_up_delay:
                    self.scaled_production_active = True
                    self.scaled_production_multiplier = 6

            if self.scaled_production_active and shortage_status[-1] < 7:
                self.scaled_production_active = False
                self.scaled_production_multiplier = 1

            production_ramp_up_status.append(1 if self.scaled_production_active else 0)

            if self.scaled_production_active and self.can_produce(restock_amount * self.scaled_production_multiplier):
                stock += restock_amount * self.scaled_production_multiplier
                self.wirkstoff_stock -= restock_amount * self.production_cycle * self.scaled_production_multiplier
                last_restock_time = month

            wirkstoff_stock_over_time.append(self.wirkstoff_stock / 1e6)

            # Calculate rolling variance of sales
            if len(total_sales) >= 3:
                rolling_var = np.var(total_sales[-3:])
                rolling_variance_sales.append(rolling_var)
            else:
                rolling_variance_sales.append(0)

            # Calculate average monthly sales over last 6 months
            if len(total_sales) >= 6:
                avg_sales = np.mean(total_sales[-6:])
                avg_monthly_sales_6m.append(avg_sales)
            else:
                avg_monthly_sales_6m.append(np.nan)  # Not enough data yet

            # Calculate cumulative restock amount over last 6 months
            if len(last_restock_amounts) >= 6:
                cumulative_restock = sum(last_restock_amounts[-6:])
                cumulative_restock_6m.append(cumulative_restock)
            else:
                cumulative_restock_6m.append(np.nan)  # Not enough data yet

            # Restocking failure count over last 6 months
            if len(restocking_failure_history) >= 6:
                failure_count = sum(restocking_failure_history[-6:])
                restocking_failure_count_6m.append(failure_count)
            else:
                restocking_failure_count_6m.append(np.nan)  # Not enough data yet

        # Calculate shortage status lag (2 months)
        shortage_status_lag_2m = [np.nan, np.nan] + shortage_status[:-2]

        df = pd.DataFrame({
            'date': dates,
            'sales': total_sales,
            'stock': total_stock,
            'shortage_status': shortage_status,
            'shortage_status_lag_2m': shortage_status_lag_2m,
            'last_restock_amount': last_restock_amounts,
            'days_since_last_restock': days_since_last_restock,
            'wirkstoff_stock': wirkstoff_stock_over_time,
            'demand_spike_indicator': demand_spike_indicator,
            'rolling_variance_sales': rolling_variance_sales,
            'avg_monthly_sales_6m': avg_monthly_sales_6m,
            'stock_to_demand_ratio': stock_to_demand_ratio,
            'cumulative_restock_6m': cumulative_restock_6m,
            'restocking_failure_count_6m': restocking_failure_count_6m,
            'production_ramp_up_status': production_ramp_up_status,
            'time_since_last_shortage_event': time_since_last_shortage_event
        })

        return df
