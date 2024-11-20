from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, inspect, MetaData, Table
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()


# Define your tables as before
class Dates(Base):
    __tablename__ = 'dates'
    date_id = Column(Integer, primary_key=True)
    date = Column(String, unique=True)
    month_name = Column(String)


class Shortages(Base):
    __tablename__ = 'shortages'
    shortage_id = Column(Integer, primary_key=True)
    shortage_status = Column(Integer)
    description = Column(String)


class Restocks(Base):
    __tablename__ = 'restocks'
    restock_id = Column(Integer, primary_key=True)
    last_restock_amount = Column(Float)
    days_since_last_restock = Column(Integer)


class SimulationData(Base):
    __tablename__ = 'simulation_data'
    simulation_id = Column(Integer, primary_key=True)
    date_id = Column(Integer, ForeignKey('dates.date_id'))
    shortage_id = Column(Integer, ForeignKey('shortages.shortage_id'))
    restock_id = Column(Integer, ForeignKey('restocks.restock_id'))
    sales = Column(Float)
    stock = Column(Float)
    wirkstoff_stock = Column(Float)
    demand_spike_indicator = Column(Integer)
    stock_to_demand_ratio = Column(Float)
    time_since_last_shortage_event = Column(Float)
    months_since_prod_issue = Column(Float)  # Add this field
    production_to_demand_ratio = Column(Float)
    cumulative_shortages = Column(Integer)


# Function to add the new column to the existing table
def add_column(engine, table_name, column):
    with engine.connect() as connection:
        connection.execute(f'ALTER TABLE {table_name} ADD COLUMN {column.compile(dialect=engine.dialect)}')


# Initialize the database and add the new column if it doesn't exist
def init_db(db_name='simulation_3nf.db'):
    engine = create_engine(f'sqlite:///{db_name}', echo=False)
    inspector = inspect(engine)

    # Check if the table already exists
    if inspector.has_table("simulation_data"):
        # Check if the column exists
        columns = [col['name'] for col in inspector.get_columns("simulation_data")]
        if 'months_since_prod_issue' not in columns:
            add_column(engine, 'simulation_data', SimulationData.__table__.c.months_since_prod_issue)
    else:
        Base.metadata.create_all(engine)

    return engine


# Create a session to interact with the database
def get_session(engine):
    Session = sessionmaker(bind=engine)
    return Session()


# Initialize the database
engine = init_db()
session = get_session(engine)
