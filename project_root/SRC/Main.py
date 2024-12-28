import pandas as pd
import os

from DB_Setup import init_db, TrainingSimulationData, TestingSimulationData
from DB import DatabaseManager
from DataSimulator import DataSimulator
from Plotter import Plotter
from PredictMed import train_and_evaluate_rolling_forecast


def check_files_exist(file_paths):
    """
    Check if required files exist.
    """
    return all(os.path.exists(path) for path in file_paths)


def main():
    base_dir = "./Dataframes_CSV_PNG"
    os.makedirs(base_dir, exist_ok=True)

    # Paths for CSV files
    training_csv_path = os.path.join(base_dir, "training_simulation_results.csv")
    testing_csv_path = os.path.join(base_dir, "testing_simulation_results.csv")

    # Paths for PNG files
    mse_by_step_path = os.path.join(base_dir, "mse_by_step_lavender.png")
    average_mse_path = os.path.join(base_dir, "average_mse_lavender.png")
    mse_comparison_path = os.path.join(base_dir, "mse_comparison_lavender.png")

    # Initialize database and simulator
    engine = init_db()
    db_manager = DatabaseManager(engine)

    # Check if simulations have already been run
    if check_files_exist([training_csv_path, testing_csv_path]):
        print("Simulations already completed. Loading data from CSV files...\n")
        training_simulation = pd.read_csv(training_csv_path)
        testing_simulation = pd.read_csv(testing_csv_path)
    else:
        print("Running simulations...\n")

        # Run training simulation
        simulator_train = DataSimulator(random_state=42, months_to_simulate=120)
        training_simulation = simulator_train.simulate_sales_and_stock()
        db_manager.save_simulation_to_db(training_simulation, TrainingSimulationData)

        # Save training simulation to CSV
        training_simulation.to_csv(training_csv_path, index=False)
        print("Training simulation saved.")

        # Run testing simulation
        simulator_test = DataSimulator(random_state=99, months_to_simulate=120)
        testing_simulation = simulator_test.simulate_sales_and_stock()
        db_manager.save_simulation_to_db(testing_simulation, TestingSimulationData)

        # Save testing simulation to CSV
        testing_simulation.to_csv(testing_csv_path, index=False)
        print("Testing simulation saved.\n")

    print("Simulations completed.\n")

    # Train and evaluate models with rolling forecast
    print("Training and evaluating models with rolling forecast...\n")
    mse_scores = train_and_evaluate_rolling_forecast(db_manager)

    # Print evaluation results
    print("\nAlgorithm Performance (Rolling Forecast):\n")
    for model_name, scores in mse_scores.items():
        avg_mse = scores["average_mse"]
        mse_list = [round(mse, 4) for mse in scores["mse_list"]]
        print(f"{model_name}:")
        print(f" - Average MSE: {avg_mse:.4f}")
        print(f" - MSE List:")
        print("   ", mse_list, "\n")

    print("Evaluation completed.\n")

    # Initialize plotter
    plotter = Plotter(save_path=base_dir)

    # Generate plots if not already existing
    if not os.path.exists(mse_by_step_path):
        print("Generating MSE by Step plot...")
        plotter.plot_mse_by_step(mse_scores, file_name="mse_by_step_lavender.png")
    else:
        print("MSE by Step plot already exists.")

    if not os.path.exists(average_mse_path):
        print("Generating Average MSE plot...")
        plotter.plot_average_mse(mse_scores, file_name="average_mse_lavender.png")
    else:
        print("Average MSE plot already exists.")

    if not os.path.exists(mse_comparison_path):
        print("Generating MSE Comparison plot...")
        plotter.plot_mse_comparison(mse_scores, file_name="mse_comparison_lavender.png")
    else:
        print("MSE Comparison plot already exists.")


if __name__ == "__main__":
    main()
