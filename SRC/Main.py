# python
from DataSimulator import DataSimulator
from PredictMed import train_and_evaluate_models
from Plotter import Plotter


def main():
    # Initialize the simulator with a specific random state for reproducibility
    simulator = DataSimulator(random_state=42, restock_interval=6)

    # Run the simulation for 48 months and obtain the DataFrame with all features
    df = simulator.simulate_sales_and_stock(months_to_simulate=48)
    plotter = Plotter(df.head(10))
    print(df)
    """
    # Check if plotting functions are called
    plotter = Plotter(df)
    print("Attempting to plot shortage status...")  # Debug print
    plotter.plot_shortage_status()
    print("Shortage status plotted.")  # Confirm plot completion
    """

    plotter.plot_dataframe_as_image()


    """
    # Train and evaluate models
    y_test, y_pred_linear, y_pred_rf = train_and_evaluate_models(df)

    # Display the predictions
    print("\nActual vs Predicted (Linear Regression):")
    for actual, pred in zip(y_test, y_pred_linear):
        print(f"Actual: {actual}, Predicted: {pred}")

    print("\nActual vs Predicted (Random Forest Regression):")
    for actual, pred in zip(y_test, y_pred_rf):
        print(f"Actual: {actual}, Predicted: {pred}")
    """


if __name__ == "__main__":
    main()
