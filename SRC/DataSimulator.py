import numpy as np
import pandas as pd
from DB_Setup import get_session, Dates, Shortages, Restocks, SimulationData
from utils import yap


def save_to_db(session, dates_df, simulation_df):
    """
    Saves the simulation results to the database.
    """
    pass  # Placeholder for the actual code


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
        self.production_cycle = 1.25
        self.wirkstoff_ramp_up_delay = 3
        self.max_production_capacity = 425_000  # Further reduced production capacity
        self.restock_delay = 0

        self.wirkstoff_restock_interval = 3
        self.wirkstoff_restock_amount = 1_580_000  # Reduced pharma stock restocking amount
        self.wirkstoff_restock_variance = 500_000

    def simulate_sales_and_stock(self):
        np.random.seed(self.random_state)

        seasonality = {
            'January': 1.2, 'February': 1.1, 'March': 1.0, 'April': 0.9, 'May': 0.8,
            'June': 0.8, 'July': 0.85, 'August': 0.9, 'September': 1.0,
            'October': 1.1, 'November': 1.2, 'December': 1.3
        }

        dates = pd.date_range(start='2024-01-01', periods=self.simulation_time_span, freq='MS')

        total_sales, total_stock, shortage_status = [], [], []
        last_restock_amounts, days_since_last_restock = [], []
        wirkstoff_stock_over_time, demand_spike_indicator = [], []
        stock_to_demand_ratio, time_since_last_shortage_event = [], []
        months_since_prod_issue, cumulative_shortages_over_time = [], []
        production_to_demand_ratio = []
        shortage_levels = []
        cumulative_shortages = 0

        stock = self.initial_pharma_stock
        last_shortage_event = -1
        last_prod_issue = -1

        for month in range(self.simulation_time_span):
            month_name = dates[month].strftime('%B')
            seasonal_factor = seasonality[month_name]

            # Calculate monthly demand
            monthly_demand = (self.population * 0.007 * 30 * seasonal_factor) + np.random.normal(0, self.variance)
            monthly_demand = max(0, monthly_demand)

            # Introduce demand spikes (3% chance if seasonality > 1.0)
            if seasonality[month_name] > 1.0 and np.random.random() < 0.03:
                monthly_demand *= 1.5 + np.random.random() * 0.5  # Spike between 1.5x and 2.0x
                yap(f"Demand spike event occurred in {month_name} (Month {month})!")
                demand_spike_indicator.append(1)
            else:
                demand_spike_indicator.append(0)

            # Calculate shortage level
            shortage_level = int((1 - (stock / self.max_pharma_stock)) * 9) + 1
            shortage_level = min(max(shortage_level, 1), 10)

            # Restock pharma stock (Wirkstoff)
            if month % self.wirkstoff_restock_interval == 0:
                wirkstoff_restock_amount = self.wirkstoff_restock_amount + np.random.normal(0, self.wirkstoff_restock_variance)
                wirkstoff_restock_amount = max(0, wirkstoff_restock_amount)
                self.wirkstoff_stock += wirkstoff_restock_amount
                yap(f"Pharma stock restocked: {wirkstoff_restock_amount / 1e6:.2f}M units.")

            # Calculate production output based on available pharma stock
            production_output = self.max_production_capacity
            required_wirkstoff = production_output * self.production_cycle

            if self.wirkstoff_stock >= required_wirkstoff:
                # Sufficient pharma stock to produce at max capacity
                self.wirkstoff_stock -= required_wirkstoff
            else:
                # Insufficient pharma stock; production limited
                production_output = self.wirkstoff_stock / self.production_cycle
                self.wirkstoff_stock = 0

            # Add production output to stock
            stock += production_output
            stock = min(stock, self.max_pharma_stock)  # Cap stock to maximum pharma stock level

            # Sales logic
            max_sales = stock * 0.65 if stock < self.max_pharma_stock * 0.75 else stock
            min_sales = stock * 0.015

            monthly_sales = min(stock, monthly_demand, max_sales)
            monthly_sales = max(monthly_sales, min_sales)
            stock -= monthly_sales
            total_sales.append(monthly_sales / 1e6)
            total_stock.append(stock / 1e6)

            # Update metrics
            stock_to_demand_ratio.append(stock / monthly_demand if monthly_demand > 0 else np.nan)
            production_to_demand_ratio.append(production_output / monthly_demand if monthly_demand > 0 else np.nan)
            cumulative_shortages_over_time.append(cumulative_shortages)
            shortage_levels.append(shortage_level)
            months_since_prod_issue.append(month - last_prod_issue if last_prod_issue >= 0 else np.nan)
            time_since_last_shortage_event.append(month - last_shortage_event if last_shortage_event >= 0 else np.nan)
            wirkstoff_stock_over_time.append(self.wirkstoff_stock / 1e6)

        dates_df = pd.DataFrame({'date': dates.strftime('%Y-%m-%d'), 'month_name': dates.strftime('%B')})
        simulation_df = pd.DataFrame({
            'sales': total_sales,
            'stock': total_stock,
            'wirkstoff_stock': wirkstoff_stock_over_time,
            'demand_spike_indicator': demand_spike_indicator,
            'stock_to_demand_ratio': stock_to_demand_ratio,
            'time_since_last_shortage_event': time_since_last_shortage_event,
            'months_since_prod_issue': months_since_prod_issue,
            'production_to_demand_ratio': production_to_demand_ratio,
            'cumulative_shortages': cumulative_shortages_over_time,
            'shortage_level': shortage_levels
        })

        return dates_df, simulation_df
