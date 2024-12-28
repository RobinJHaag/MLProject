import matplotlib.pyplot as plt
import os


class Plotter:
    def __init__(self, save_path="./Dataframes_CSV_PNG"):
        self.save_path = os.path.abspath(save_path)  # Use absolute path
        self.ensure_save_directory()

    def ensure_save_directory(self):
        """
        Ensure that the save directory exists; if not, create it.
        """
        os.makedirs(self.save_path, exist_ok=True)

    def plot_mse_by_step(self, mse_scores, file_name="mse_by_step.png"):
        """
        Plot MSE values for each step in the rolling forecast for all models.
        """
        plt.figure(figsize=(10, 6))

        colors = {
            "Linear Regression": "#b19cd9",  # Lavender
            "XGBoost": "#9370db",  # Medium Purple
            "SVM": "#8a2be2"  # Blue Violet
        }

        for model, scores in mse_scores.items():
            mse_list = scores["mse_list"]
            steps = range(1, len(mse_list) + 1)
            plt.plot(steps, mse_list, marker='o', label=model, color=colors.get(model, "#9370db"))

        plt.title("MSE by Step in Rolling Forecast", fontsize=14)
        plt.xlabel("Step (Month)", fontsize=12)
        plt.ylabel("Mean Squared Error (MSE)", fontsize=12)
        plt.legend(title="Models", fontsize=10)
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.tight_layout()

        file_path = os.path.join(self.save_path, file_name)
        plt.savefig(file_path)
        plt.show()
        print(f"MSE by Step plot saved as {file_path}.")

    def plot_average_mse(self, mse_scores, file_name="average_mse.png"):
        """
        Plot average MSE for each model.
        """
        models = list(mse_scores.keys())
        averages = [scores["average_mse"] for scores in mse_scores.values()]

        colors = ["#b19cd9", "#9370db", "#8a2be2"]

        plt.figure(figsize=(8, 6))
        plt.bar(models, averages, color=colors)
        plt.title("Average MSE Across Rolling Forecast", fontsize=14)
        plt.xlabel("Models", fontsize=12)
        plt.ylabel("Average Mean Squared Error (MSE)", fontsize=12)
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        plt.tight_layout()

        file_path = os.path.join(self.save_path, file_name)
        plt.savefig(file_path)
        plt.show()
        print(f"Average MSE plot saved as {file_path}.")

    def plot_mse_comparison(self, mse_scores, file_name="mse_comparison.png"):
        """
        Compare the MSE values across steps for all models in a grouped bar chart.
        """
        steps = range(1, len(next(iter(mse_scores.values()))["mse_list"]) + 1)
        width = 0.25  # Bar width
        x = range(len(steps))

        colors = ["#b19cd9", "#9370db", "#8a2be2"]

        plt.figure(figsize=(12, 6))
        for i, (model, scores) in enumerate(mse_scores.items()):
            mse_list = scores["mse_list"]
            plt.bar([pos + (i * width) for pos in x], mse_list, width=width, label=model, color=colors[i])

        plt.title("MSE Comparison Across Steps", fontsize=14)
        plt.xlabel("Step (Month)", fontsize=12)
        plt.ylabel("Mean Squared Error (MSE)", fontsize=12)
        plt.xticks([pos + width for pos in x], steps)
        plt.legend(title="Models", fontsize=10)
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        plt.tight_layout()

        file_path = os.path.join(self.save_path, file_name)
        plt.savefig(file_path)
        plt.show()
        print(f"MSE Comparison plot saved as {file_path}.")
