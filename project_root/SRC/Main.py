import pandas as pd
import os
from DB_Setup import init_db, TrainingSimulationData, TestingSimulationData
from DB import DatabaseManager
from DataSimulator import DataSimulator
from Plotter import Plotter
from PredictMed import *


def check_files_exist(csv_path, png_path=None):
    """
    Check if required files (CSV and optionally PNG) exist.
    """
    if png_path:
        return os.path.exists(csv_path) and os.path.exists(png_path)
    return os.path.exists(csv_path)


def main():
    base_dir = "./Dataframes_CSV_PNG"
    os.makedirs(base_dir, exist_ok=True)

    # Paths for CSV and PNG files
    training_csv_path = os.path.join(base_dir, "training_simulation_results.csv")
    training_png_path = os.path.join(base_dir, "training_simulation_results.png")
    testing_csv_path = os.path.join(base_dir, "testing_simulation_results.csv")
    testing_png_path = os.path.join(base_dir, "testing_simulation_results.png")

    # Initialize database and simulator
    engine = init_db()
    db_manager = DatabaseManager(engine)

    # Check if simulations have already been run
    if check_files_exist(testing_csv_path, testing_png_path):
        print("Simulations already completed. Loading data from CSV files...")

        # Load training and testing simulations from CSV
        training_simulation = pd.read_csv(training_csv_path)
        testing_simulation = pd.read_csv(testing_csv_path)
        print("Training Simulation Columns:", training_simulation.columns.tolist())
        print("Testing Simulation Columns:", testing_simulation.columns.tolist())
    else:
        print("Running simulations...")

        # Run training simulation
        simulator_train = DataSimulator(random_state=42, months_to_simulate=120)
        training_simulation = simulator_train.simulate_sales_and_stock()
        db_manager.save_simulation_to_db(training_simulation, TrainingSimulationData)

        # Save training simulation to CSV
        plotter_train = Plotter(training_simulation, save_path=base_dir)
        plotter_train.save_dataframe(file_name="training_simulation_results.csv")
        plotter_train.save_dataframe(file_name="training_simulation_results.png")

        print("Training simulation saved.")

        # Run testing simulation
        simulator_test = DataSimulator(random_state=99, months_to_simulate=120)
        testing_simulation = simulator_test.simulate_sales_and_stock()
        db_manager.save_simulation_to_db(testing_simulation, TestingSimulationData)

        # Save testing simulation to CSV and PNG
        plotter_test = Plotter(testing_simulation, save_path=base_dir)
        plotter_test.save_dataframe(file_name="testing_simulation_results.csv")
        plotter_test.plot_dataframe_as_image(file_name="testing_simulation_results.png")

        print("Testing simulation saved.")

    print("Simulations completed.")
    print("Sample Training Data:")
    print(training_simulation.head())
    print("Sample Testing Data:")
    print(testing_simulation.head())

    engine = init_db('simulation_3nf.db')
    db_manager = DatabaseManager(engine)

    train_and_evaluate_models(db_manager)


if __name__ == "__main__":
    main()
