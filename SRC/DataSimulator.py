import numpy as np
import pandas as pd
from DB_Setup import get_session, Dates, Shortages, Restocks, SimulationData
from utils import yap


def save_to_db(session, dates_df, simulation_df):
    """
    Speichert die Simulationsergebnisse in der Datenbank.
    """
    # (Der Code bleibt unverändert)
    pass  # Platzhalter für den tatsächlichen Code


class DataSimulator:
    def __init__(self, random_state=None, restock_interval=3, base_restock_amount=6_500_000, months_to_simulate=48):
        self.random_state = random_state
        self.restock_interval = restock_interval  # Restock-Hauptbestand alle 3 Monate
        self.base_restock_amount = base_restock_amount  # Leicht erhöhte Basis-Restock-Menge
        self.simulation_time_span = months_to_simulate + 1
        self.initial_pharma_stock = 4_000_000  # Beibehalten
        self.max_pharma_stock = 8_000_000  # Beibehalten
        self.population = 1_000_000
        self.variance = 500_000  # Beibehalten
        self.production_variance = 300_000  # Beibehalten
        self.wirkstoff_stock = 4_000_000  # Beibehalten
        self.production_cycle = 1.4  # Leicht reduzierter Wirkstoffverbrauch
        self.wirkstoff_ramp_up_delay = 3
        self.max_production_capacity = 850_000  # Leicht erhöhte Produktionskapazität
        self.restock_delay = 0

        # Angepasste Wirkstoff-Restock-Parameter
        self.wirkstoff_restock_interval = 3  # Beibehalten
        self.wirkstoff_restock_amount = 3_500_000  # Leicht erhöhte Wirkstoff-Restock-Menge
        self.wirkstoff_restock_variance = 500_000  # Beibehalten

    def simulate_sales_and_stock(self):
        """
        Simuliert die pharmazeutische Produktion, Verkäufe und Lagerbestände über einen definierten Zeitraum.
        """
        np.random.seed(self.random_state)

        # Saisonale Faktoren zur Simulation monatlicher Nachfragevariationen.
        seasonality = {
            'January': 1.2, 'February': 1.1, 'March': 1.0, 'April': 0.9, 'May': 0.8,
            'June': 0.8, 'July': 0.85, 'August': 0.9, 'September': 1.0,
            'October': 1.1, 'November': 1.2, 'December': 1.3
        }

        # Generiere Daten für die Simulation
        dates = pd.date_range(start='2024-01-01', periods=self.simulation_time_span, freq='MS')

        # Simulationsausgabevariablen
        total_sales, total_stock, shortage_status = [], [], []
        last_restock_amounts, days_since_last_restock = [], []
        wirkstoff_stock_over_time, demand_spike_indicator = [], []
        stock_to_demand_ratio, time_since_last_shortage_event = [], []
        months_since_prod_issue, cumulative_shortages_over_time = [], []
        production_to_demand_ratio = []
        shortage_levels = []  # Um Knappheitslevel zu speichern
        cumulative_shortages = 0

        # Anfangszustandsvariablen
        stock = self.initial_pharma_stock
        restock_amount = self.base_restock_amount
        last_shortage_event = -1
        last_prod_issue = -1

        # Variablen für Produktionsboost-Logik
        boost_active = False
        boost_scheduled = False
        boost_start_month = None
        boost_end_month = None

        # Monatliche Simulation
        for month in range(self.simulation_time_span):
            month_name = dates[month].strftime('%B')
            seasonal_factor = seasonality[month_name]

            # Nachfrage mit Saisonalität und Varianz berechnen
            monthly_demand = (self.population * 0.007 * 30 * seasonal_factor) + np.random.normal(0, self.variance)
            monthly_demand = max(0, monthly_demand)  # Sicherstellen, dass die Nachfrage nicht negativ ist

            # Zufällige Nachfragespitzen einführen
            if np.random.random() < 0.3:
                monthly_demand *= 2
                demand_spike_indicator.append(1)
            else:
                demand_spike_indicator.append(0)

            # Boost-Status aktualisieren
            if boost_scheduled and month >= boost_start_month:
                boost_active = True
            if boost_active and month > boost_end_month:
                boost_active = False
                boost_scheduled = False

            # Basis-Restock-Menge basierend auf Boost anpassen
            if boost_active:
                adjusted_base_restock_amount = self.base_restock_amount * 1.15
            else:
                adjusted_base_restock_amount = self.base_restock_amount

            # Wirkstoff restocken, wenn es das Restock-Intervall ist
            if month % self.wirkstoff_restock_interval == 0:
                # Varianz zum Wirkstoff-Restocking hinzufügen
                wirkstoff_restock_amount = self.wirkstoff_restock_amount + np.random.normal(0, self.wirkstoff_restock_variance)
                wirkstoff_restock_amount = max(0, wirkstoff_restock_amount)  # Sicherstellen, dass die Menge nicht negativ ist
                self.wirkstoff_stock += wirkstoff_restock_amount

            # Produktion mit Varianz berechnen
            production_output = adjusted_base_restock_amount + np.random.normal(0, self.production_variance)
            production_output = max(0, production_output)

            # Produktionsprobleme prüfen
            if np.random.random() < 0.05:  # Wahrscheinlichkeit für Produktionsprobleme
                production_output *= 0.9  # Produktion um 10% reduzieren
                last_prod_issue = month

            # Max. Produktionskapazität beachten
            production_output = min(production_output, self.max_production_capacity)

            # Benötigten Wirkstoff für die Produktion berechnen
            required_wirkstoff = production_output * self.production_cycle

            if self.wirkstoff_stock >= required_wirkstoff:
                # Genug Wirkstoff vorhanden, Produktion fortsetzen
                self.wirkstoff_stock -= required_wirkstoff
            else:
                # Nicht genug Wirkstoff, Produktionsoutput anpassen
                production_output = self.wirkstoff_stock / self.production_cycle
                self.wirkstoff_stock = 0  # Gesamter verfügbarer Wirkstoff wurde verbraucht

            # Restocken und Bestände aktualisieren, wenn Produktionsoutput größer als Null ist
            if month % self.restock_interval == 0 and production_output > 0:
                stock += production_output
                restock_amount = production_output
                last_restock_amounts.append(restock_amount / 1e6)
            else:
                last_restock_amounts.append(0)

            # Verkaufs-Guardrails
            max_sales = stock * 0.5 if stock < self.max_pharma_stock * 0.85 else stock
            min_sales = stock * 0.005  # Mindestverkauf von 0,5% des aktuellen Bestands

            # Verkäufe berechnen
            monthly_sales = min(stock, monthly_demand, max_sales)
            monthly_sales = max(monthly_sales, min_sales)
            stock -= monthly_sales
            total_sales.append(monthly_sales / 1e6)
            total_stock.append(stock / 1e6)

            # Metriken berechnen
            stock_to_demand_ratio.append(stock / monthly_demand if monthly_demand > 0 else np.nan)
            production_to_demand_ratio.append(production_output / monthly_demand if monthly_demand > 0 else np.nan)

            # Engpässe verfolgen und kumulative Engpässe
            if stock < self.max_pharma_stock * 0.2:
                cumulative_shortages += 1
                last_shortage_event = month

            cumulative_shortages_over_time.append(cumulative_shortages)

            # Knappheitsstatus aktualisieren
            shortage_status.append(9 if stock < self.max_pharma_stock * 0.2 else 1)

            # Knappheitslevel von 1 bis 10 berechnen
            shortage_level = int((1 - (stock / self.max_pharma_stock)) * 9) + 1
            shortage_level = min(max(shortage_level, 1), 10)
            shortage_levels.append(shortage_level)

            # Produktionsboost planen, wenn Knappheitslevel 7 oder höher ist
            if shortage_level >= 7 and not boost_active and not boost_scheduled:
                boost_start_month = month + 2
                boost_end_month = boost_start_month + 1  # Boost dauert 2 Monate
                boost_scheduled = True

            # Monate seit letztem Produktionsproblem aktualisieren
            months_since_prod_issue.append(month - last_prod_issue if last_prod_issue >= 0 else np.nan)

            # Wirkstoffbestandslevel verfolgen
            wirkstoff_stock_over_time.append(self.wirkstoff_stock / 1e6)

            # Zeit seit letztem Engpassereignis aktualisieren
            time_since_last_shortage_event.append(month - last_shortage_event if last_shortage_event >= 0 else np.nan)

        # DataFrames für Datenbankspeicherung oder weitere Analyse vorbereiten
        dates_df = pd.DataFrame({'date': dates.strftime('%Y-%m-%d'), 'month_name': dates.strftime('%B')})
        simulation_df = pd.DataFrame({
            'sales': total_sales,
            'stock': total_stock,
            'wirkstoff_stock': wirkstoff_stock_over_time,
            'demand_spike_indicator': demand_spike_indicator,
            'stock_to_demand_ratio': stock_to_demand_ratio,
            'time_since_last_shortage_event': time_since_last_shortage_event,
            'months_since_prod_issue': months_since_prod_issue,
            'production_to_demand_ratio': production_to_demand_ratio,
            'cumulative_shortages': cumulative_shortages_over_time,
            'shortage_level': shortage_levels
        })

        return dates_df, simulation_df
