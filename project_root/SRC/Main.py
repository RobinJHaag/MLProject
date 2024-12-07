import pandas

from DB_Setup import init_db
from DB import DatabaseManager
from DataSimulator import DataSimulator
from Plotter import Plotter
import os
import pandas as pd


def main():
    # Define base path for outputs
    base_dir = "X:/Coding/test_neu/MLProject/project_root/SRC/Dataframes_CSV_PNG"
    os.makedirs(base_dir, exist_ok=True)  # Ensure the directory exists

    # Define file paths relative to base_dir
    csv_path = os.path.join(base_dir, "simulation_results.csv")
    png_path = os.path.join(base_dir, "simulation_results.png")

    # Check if files already exist
    if os.path.exists(csv_path) and os.path.exists(png_path):
        print("Simulation already completed. Loading data from CSV...")
        simulation_df = pd.read_csv(csv_path)
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
        plotter = Plotter(simulation_df, save_path=base_dir)  # Pass base_dir here
        plotter.plot_dataframe_as_image(file_name="simulation_results.png")

        print("Simulation results saved as CSV and PNG.")

    # Example usage of simulation_df
    print(simulation_df.head())


if __name__ == "__main__":
    main()




