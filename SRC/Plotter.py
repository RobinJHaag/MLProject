import matplotlib.pyplot as plt
from pandas.plotting import table


class Plotter:
    def __init__(self, df):
        self.df = df

    def plot_shortage_status(self):
        plt.figure(figsize=(12, 6))
        plt.plot(self.df['date'], self.df['shortage_status'], marker='o', linestyle='-', color='b')
        plt.title('Shortage Status Over Time')
        plt.xlabel('Date')
        plt.ylabel('Shortage Status')
        plt.grid(True)
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()

    def plot_dataframe_as_image(self):
        fig, ax = plt.subplots(figsize=(12, 8))
        ax.axis("tight")
        ax.axis("off")

        tbl = table(ax, self.df, loc="center", cellLoc="center", colWidths=[0.1] * len(self.df.columns))
        tbl.auto_set_font_size(False)
        tbl.set_fontsize(10)
        tbl.scale(1.2, 1.2)

        plt.show()  # Display the image directly instead of saving
