import matplotlib.pyplot as plt
from pandas.plotting import table


class Plotter:
    def __init__(self, df):
        self.df = df

    def truncate_large_cells(self, max_width=15):
        for col in self.df.columns:
            self.df[col] = self.df[col].apply(
                lambda x: f"{str(x)[:max_width]}..." if len(str(x)) > max_width else x
            )

    def wrap_column_names(self, max_width=15):
        self.df.columns = [
            "\n".join(col[i:i + max_width] for i in range(0, len(col), max_width))
            if len(col) > max_width else col
            for col in self.df.columns
        ]

    def plot_dataframe_as_image(self):
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

        plt.subplots_adjust(left=0.05, right=0.95, top=0.85, bottom=0.15)
        plt.show()
