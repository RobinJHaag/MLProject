import matplotlib.pyplot as plt
from pandas.plotting import table


class Plotter:
    def __init__(self, df):
        self.df = df

    """
    def plot_shortage_status(self):
        plt.figure(figsize=(20, 20))
        plt.plot(self.df['date'], self.df['shortage_status'], marker='o', linestyle='-', color='b')
        plt.title('Shortage Status Over Time')
        plt.xlabel('Date')
        plt.ylabel('Shortage Status')
        plt.grid(True)
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()
    """
    def plot_dataframe_as_image(self):
        # Adjust column names to fit within the table by splitting long names
        new_columns = []
        for col in self.df.columns:
            if len(col) > 15:  # Adjust the length threshold as needed
                # Split the column name into multiple lines for better readability
                split_points = [i for i in range(0, len(col), 15)]
                new_col = '\n'.join([col[i:i+15] for i in split_points])
                new_columns.append(new_col)
            else:
                new_columns.append(col)
        self.df.columns = new_columns

        # Plot the DataFrame as an image
        fig, ax = plt.subplots(figsize=(20, 8))
        ax.axis("tight")
        ax.axis("off")

        # Set column widths dynamically based on the number of columns
        col_widths = [0.15] * len(self.df.columns)

        tbl = table(ax, self.df, loc="center", cellLoc="center", colWidths=col_widths)
        tbl.auto_set_font_size(False)
        tbl.set_fontsize(8)
        tbl.scale(1, 1.2)

        # Adjust subplot margins to prevent overlapping
        plt.subplots_adjust(left=0.05, right=0.95, top=0.75, bottom=0.1)

        # Show the plot
        plt.show()
