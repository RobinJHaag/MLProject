from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from DB_Setup import Base, Dates, SimulationData


def init_db(db_name='simulation_3nf.db'):
    engine = create_engine(f'sqlite:///{db_name}', echo=False)
    Base.metadata.create_all(engine)
    return engine


def get_session(engine):
    Session = sessionmaker(bind=engine)
    return Session()


def save_simulation_to_db(session, dates_df, simulation_df):
    """
    Save the simulation data into the database.
    """
    # Save dates to the database
    date_id_map = {}
    for _, row in dates_df.iterrows():
        # Check if the date already exists
        existing_date = session.query(Dates).filter_by(date=row['date']).first()
        if existing_date:
            date_id_map[row['date']] = existing_date.date_id
        else:
            # Add new date and get its ID
            new_date = Dates(date=row['date'], month_name=row['month_name'])
            session.add(new_date)
            session.flush()  # Get the generated primary key
            date_id_map[row['date']] = new_date.date_id

    session.commit()  # Commit all new dates to generate IDs

    # Save simulation data
    for i, sim_row in enumerate(simulation_df.itertuples(index=False, name=None)):  # Enumerate for index tracking
        (
            sales,
            stock,
            wirkstoff_stock,
            demand_spike_indicator,
            stock_to_sales_ratio,
            time_since_last_shortage_event,
            months_since_prod_issue,
            cumulative_shortages,
            sales_to_stock_ratio,
            wirkstoff_stock_percentage,
            shortage_level
        ) = sim_row

        # Use the current loop index `i` to access the date in dates_df
        date = dates_df.loc[i, 'date']
        date_id = date_id_map.get(date)

        if date_id is None:
            raise ValueError(f"Date ID not found for {date} in simulation_df row {i}.")

        # Create a SimulationData object
        simulation_data = SimulationData(
            date_id=date_id,
            sales=sales,
            stock=stock,
            wirkstoff_stock=wirkstoff_stock,
            demand_spike_indicator=demand_spike_indicator,
            stock_to_sales_ratio=stock_to_sales_ratio,
            time_since_last_shortage_event=time_since_last_shortage_event,
            months_since_prod_issue=months_since_prod_issue,
            cumulative_shortages=cumulative_shortages,
            sales_to_stock_ratio=sales_to_stock_ratio,
            wirkstoff_stock_percentage=wirkstoff_stock_percentage,
            shortage_level=shortage_level
        )
        session.add(simulation_data)






