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
    testing_png_path = os.path.join(base_dir, "testing_simulation_results.png")

    # Initialize database and simulator
    engine = init_db()
    db_manager = DatabaseManager(engine)

    # Check if simulations have already been run
    if check_files_exist(testing_csv_path, testing_png_path):
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

        # Save testing simulation to CSV and PNG
        plotter_test = Plotter(testing_simulation, save_path=base_dir)
        plotter_test.save_dataframe(file_name="testing_simulation_results.csv")
        plotter_test.plot_dataframe_as_image(file_name="testing_simulation_results.png")
        print("Testing simulation saved.")

    print("Simulations completed.")

    # Train and evaluate models
    mse_scores = train_and_evaluate_models_monthly(db_manager)

    # Identify the best model based on 12-month MSE
    best_model_name = min(mse_scores, key=lambda x: mse_scores[x]['mse_12'])
    print(f"Best overall model: {best_model_name}")

    # Add predictions to the testing simulation using the best model
    testing_simulation['Predicted Shortage Level'] = mse_scores[best_model_name]['model'].predict(
        StandardScaler().fit_transform(testing_simulation[
            ['sales', 'stock', 'last_restock_amount', 'days_since_last_restock', 'wirkstoff_stock', 'trend', 'seasonal']
        ])
    )

    # Ensure the Date column is formatted correctly if it exists
    if 'date' in testing_simulation.columns:
        testing_simulation['Date'] = pd.to_datetime(testing_simulation['date'])

    # Initialize the Plotter with the updated DataFrame
    plotter_test = Plotter(testing_simulation, save_path=base_dir)

    if not check_files_exist("./Dataframes_CSV_PNG/mse_line_chart.png"):
        print("Creating MSE line chart...")
        plotter_test.plot_mse_line_chart(mse_scores, file_name="mse_line_chart.png")
    else:
        print("MSE line chart already exists. Skipping creation.")

    if not check_files_exist("./Dataframes_CSV_PNG/mse_bar_36_months.png"):
        print("Creating MSE bar chart for 36 months...")
        plotter_test.plot_mse_bar_36(mse_scores, file_name="mse_bar_36_months.png")
    else:
        print("MSE bar chart for 36 months already exists. Skipping creation.")

    # Display rankings
    print("\nAlgorithm Rankings by MSE for Different Horizons:")
    for model_name, scores in mse_scores.items():
        print(f"\n{model_name}:")
        for horizon, mse in scores.items():
            if horizon.startswith('mse_'):
                print(f" - {horizon}: MSE = {mse:.4f}")

    print("\nCompleted evaluation and rankings for all horizons.")


if __name__ == "__main__":
    main()
