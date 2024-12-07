from sqlalchemy.orm import sessionmaker
from sqlalchemy import func
from DB_Setup import Dates, SimulationData


class DatabaseManager:
    def __init__(self, engine):
        self.engine = engine
        self.session = self.get_session()

    def get_session(self):
        """
        Create a new session for the database.
        """
        Session = sessionmaker(bind=self.engine)
        return Session()

    def is_simulation_data_complete(self, months=120):
        """
        Check if the database already has the specified number of months of simulated data.
        """
        total_months = self.session.query(func.count(Dates.date_id)).scalar()
        return total_months == months

    def load_simulation_data(self):
        """
        Load simulation data from the database into a DataFrame.
        """
        query = self.session.query(
            SimulationData,
            Dates.date,
            Dates.month_name
        ).join(Dates, SimulationData.date_id == Dates.date_id)

        # Convert query results to a DataFrame
        df = pd.DataFrame([{
            'date': row.date,
            'month_name': row.month_name,
            'sales': row.sales,
            'stock': row.stock,
            'wirkstoff_stock': row.wirkstoff_stock,
            'demand_spike_indicator': row.demand_spike_indicator,
            'stock_to_sales_ratio': row.stock_to_sales_ratio,
            'time_since_last_shortage_event': row.time_since_last_shortage_event,
            'months_since_prod_issue': row.months_since_prod_issue,
            'cumulative_shortages': row.cumulative_shortages,
            'sales_to_stock_ratio': row.sales_to_stock_ratio,
            'wirkstoff_stock_percentage': row.wirkstoff_stock_percentage,
            'shortage_level': row.shortage_level
        } for row in query.all()])

        return df

    def save_simulation_to_db(self, simulation_df):
        """
        Save simulation data into the database, mapping 'date' to 'date_id'.
        """
        # Map existing dates to date_ids
        date_id_map = {}
        for date in simulation_df['date'].unique():
            existing_date = self.session.query(Dates).filter_by(date=date).first()
            if existing_date:
                date_id_map[date] = existing_date.date_id
            else:
                # Add date to the Dates table if it doesn't exist
                new_date = Dates(date=date,
                                 month_name=simulation_df[simulation_df['date'] == date]['month_name'].iloc[0])
                self.session.add(new_date)
                self.session.flush()  # Retrieve date_id
                date_id_map[date] = new_date.date_id

        self.session.commit()  # Commit dates to the database

        # Insert simulation data
        for i, row in simulation_df.iterrows():
            try:
                simulation_data = SimulationData(
                    date_id=date_id_map[row['date']],  # Map 'date' to 'date_id'
                    sales=row['sales'],
                    stock=row['stock'],
                    wirkstoff_stock=row['wirkstoff_stock'],
                    demand_spike_indicator=row['demand_spike_indicator'],
                    stock_to_sales_ratio=row['stock_to_sales_ratio'],
                    time_since_last_shortage_event=row['time_since_last_shortage_event'],
                    months_since_prod_issue=row['months_since_prod_issue'],
                    cumulative_shortages=row['cumulative_shortages'],
                    sales_to_stock_ratio=row['sales_to_stock_ratio'],
                    wirkstoff_stock_percentage=row['wirkstoff_stock_percentage'],
                    shortage_level=row['shortage_level']
                )
                self.session.add(simulation_data)
            except Exception as e:
                print(f"Error saving row {i}: {e}")

        self.session.commit()  # Commit all simulation data
