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

    def plot_mse_line_chart(self, mse_scores, file_name="mse_line_chart.png"):
        """
        Plot a line chart comparing MSE scores across models and time horizons.
        """
        # Extract data for plotting
        horizons = [12, 24]
        models = mse_scores.keys()
        colors = ['#FF4500', '#800080', '#40E0D0']  # Sunset orange, purple, turquoise

        plt.figure(figsize=(12, 6))

        # Plot each model's MSE across horizons
        for model, color in zip(models, colors):
            mse_values = [mse_scores[model][f'mse_{horizon}'] for horizon in horizons]
            plt.plot(horizons, mse_values, label=model, color=color, marker='o', linestyle='-', linewidth=2)

        # Customize the plot
        plt.title('MSE Comparison Across Time Horizons', fontsize=16)
        plt.xlabel('Time Horizon (Months)', fontsize=14)
        plt.ylabel('Mean Squared Error', fontsize=14)
        plt.xticks(horizons, fontsize=12)
        plt.legend(fontsize=12, loc='upper left')
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        plt.tight_layout()

        # Save the plot
        file_path = os.path.join(self.save_path, file_name)
        plt.savefig(file_path)
        plt.show()
        plt.close()
        print(f"MSE Line Chart saved as {file_path}.")

    def plot_mse_bar_36(self, mse_scores, file_name="mse_bar_36_months.png"):
        """
        Plot a bar chart for the 36-month MSE to showcase XGBoost's outlier.
        """
        models = mse_scores.keys()
        mse_36_values = [mse_scores[model].get('mse_36', None) for model in models]
        colors = ['#FF4500', '#800080', '#40E0D0']  # Sunset orange, purple, turquoise

        plt.figure(figsize=(8, 6))
        plt.bar(models, mse_36_values, color=colors, alpha=0.8)
        plt.title('MSE Comparison at 36-Month Horizon', fontsize=16)
        plt.xlabel('Models', fontsize=14)
        plt.ylabel('Mean Squared Error', fontsize=14)
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        plt.tight_layout()

        # Save the plot
        file_path = os.path.join(self.save_path, file_name)
        plt.savefig(file_path)
        plt.show()
        plt.close()
        print(f"MSE Bar Chart for 36 months saved as {file_path}.")



