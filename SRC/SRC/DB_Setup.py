from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import declarative_base

Base = declarative_base()



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
