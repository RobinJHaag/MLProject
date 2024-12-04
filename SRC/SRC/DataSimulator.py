import numpy as np
import pandas as pd
from DB_Setup import Dates, SimulationData
from DB import save_simulation_to_db, get_session


class DataSimulator:
    def __init__(self, random_state=None, restock_interval=3, months_to_simulate=120):
        self.random_state = random_state
        self.restock_interval = restock_interval
        self.simulation_time_span = months_to_simulate + 1
        self.initial_pharma_stock = 3_000_000
        self.max_pharma_stock = 6_000_000
        self.population = 1_000_000
        self.variance = 650_000
        self.production_variance = 300_000
        self.wirkstoff_stock = 3_000_000
        self.max_wirkstoff_stock = 6_000_000
        self.production_cycle = 1.25
        self.wirkstoff_ramp_up_delay = 3
        self.max_production_capacity = 425_000
        self.restock_delay = 0
        self.wirkstoff_restock_interval = 3
        self.wirkstoff_restock_amount = 1_575_000
        self.wirkstoff_restock_variance = 500_000

    def simulate_sales_and_stock(self):
        np.random.seed(self.random_state)

        seasonality = {
            'January': 1.2, 'February': 1.1, 'March': 1.0, 'April': 0.9, 'May': 0.8,
            'June': 0.8, 'July': 0.85, 'August': 0.9, 'September': 1.0,
            'October': 1.1, 'November': 1.2, 'December': 1.3
        }

        dates = pd.date_range(start='2024-01-01', periods=self.simulation_time_span, freq='MS')

        total_sales, total_stock = [], []
        wirkstoff_stock_over_time, demand_spike_indicator = [], []
        stock_to_sales_ratio, time_since_last_shortage_event = [], []  # Renamed
        months_since_prod_issue, cumulative_shortages_over_time = [], []
        cumulative_shortages = 0
        shortage_levels, sales_to_stock_ratios = [], []
        wirkstoff_stock_percentages = []

        stock = self.initial_pharma_stock
        last_shortage_event = -1
        last_prod_issue = -1

        for month in range(self.simulation_time_span):
            month_name = dates[month].strftime('%B')
            seasonal_factor = seasonality[month_name]

            # Calculate monthly demand
            monthly_demand = (self.population * 0.007 * 30 * seasonal_factor) + np.random.normal(0, self.variance)
            monthly_demand = max(0, monthly_demand)

            # Introduce demand spikes
            if seasonality[month_name] > 1.0 and np.random.random() < 0.05:
                monthly_demand *= 1.5 + np.random.random() * 0.5
                demand_spike_indicator.append(1)
            else:
                demand_spike_indicator.append(0)

            # Calculate production output based on available pharma stock
            production_output = self.max_production_capacity
            required_wirkstoff = production_output * self.production_cycle

            if self.wirkstoff_stock >= required_wirkstoff:
                self.wirkstoff_stock -= required_wirkstoff
            else:
                production_output = self.wirkstoff_stock / self.production_cycle
                self.wirkstoff_stock = 0

            # Check for production issues
            if np.random.random() < 0.05:
                production_output *= 0.9
                last_prod_issue = month

            # Add production output to stock
            stock += production_output
            stock = min(stock, self.max_pharma_stock)

            # Calculate shortage level
            shortage_level = int((1 - (stock / self.max_pharma_stock)) * 9) + 1
            shortage_level = min(max(shortage_level, 1), 10)

            # Update cumulative shortages
            if shortage_level >= 7:
                cumulative_shortages += 1
                last_shortage_event = month

            # Restock Wirkstoff
            if month % self.wirkstoff_restock_interval == 0:
                wirkstoff_restock_amount = self.wirkstoff_restock_amount + np.random.normal(0, self.wirkstoff_restock_variance)
                wirkstoff_restock_amount = max(0, wirkstoff_restock_amount)
                self.wirkstoff_stock += wirkstoff_restock_amount
                self.wirkstoff_stock = min(self.wirkstoff_stock, self.max_wirkstoff_stock)

            # Sales logic
            max_sales = stock * 0.65 if stock < self.max_pharma_stock * 0.75 else stock
            min_sales = stock * 0.015

            monthly_sales = min(stock, monthly_demand, max_sales)
            monthly_sales = max(monthly_sales, min_sales)
            stock -= monthly_sales
            total_sales.append(monthly_sales / 1e6)
            total_stock.append(stock / 1e6)

            # Calculate new features
            sales_to_stock_ratio = monthly_sales / stock if stock > 0 else np.nan
            wirkstoff_stock_percentage = (self.wirkstoff_stock / self.max_wirkstoff_stock) * 100
            stock_to_sales_ratio.append(stock / monthly_sales if monthly_sales > 0 else np.nan)

            # Update metrics
            cumulative_shortages_over_time.append(cumulative_shortages)
            shortage_levels.append(shortage_level)
            months_since_prod_issue.append(month - last_prod_issue if last_prod_issue >= 0 else np.nan)
            time_since_last_shortage_event.append(month - last_shortage_event if last_shortage_event >= 0 else np.nan)
            wirkstoff_stock_over_time.append(self.wirkstoff_stock / 1e6)
            sales_to_stock_ratios.append(sales_to_stock_ratio)
            wirkstoff_stock_percentages.append(wirkstoff_stock_percentage)

        # Create DataFrames
        dates_df = pd.DataFrame({'date': dates.strftime('%Y-%m-%d'), 'month_name': dates.strftime('%B')})
        simulation_df = pd.DataFrame({
            'sales': total_sales,
            'stock': total_stock,
            'wirkstoff_stock': wirkstoff_stock_over_time,
            'demand_spike_indicator': demand_spike_indicator,
            'stock_to_sales_ratio': stock_to_sales_ratio,
            'time_since_last_shortage_event': time_since_last_shortage_event,
            'months_since_prod_issue': months_since_prod_issue,
            'cumulative_shortages': cumulative_shortages_over_time,
            'sales_to_stock_ratio': sales_to_stock_ratios,
            'wirkstoff_stock_percentage': wirkstoff_stock_percentages,
            'shortage_level': shortage_levels

        })

        # Normalize column names to avoid wrapping or formatting issues
        simulation_df.columns = simulation_df.columns.str.replace(r"\n", "", regex=True)
        print("Cleaned simulation_df columns:", list(simulation_df.columns))
        simulation_df = simulation_df.round(2)

        return dates_df, simulation_df





