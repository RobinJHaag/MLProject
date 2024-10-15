# python
import matplotlib.pyplot as plt


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
