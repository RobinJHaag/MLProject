from sqlalchemy.engine import row
from sqlalchemy.orm import sessionmaker
from DB_Setup import *
import pandas as pd
from sqlalchemy.orm import joinedload


class DatabaseManager:
    def __init__(self, engine):
        self.engine = engine
        self.session = self.get_session()

    def get_session(self):
        Session = sessionmaker(bind=self.engine)
        return Session()

    def save_simulation_to_db(self, simulation_df, table):
        """
        Save simulation data to the specified table (training or testing).
        """
        date_id_map = {}
        for date in simulation_df['date'].unique():
            existing_date = self.session.query(Dates).filter_by(date=date).first()
            if existing_date:
                date_id_map[date] = existing_date.date_id
            else:
                new_date = Dates(date=date,
                                 month_name=simulation_df[simulation_df['date'] == date]['month_name'].iloc[0])
                self.session.add(new_date)
                self.session.flush()
                date_id_map[date] = new_date.date_id

        self.session.commit()

        for _, row in simulation_df.iterrows():
            simulation_data = table(
                date_id=date_id_map[row['date']],
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
                shortage_level=row['shortage_level'],
                last_restock_amount=row['last_restock_amount'],
                days_since_last_restock=row['days_since_last_restock'],
                trend=row['trend'],
                seasonal=row['seasonal'],
                residual=row['residual']
            )
            self.session.add(simulation_data)

        self.session.commit()

    def load_simulation_data(self, table):
        """
        Load simulation data from the specified table (training or testing).
        """
        query = self.session.query(
            table.sales,
            table.stock,
            table.wirkstoff_stock,
            table.demand_spike_indicator,
            table.stock_to_sales_ratio,
            table.time_since_last_shortage_event,
            table.months_since_prod_issue,
            table.cumulative_shortages,
            table.sales_to_stock_ratio,
            table.wirkstoff_stock_percentage,
            table.shortage_level,
            table.last_restock_amount,
            table.days_since_last_restock,
            table.trend,
            table.seasonal,
            table.residual,
            Dates.date  # Selecting the `date` field from the `Dates` table
        ).join(Dates, table.date_id == Dates.date_id)  # Proper join with Dates table

        df = pd.DataFrame([{
            'date': row.date,  # Accessing the date from the Dates table
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
            'shortage_level': row.shortage_level,
            'last_restock_amount': row.last_restock_amount,
            'days_since_last_restock': row.days_since_last_restock,
            'trend': row.trend,
            'seasonal': row.seasonal,
            'residual': row.residual
        } for row in query.all()])

        return df


