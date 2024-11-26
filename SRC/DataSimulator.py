import numpy as np
import pandas as pd
from DB_Setup import get_session, Dates, Shortages, Restocks, SimulationData
from utils import yap


def save_to_db(session, dates_df, simulation_df):
    """
    Saves simulation results to the database and an Excel file.
    Handles both the dates and simulation metrics while ensuring no duplicate entries.
    """
    # Save dates
    for _, row in dates_df.iterrows():
        if not session.query(Dates).filter(Dates.date == row['date']).first():
            session.add(Dates(date=row['date'], month_name=row['month_name']))
    session.commit()
    yap("Dates saved to DB")

    # Save simulation data
    for _, row in simulation_df.iterrows():
        session.add(SimulationData(
            sales=row['sales'],
            stock=row['stock'],
            wirkstoff_stock=row['wirkstoff_stock'],
            demand_spike_indicator=row['demand_spike_indicator'],
            stock_to_demand_ratio=row['stock_to_demand_ratio'],
            time_since_last_shortage_event=row['time_since_last_shortage_event'],
            months_since_prod_issue=row['months_since_prod_issue'],
            production_to_demand_ratio=row['production_to_demand_ratio'],
            cumulative_shortages=row['cumulative_shortages'],
            shortage_level=row['shortage_level']  # Added shortage_level
        ))
    session.commit()
    yap("Simulation data saved to DB")


class DataSimulator:
    def __init__(self, random_state=None, restock_interval=6, base_restock_amount=7600000, months_to_simulate=48):
        self.random_state = random_state
        self.restock_interval = restock_interval
        self.base_restock_amount = base_restock_amount
        self.simulation_time_span = months_to_simulate + 1
        self.initial_pharma_stock = 5000000
        self.max_pharma_stock = 10000000
        self.population = 1000000
        self.variance = 200000  # Variance for sales
        self.production_variance = 150000  # Variance for production
        self.wirkstoff_stock = 5000000
        self.production_cycle = 1
        self.wirkstoff_restock_rate = 120000
        self.wirkstoff_ramp_up_delay = 3
        self.max_production_capacity = 1000000
        self.restock_delay = 0

    def simulate_sales_and_stock(self):
        """
        Simulates the pharmaceutical production, sales, and stock levels over a defined period.
        Includes tracking of shortages, restocking, and production variability.
        """
        np.random.seed(self.random_state)

        # Seasonality factors to simulate monthly demand variations.
        seasonality = {
            'January': 1.2, 'February': 1.1, 'March': 1.0, 'April': 0.9, 'May': 0.8,
            'June': 0.8, 'July': 0.85, 'August': 0.9, 'September': 1.0,
            'October': 1.1, 'November': 1.2, 'December': 1.3
        }

        # Generate dates for simulation
        dates = pd.date_range(start='2024-01-01', periods=self.simulation_time_span, freq='MS')

        # Simulation output variables
        total_sales, total_stock, shortage_status = [], [], []
        last_restock_amounts, days_since_last_restock = [], []
        wirkstoff_stock_over_time, demand_spike_indicator = [], []
        stock_to_demand_ratio, time_since_last_shortage_event = [], []
        months_since_prod_issue, cumulative_shortages = [], 0
        production_to_demand_ratio = []
        shortage_levels = []  # To store shortage levels

        # Initial state variables
        stock = self.initial_pharma_stock
        restock_amount = self.base_restock_amount
        last_shortage_event = -1
        last_prod_issue = -1

        # Variables for production boost logic
        boost_active = False
        boost_scheduled = False
        boost_start_month = None
        boost_end_month = None

        # Simulate month by month
        for month in range(self.simulation_time_span):
            month_name = dates[month].strftime('%B')
            seasonal_factor = seasonality[month_name]

            # Calculate demand with seasonality and variance
            monthly_demand = (self.population * 0.005 * 30 * seasonal_factor) + np.random.normal(0, self.variance)
            monthly_demand = max(0, monthly_demand)  # Ensure demand is non-negative

            # Introduce random demand spikes
            if np.random.random() < 0.3:
                monthly_demand *= 2
                demand_spike_indicator.append(1)
            else:
                demand_spike_indicator.append(0)

            # Update boost status
            if boost_scheduled and month >= boost_start_month:
                boost_active = True
            if boost_active and month > boost_end_month:
                boost_active = False
                boost_scheduled = False

            # Adjust base restock amount based on boost
            if boost_active:
                adjusted_base_restock_amount = self.base_restock_amount * 1.15
            else:
                adjusted_base_restock_amount = self.base_restock_amount

            # Calculate production with variance
            production_output = adjusted_base_restock_amount + np.random.normal(0, adjusted_base_restock_amount * 0.1)
            production_output = max(0, production_output)

            # Apply production issue reduction
            if month - last_prod_issue <= 1:
                production_output *= 0.9  # Reduce output by 10% temporarily after a production issue

            # Limit to max production capacity
            production_output = min(production_output, self.max_production_capacity)

            # Restock and update stocks
            if month % self.restock_interval == 0:
                stock += production_output
                self.wirkstoff_stock -= production_output * self.production_cycle
                restock_amount = production_output
                last_restock_amounts.append(restock_amount / 1e6)
            else:
                last_restock_amounts.append(0)

            # Apply sales guardrail
            max_sales = stock * 0.25 if stock < self.max_pharma_stock * 0.85 else stock
            min_sales = stock * 0.01  # Ensure sales are at least 2% of current stock
            monthly_sales = min(stock, monthly_demand, max_sales)
            monthly_sales = max(monthly_sales, min_sales)  # Apply the minimum sales guardrail
            stock -= monthly_sales
            total_sales.append(monthly_sales / 1e6)
            total_stock.append(stock / 1e6)

            # Calculate metrics
            stock_to_demand_ratio.append(stock / monthly_demand if monthly_demand > 0 else np.nan)
            production_to_demand_ratio.append(production_output / monthly_demand if monthly_demand > 0 else np.nan)

            # Track shortage events and cumulative shortages
            if stock < self.max_pharma_stock * 0.2:
                cumulative_shortages += 1
                last_shortage_event = month

            # Update shortage status
            shortage_status.append(9 if stock < self.max_pharma_stock * 0.2 else 1)

            # Calculate shortage level from 1 to 10
            shortage_level = int((1 - (stock / self.max_pharma_stock)) * 9) + 1
            shortage_level = min(max(shortage_level, 1), 10)
            shortage_levels.append(shortage_level)

            # Schedule production boost if shortage level is 7 or higher
            if shortage_level >= 7 and not boost_active and not boost_scheduled:
                boost_start_month = month + 2
                boost_end_month = boost_start_month + 1  # Boost lasts for 2 months
                boost_scheduled = True

            # Update months since last production issue
            if np.random.random() < 0.05:  # Production issue probability
                last_prod_issue = month
            months_since_prod_issue.append(month - last_prod_issue if last_prod_issue >= 0 else np.nan)

            # Track Wirkstoff stock levels
            wirkstoff_stock_over_time.append(self.wirkstoff_stock / 1e6)

        # Prepare DataFrames for database storage or further analysis
        dates_df = pd.DataFrame({'date': dates.strftime('%Y-%m-%d'), 'month_name': dates.strftime('%B')})
        simulation_df = pd.DataFrame({
            'sales': total_sales,
            'stock': total_stock,
            'wirkstoff_stock': wirkstoff_stock_over_time,
            'demand_spike_indicator': demand_spike_indicator,
            'stock_to_demand_ratio': stock_to_demand_ratio,
            'time_since_last_shortage_event': [
                month - last_shortage_event if last_shortage_event >= 0 else np.nan for month in
                range(self.simulation_time_span)
            ],
            'months_since_prod_issue': months_since_prod_issue,
            'production_to_demand_ratio': production_to_demand_ratio,
            'cumulative_shortages': [cumulative_shortages] * self.simulation_time_span,
            'shortage_level': shortage_levels  # Include shortage level in the DataFrame
        })

        return dates_df, simulation_df
