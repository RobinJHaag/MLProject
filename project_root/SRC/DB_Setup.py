from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import declarative_base

Base = declarative_base()


# Shared schema for training and testing tables
class BaseSimulationData:
    simulation_id = Column(Integer, primary_key=True)
    date_id = Column(Integer, ForeignKey('dates.date_id'))
    sales = Column(Float)
    stock = Column(Float)
    wirkstoff_stock = Column(Float)
    demand_spike_indicator = Column(Integer)
    stock_to_sales_ratio = Column(Float)
    time_since_last_shortage_event = Column(Float)
    months_since_prod_issue = Column(Float)
    cumulative_shortages = Column(Integer)
    sales_to_stock_ratio = Column(Float)
    wirkstoff_stock_percentage = Column(Float)
    shortage_level = Column(Integer)

    # New fields
    last_restock_amount = Column(Float)
    days_since_last_restock = Column(Integer)
    trend = Column(Float)
    seasonal = Column(Float)
    residual = Column(Float)


class TrainingSimulationData(Base, BaseSimulationData):
    __tablename__ = 'training_simulation_data'


class TestingSimulationData(Base, BaseSimulationData):
    __tablename__ = 'testing_simulation_data'


class Dates(Base):
    __tablename__ = 'dates'
    date_id = Column(Integer, primary_key=True)
    date = Column(String, unique=True)
    month_name = Column(String)


# Initialize database
def init_db(db_name='simulation_3nf.db'):
    engine = create_engine(f'sqlite:///{db_name}', echo=False)
    Base.metadata.create_all(engine)
    return engine

