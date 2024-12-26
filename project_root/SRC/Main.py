import pandas as pd
import os

from sklearn.preprocessing import StandardScaler

from DB_Setup import init_db, TrainingSimulationData, TestingSimulationData
from DB import DatabaseManager
from DataSimulator import DataSimulator
from Plotter import Plotter
from PredictMed import train_and_evaluate_models_monthly


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
    testing_csv_path = os.path.join(base_dir, "testing_simulation_results.csv")
    mse_horizon_plot_path = os.path.join(base_dir, "mse_by_horizon_lavender.png")
    average_mse_plot_path = os.path.join(base_dir, "average_mse_lavender.png")

    # Initialize database and simulator
    engine = init_db()
    db_manager = DatabaseManager(engine)

    # Check if simulations have already been run
    if check_files_exist(testing_csv_path):
        print("Simulations already completed. Loading data from CSV files...")
        training_simulation = pd.read_csv(training_csv_path)
        testing_simulation = pd.read_csv(testing_csv_path)
    else:
        print("Running simulations...")

        # Run training simulation
        simulator_train = DataSimulator(random_state=42, months_to_simulate=120)
        training_simulation = simulator_train.simulate_sales_and_stock()
        db_manager.save_simulation_to_db(training_simulation, TrainingSimulationData)

        # Save training simulation to CSV
        plotter_train = Plotter(training_simulation, save_path=base_dir)
        plotter_train.save_dataframe(file_name="training_simulation_results.csv")
        print("Training simulation saved.")

        # Run testing simulation
        simulator_test = DataSimulator(random_state=99, months_to_simulate=120)
        testing_simulation = simulator_test.simulate_sales_and_stock()
        db_manager.save_simulation_to_db(testing_simulation, TestingSimulationData)

        # Save testing simulation to CSV
        plotter_test = Plotter(testing_simulation, save_path=base_dir)
        plotter_test.save_dataframe(file_name="testing_simulation_results.csv")
        print("Testing simulation saved.")

    print("Simulations completed.")

    # Train and evaluate models
    mse_scores = train_and_evaluate_models_monthly(db_manager)

    # Plot only if the plots do not already exist
    plotter = Plotter(testing_simulation, save_path=base_dir)
    if not os.path.exists(mse_horizon_plot_path):
        print("Generating MSE by Horizon plot...")
        plotter.plot_mse_by_horizon(mse_scores, file_name="mse_by_horizon_lavender.png")
    else:
        print("MSE by Horizon plot already exists.")

    if not os.path.exists(average_mse_plot_path):
        print("Generating Average MSE plot...")
        plotter.plot_average_mse(mse_scores, file_name="average_mse_lavender.png")
    else:
        print("Average MSE plot already exists.")

    print("\nAlgorithm Rankings by MSE for Different Horizons:")
    for model_name, scores in mse_scores.items():
        print(f"\n{model_name}:")
        for horizon, mse in scores.items():
            if horizon.startswith('mse_'):
                print(f" - {horizon}: MSE = {mse:.4f}")
        print(f" - rfo_mse: MSE = {scores['rfo_mse']:.4f}")

    print("\nCompleted evaluation and rankings for all horizons.")


if __name__ == "__main__":
    main()
