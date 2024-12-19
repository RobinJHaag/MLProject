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

