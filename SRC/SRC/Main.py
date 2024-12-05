from DataSimulator import DataSimulator
from DB import init_db, get_session, save_simulation_to_db
from utils import yap
from Plotter import Plotter


def main():
    engine = init_db()
    session = get_session(engine)

    simulator = DataSimulator(random_state=42)
    dates_df, simulation_df = simulator.simulate_sales_and_stock()

    yap("Simulation Data:")
    print(simulation_df)
    plotter = Plotter(simulation_df)
    plotter.plot_dataframe_as_image()

    save_simulation_to_db(session, dates_df, simulation_df)

    print("Simulation data saved to the database.")


if __name__ == '__main__':
    main()
