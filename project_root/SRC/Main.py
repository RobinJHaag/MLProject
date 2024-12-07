import pandas

from DB_Setup import init_db
from DB import DatabaseManager
from DataSimulator import DataSimulator
from Plotter import Plotter
import os
import pandas as pd


def main():
    # Define paths to the output files
    csv_path = "Dataframes_CSV_PNG/simulation_results.csv"
    png_path = "Dataframes_CSV_PNG/simulation_results.png"

    # Check if files already exist
    if os.path.exists(csv_path) and os.path.exists(png_path):
        print("Simulation already completed. Loading data from CSV...")
        simulation_df = pd.read_csv(csv_path)  # Load the CSV if you need the data
    else:
        print("Simulation files not found. Running simulation...")

        # Initialize the database and run the simulation
        engine = init_db()
        db_manager = DatabaseManager(engine)
        simulator = DataSimulator(random_state=42, months_to_simulate=120)
        simulation_df = simulator.simulate_sales_and_stock()

        # Save results to the database
        db_manager.save_simulation_to_db(simulation_df)

        # Save results to CSV and PNG
        simulation_df.to_csv(csv_path, index=False)
        plotter = Plotter(simulation_df)
        plotter.plot_dataframe_as_image(file_name=png_path, show=True)
        print("Simulation results saved as CSV and PNG.")

    # Example usage of simulation_df to avoid the warning
    print(simulation_df.head())


if __name__ == "__main__":
    main()


