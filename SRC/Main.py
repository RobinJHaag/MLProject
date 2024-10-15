# python
from DataSimulator import DataSimulator
from PredictMed import train_and_evaluate_models
from Plotter import Plotter


def main():
    # Initialize the simulator with a specific random state for reproducibility
    simulator = DataSimulator(random_state=42)

    # Simulate for 36 months
    df = simulator.simulate_sales_and_stock(months_to_simulate=36)

    # Display the simulation results
    print("Gesamte Simulationsergebnisse:\n")
    print(df)

    # Plot the shortage status over time
    plotter = Plotter(df)
    plotter.plot_shortage_status()

    # Train and evaluate models
    y_test, y_pred_linear, y_pred_rf = train_and_evaluate_models(df)

    # Display the predictions
    print("\nActual vs Predicted (Linear Regression):")
    for actual, pred in zip(y_test, y_pred_linear):
        print(f"Actual: {actual}, Predicted: {pred}")

    print("\nActual vs Predicted (Random Forest Regression):")
    for actual, pred in zip(y_test, y_pred_rf):
        print(f"Actual: {actual}, Predicted: {pred}")

if __name__ == "__main__":
    main()