from DataSimulator import DataSimulator
from DB import init_db, get_session, save_simulation_to_db
from utils import yap
from Plotter import Plotter


def main():
    # Initialize the database and session
    engine = init_db()
    session = get_session(engine)

    # Generate simulation data
    simulator = DataSimulator(random_state=42)
    dates_df, simulation_df = simulator.simulate_sales_and_stock()

    # Print and plot the simulation DataFrame
    yap("Simulation Data:")
    print(simulation_df)
    plotter = Plotter(simulation_df)
    plotter.plot_dataframe_as_image()

    # Save simulation data to the database
    save_simulation_to_db(session, dates_df, simulation_df)

    print("Simulation data saved to the database.")


if __name__ == '__main__':
    main()
