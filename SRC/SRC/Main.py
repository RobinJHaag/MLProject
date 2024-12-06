from DB_Setup import init_db
from DB import DatabaseManager
from DataSimulator import DataSimulator
from Plotter import Plotter
import os
import pandas as pd

def main():
    # Step 1: Initialize the database and database manager
    engine = init_db()
    db_manager = DatabaseManager(engine)

    # Step 2: Check if simulation data exists in the database
    if db_manager.is_simulation_data_complete():
        print("Simulation data already exists. Loading from database...")
        simulation_df = db_manager.load_simulation_data()

        # Print the path to the previously saved DataFrame
        saved_csv_path = os.path.join("SRC", "SRC", "DataFrames", "simulation_results.csv")
        print(f"Previously saved DataFrame located at: {saved_csv_path}")
    else:
        print("Simulation data not found or incomplete. Running simulation...")
        simulator = DataSimulator(random_state=42, months_to_simulate=120)
        simulation_df = simulator.simulate_sales_and_stock()
        db_manager.save_simulation_to_db(simulation_df)

        # Save the DataFrame as a CSV and PNG
        plotter = Plotter(simulation_df)

        # Save as CSV
        plotter.save_dataframe(file_name="simulation_results.csv")

        # Save as PNG
        plotter.plot_dataframe_as_image(file_name="simulation_results.png")

        print("Simulation data has been saved as both CSV and PNG.")


if __name__ == "__main__":
    main()
