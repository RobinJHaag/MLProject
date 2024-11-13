from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, inspect
from sqlalchemy.orm import relationship, declarative_base, sessionmaker

Base = declarative_base()


# Define Dates table
class Dates(Base):
    __tablename__ = 'dates'
    date_id = Column(Integer, primary_key=True)
    date = Column(String, unique=True)
    month_name = Column(String)


# Define Shortages table
class Shortages(Base):
    __tablename__ = 'shortages'
    shortage_id = Column(Integer, primary_key=True)
    shortage_status = Column(Integer)
    description = Column(String)


# Define Restocks table
class Restocks(Base):
    __tablename__ = 'restocks'
    restock_id = Column(Integer, primary_key=True)
    last_restock_amount = Column(Float)
    days_since_last_restock = Column(Integer)


# Define SimulationData table
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
    time_since_last_shortage_event = Column(Integer)


# Initialize the database and create tables if they don't exist
def init_db(db_name='simulation_3nf.db'):
    engine = create_engine(f'sqlite:///{db_name}', echo=False)
    inspector = inspect(engine)

    # Check if the tables already exist
    if not inspector.has_table("dates") or not inspector.has_table("shortages") or not inspector.has_table(
            "restocks") or not inspector.has_table("simulation_data"):
        Base.metadata.create_all(engine)

    return engine


# Create a session to interact with the database
def get_session(engine):
    Session = sessionmaker(bind=engine)
    return Session()
