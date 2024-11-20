import numpy as np
import pandas as pd
from DB_Setup import get_session, Dates, Shortages, Restocks, SimulationData
from utils import yap


class DataSimulator:
    def __init__(self, random_state=None, restock_interval=6, base_restock_amount=550000, months_to_simulate=48):
        # Initialize simulation parameters and variables.
        self.random_state = random_state
        self.restock_interval = restock_interval
        self.base_restock_amount = base_restock_amount
        self.simulation_time_span = months_to_simulate + 1
        self.initial_pharma_stock = 5000000
        self.max_pharma_stock = 10000000
        self.population = 1000000
        self.variance = 300000
        self.wirkstoff_stock = 5000000
        self.production_cycle = 1
        self.wirkstoff_restock_rate = 120000
        self.wirkstoff_ramp_up_delay = 3
        self.wirkstoff_restock_delay = -1
        self.max_production_capacity = 1000000
        self.restock_delay = 0

    def simulate_sales_and_stock(self):
        """
        Simulates the pharmaceutical sales and stock levels over the given time span.
        This includes handling seasonal demand, random demand fluctuations, shortages, restocking,
        and production issues. It also tracks various metrics to analyze system performance.
        """
        np.random.seed(self.random_state)

        # Define seasonality factors for each month to simulate varying demand patterns.
        seasonality = {
            'January': 9, 'February': 8, 'March': 7, 'April': 5, 'May': 2,
            'June': 2, 'July': 3, 'August': 4, 'September': 5,
            'October': 7, 'November': 8, 'December': 10
        }

        # Generate the range of dates corresponding to each simulated month.
        dates = pd.date_range(start='2024-01-01', periods=self.simulation_time_span, freq='MS')

        # Initialize lists to store simulation results for later analysis.
        total_sales, total_stock, shortage_status = [], [], []
        last_restock_amounts, days_since_last_restock = [], []
        wirkstoff_stock_over_time, demand_spike_indicator = [], []
        stock_to_demand_ratio, time_since_last_shortage_event = [], []

        # Set initial stock and restock parameters.
        stock = self.initial_pharma_stock
        restock_amount = self.base_restock_amount
        last_restock_time = 0
        last_shortage_event = -1

        # Iterate over each month to simulate sales, stock changes, and production events.
        for month in range(self.simulation_time_span):
            # Determine demand based on seasonal factors, random fluctuations, and potential demand spikes.
            month_name = dates[month].strftime('%B')
            seasonal_factor = 1 + ((seasonality[month_name] - 5) * 0.1)
            monthly_demand = (self.population * 0.005 * 30 * seasonal_factor) + np.random.normal(0, self.variance)
            monthly_demand = max(0, monthly_demand)  # Ensure non-negative demand.

            # Simulate random demand spikes that occur with a 30% probability.
            if np.random.random() < 0.3:
                monthly_demand *= 2
                demand_spike_indicator.append(1)
            else:
                demand_spike_indicator.append(0)

            # Update sales and stock levels for the month based on demand and availability.
            monthly_sales = min(stock, monthly_demand)
            stock -= monthly_sales
            stock_to_demand_ratio.append(stock / monthly_demand if monthly_demand > 0 else np.nan)
            total_sales.append(monthly_sales / 1e6)  # Convert to millions for easier analysis.
            total_stock.append(stock / 1e6)

            # Assign a shortage status code based on stock levels relative to thresholds.
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

            # Log shortages and track time since the last shortage event.
            shortage_status.append(status)
            if status >= 7:
                yap(f"Month: {month_name}, Stock: {stock}, Monthly Sales: {monthly_sales}, Status: {status}")
                last_shortage_event = month
            time_since_last_shortage_event.append(month - last_shortage_event if last_shortage_event >= 0 else np.nan)

            # Simulate restocking events and production issues based on timing and probabilities.
            if month % self.restock_interval == 0:
                if np.random.random() < 0.05:  # Simulate a restocking delay.
                    self.restock_delay = 2
                    restock_amount = 0
                    yap(f"Month: {month_name}, Restock Delayed, No Restock")
                elif np.random.random() < 0.05:  # Simulate a production issue with a random dip.
                    production_dip = np.random.uniform(0.1, 0.4)
                    restock_amount = self.base_restock_amount * (1 - production_dip)
                    yap(f"Month: {month_name}, Production Issue Occurred, Production Dip: {production_dip * 100:.1f}%")
                else:  # Normal restocking behavior.
                    restock_amount = min(self.base_restock_amount + np.random.normal(0, self.variance / 2), self.max_production_capacity)
                stock += restock_amount
                self.wirkstoff_stock -= restock_amount * self.production_cycle
                last_restock_amounts.append(restock_amount / 1e6)
                days_since_last_restock.append(0)
            else:
                last_restock_amounts.append(0)
                days_since_last_restock.append(month)

            # Track Wirkstoff stock levels for each month.
            wirkstoff_stock_over_time.append(self.wirkstoff_stock / 1e6)

        # Prepare DataFrames for simulation results to store in the database or analyze further.
        dates_df = pd.DataFrame({'date': dates.strftime('%Y-%m-%d'), 'month_name': dates.strftime('%B')})
        simulation_df = pd.DataFrame({
            'sales': total_sales, 'stock': total_stock, 'wirkstoff_stock': wirkstoff_stock_over_time,
            'demand_spike_indicator': demand_spike_indicator, 'stock_to_demand_ratio': stock_to_demand_ratio,
            'time_since_last_shortage_event': time_since_last_shortage_event
        })

        return dates_df, simulation_df

    def save_to_db(self, session, dates_df, simulation_df):
        """
        Saves the generated simulation data into the database.
        Handles both the date records and the simulation metrics, ensuring no duplicate entries.
        """
        # Insert dates into the Dates table, checking for existing entries to avoid duplication.
        for _, row in dates_df.iterrows():
            existing_date = session.query(Dates).filter(Dates.date == row['date']).first()
            if not existing_date:
                session.add(Dates(date=row['date'], month_name=row['month_name']))
        session.commit()
        yap("Dates saved to DB")

        # Insert simulation data into the SimulationData table for all generated records.
        for _, row in simulation_df.iterrows():
            session.add(SimulationData(
                sales=row['sales'],
                stock=row['stock'],
                wirkstoff_stock=row['wirkstoff_stock'],
                demand_spike_indicator=row['demand_spike_indicator'],
                stock_to_demand_ratio=row['stock_to_demand_ratio'],
                time_since_last_shortage_event=row['time_since_last_shortage_event']
            ))
        session.commit()
        yap("Simulation data saved to DB")
