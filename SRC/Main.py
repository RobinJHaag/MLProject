from DataSimulator import DataSimulator, save_to_db
from DB_Setup import init_db, get_session
from Plotter import Plotter
from utils import yap


def main():
    # Initialize the simulator
    simulator = DataSimulator()

    # Run the simulation to get the DataFrames
    dates_df, simulation_df = simulator.simulate_sales_and_stock()

    # Initialize database and session
    engine = init_db()
    session = get_session(engine)

    # Print and plot the simulation DataFrame
    yap("Simulation Data:")
    print(simulation_df)
    plotter = Plotter(simulation_df)
    plotter.plot_dataframe_as_image()

    yap("Data saved to DB")


if __name__ == "__main__":
    main()
