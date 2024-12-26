import matplotlib.pyplot as plt
from pandas.plotting import table
import os


class Plotter:
    def __init__(self, df, save_path="./Dataframes_CSV_PNG"):
        self.df = df
        self.save_path = os.path.abspath(save_path)  # Use absolute path
        self.ensure_save_directory()

    def ensure_save_directory(self):
        """
        Ensure that the save directory exists; if not, create it.
        """
        os.makedirs(self.save_path, exist_ok=True)

    def truncate_large_cells(self, max_width=15):
        """
        Truncate the content of large cells in the DataFrame to improve display readability.
        """
        for col in self.df.columns:
            self.df[col] = self.df[col].apply(
                lambda x: f"{str(x)[:max_width]}..." if len(str(x)) > max_width else x
            )

    def wrap_column_names(self, max_width=15):
        """
        Wrap column names to fit within the specified maximum width.
        """
        self.df.columns = [
            "\n".join(col[i:i + max_width] for i in range(0, len(col), max_width))
            if len(col) > max_width else col
            for col in self.df.columns
        ]

    def plot_dataframe_as_image(self, file_name="dataframe_plot.png"):
        """
        Plot the DataFrame as an image and save it to a PNG file.
        """
        self.truncate_large_cells(max_width=15)
        self.wrap_column_names(max_width=15)

        num_rows, num_cols = self.df.shape
        fig_width = max(20, num_cols * 1.5)
        fig_height = max(10, num_rows * 0.5)

        fig, ax = plt.subplots(figsize=(fig_width, fig_height))
        ax.axis("tight")
        ax.axis("off")

        col_widths = [1.0 / len(self.df.columns)] * len(self.df.columns)

        tbl = table(ax, self.df, loc="center", cellLoc="center", colWidths=col_widths)
        tbl.auto_set_font_size(False)
        tbl.set_fontsize(8)
        tbl.scale(1, 1.2)

        # Save the plot as a PNG file
        file_path = os.path.join(self.save_path, file_name)  # Relative to save_path
        print(f"Saving PNG to: {file_path}")  # Debug print

        plt.savefig(file_path, bbox_inches="tight")
        plt.show()
        plt.close(fig)

        print(f"DataFrame plot saved as {file_path}.")

    def save_dataframe(self, file_name="dataframe.csv"):
        """
        Save the DataFrame to a file in the specified directory.
        Supports saving as CSV.
        """
        file_path = os.path.join(self.save_path, file_name)
        print(f"Saving CSV to: {file_path}")  # Debug print

        self.df.to_csv(file_path, index=False)

    def plot_mse_by_horizon(self, mse_scores, file_name="mse_by_horizon.png"):
        """
        Plot MSE values across different horizons (3, 6, 12 months) for each model.
        """
        horizons = ['mse_3', 'mse_6', 'mse_12']
        models = list(mse_scores.keys())

        # Prepare data for plotting
        data = {model: [mse_scores[model][horizon] for horizon in horizons] for model in models}

        # Define colors in lavender tones
        colors = {
            "Linear Regression": "#b19cd9",  # Lavender
            "XGBoost": "#9370db",  # Medium Purple
            "SVM": "#8a2be2"  # Blue Violet
        }

        plt.figure(figsize=(10, 6))
        for model, values in data.items():
            plt.plot(horizons, values, marker='o', label=model, color=colors.get(model, "#9370db"))

        plt.title("MSE Across Different Horizons", fontsize=14)
        plt.xlabel("Horizon", fontsize=12)
        plt.ylabel("Mean Squared Error (MSE)", fontsize=12)
        plt.legend(title="Models", fontsize=10)
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.tight_layout()

        file_path = os.path.join(self.save_path, file_name)
        plt.savefig(file_path)
        plt.show()
        print(f"MSE by Horizon plot saved as {file_path}.")

    def plot_average_mse(self, mse_scores, file_name="average_mse.png"):
        """
        Plot average MSE values across all horizons for each model.
        """
        models = list(mse_scores.keys())
        averages = [sum([mse_scores[model][horizon] for horizon in ['mse_3', 'mse_6', 'mse_12']]) / 3 for model in
                    models]

        # Define colors in lavender tones
        colors = ["#b19cd9", "#9370db", "#8a2be2"]

        plt.figure(figsize=(8, 6))
        plt.bar(models, averages, color=colors)
        plt.title("Average MSE Across All Horizons", fontsize=14)
        plt.xlabel("Models", fontsize=12)
        plt.ylabel("Average Mean Squared Error (MSE)", fontsize=12)
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        plt.tight_layout()

        file_path = os.path.join(self.save_path, file_name)
        plt.savefig(file_path)
        plt.show()
        print(f"Average MSE plot saved as {file_path}.")





