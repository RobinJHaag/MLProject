from DataSimulator import DataSimulator

def main():
    # Initialize the simulator with a specific random state for reproducibility
    simulator = DataSimulator(random_state=42)

    # Simulate for 36 months
    df = simulator.simulate_sales_and_stock(months_to_simulate=36)

    # Display the simulation results
    print("Gesamte Simulationsergebnisse:\n")
    print(df)

if __name__ == "__main__":
    main()