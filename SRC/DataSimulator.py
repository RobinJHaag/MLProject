import numpy as np
import pandas as pd
from DB_Setup import get_session, Dates, Shortages, Restocks, SimulationData


def yap(message):
    print(message)  # Consistent personality output


class DataSimulator:
    def __init__(self, random_state=None, restock_interval=6, base_restock_amount=550000, months_to_simulate=48):
        self.random_state = random_state
        self.restock_interval = restock_interval
        self.base_restock_amount = base_restock_amount
        self.simulation_time_span = months_to_simulate + 1
        self.initial_pharma_stock = 5000000
        self.max_pharma_stock = 10000000
        self.population = 1000000
        self.variance = 100000
        self.wirkstoff_stock = 5000000
        self.production_cycle = 1
        self.wirkstoff_restock_rate = 120000
        self.wirkstoff_ramp_up_delay = 3
        self.wirkstoff_restock_delay = -1

    def simulate_sales_and_stock(self):
        np.random.seed(self.random_state)
        seasonality = {
            'January': 9, 'February': 8, 'March': 7, 'April': 5, 'May': 2,
            'June': 2, 'July': 3, 'August': 4, 'September': 5,
            'October': 7, 'November': 8, 'December': 10
        }
        dates = pd.date_range(start='2024-01-01', periods=self.simulation_time_span, freq='MS')

        total_sales, total_stock, shortage_status = [], [], []
        last_restock_amounts, days_since_last_restock = [], []
        wirkstoff_stock_over_time, demand_spike_indicator = [], []
        stock_to_demand_ratio, time_since_last_shortage_event = [], []

        stock = self.initial_pharma_stock
        restock_amount = self.base_restock_amount
        last_restock_time = 0
        last_shortage_event = -1

        for month in range(self.simulation_time_span):
            month_name = dates[month].strftime('%B')
            seasonal_factor = 1 + ((seasonality[month_name] - 5) * 0.1)
            monthly_demand = (self.population * 0.005 * 30 * seasonal_factor) + np.random.normal(0, self.variance)
            monthly_demand = max(0, monthly_demand)

            if np.random.random() < 0.3:
                monthly_demand *= 2
                demand_spike_indicator.append(1)
            else:
                demand_spike_indicator.append(0)

            monthly_sales = min(stock, monthly_demand)
            stock -= monthly_sales

            stock_to_demand_ratio.append(stock / monthly_demand if monthly_demand > 0 else np.nan)
            total_sales.append(monthly_sales / 1e6)
            total_stock.append(stock / 1e6)

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

            if status >= 7:
                last_shortage_event = month
            time_since_last_shortage_event.append(month - last_shortage_event if last_shortage_event >= 0 else np.nan)

            if month % self.restock_interval == 0:
                stock += restock_amount
                self.wirkstoff_stock -= restock_amount * self.production_cycle
                last_restock_amounts.append(restock_amount / 1e6)
                days_since_last_restock.append(0)
            else:
                last_restock_amounts.append(0)
                days_since_last_restock.append(month)

            wirkstoff_stock_over_time.append(self.wirkstoff_stock / 1e6)

        # Convert 'dates' column to string format for compatibility with SQLite
        dates_df = pd.DataFrame({'date': dates.strftime('%Y-%m-%d'), 'month_name': dates.strftime('%B')})
        simulation_df = pd.DataFrame({
            'sales': total_sales, 'stock': total_stock, 'wirkstoff_stock': wirkstoff_stock_over_time,
            'demand_spike_indicator': demand_spike_indicator, 'stock_to_demand_ratio': stock_to_demand_ratio,
            'time_since_last_shortage_event': time_since_last_shortage_event
        })

        return dates_df, simulation_df

    def save_to_db(self, session, dates_df, simulation_df):
        # Insert data into the Dates table while avoiding duplicates
        for _, row in dates_df.iterrows():
            # Check if the date already exists
            existing_date = session.query(Dates).filter(Dates.date == row['date']).first()
            if not existing_date:
                session.add(Dates(date=row['date'], month_name=row['month_name']))

        session.commit()  # Commit after inserting dates
        yap("Dates saved to DB")

        # Insert data into the SimulationData table
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
