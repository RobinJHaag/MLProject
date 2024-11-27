# Pharmazeutische Produktions- und Vertriebssimulation
Diese Simulation modelliert aus der Perspektive des Schweizer Staates die Produktion, den Verkauf und das Bestandsmanagement eines einzelnen Medikaments auf nationaler Ebene über einen Zeitraum von 48 Monaten. Sie dient als Prototyp, um die nationale Sicht auf ein Medikament zu simulieren und soll dazu beitragen, Engpässe frühzeitig zu erkennen und effektiver darauf reagieren zu können.

Das Ziel ist es, dem Schweizer Staat mehr Handlungsraum zu bieten, indem mithilfe von maschinellem Lernen zukünftige Knappheiten vorhergesagt werden. Dadurch können Maßnahmen früher eingeleitet und die Versorgungssicherheit der Bevölkerung verbessert werden.

# Ziele der Simulation
Nationale Bestandsübersicht: Bereitstellung eines umfassenden Überblicks über die Verfügbarkeit eines wichtigen Medikaments in der Schweiz.
Nachfragevorhersage: Simulation der monatlichen Nachfrage unter Berücksichtigung saisonaler Schwankungen und zufälliger Nachfragespitzen.
Produktionsplanung: Modellierung der Produktionsprozesse unter Berücksichtigung von Produktionskapazitäten, Wirkstoffverfügbarkeit und möglichen Produktionsproblemen.
Engpassanalyse und Prävention: Identifizierung potenzieller Engpässe und Unterstützung des Schweizer Staates bei der frühzeitigen Planung von Gegenmaßnahmen.
Unterstützung durch maschinelles Lernen: Einsatz eines ML-Modells, um Knappheiten vorherzusagen und dem Schweizer Staat proaktive Entscheidungen zu ermöglichen.


# Hauptkomponenten der Simulation
1. Nachfragemodellierung
Die monatliche Nachfrage wird wie folgt berechnet:

Basisnachfrage: Abhängig von der Schweizer Bevölkerung und einem festen Prozentsatz der Bevölkerung, die das Medikament benötigt.
Saisonale Schwankungen: Monatliche saisonale Faktoren erhöhen oder verringern die Basisnachfrage.
Varianz: Ein zufälliger Wert wird hinzugefügt, um natürliche Schwankungen in der Nachfrage zu simulieren.
Nachfragespitzen: Mit einer bestimmten Wahrscheinlichkeit tritt eine Nachfragespitze auf, die die Nachfrage verdoppelt, um unerwartete Ereignisse wie Krankheitsausbrüche zu simulieren.

2. Produktionsmodellierung
Produktionskapazität: Es gibt eine maximale Produktionskapazität pro Monat, die nicht überschritten werden kann.
Basis-Restock-Menge: Die Menge, die alle festgelegten Restock-Intervalle produziert wird.
Produktionsvarianz: Ein zufälliger Wert wird hinzugefügt, um Schwankungen in der Produktion zu simulieren.
Produktionsprobleme: Mit einer bestimmten Wahrscheinlichkeit tritt ein Produktionsproblem auf, das die Produktion reduziert.
Wirkstoffverbrauch: Für die Produktion wird eine bestimmte Menge Wirkstoff pro Produktionseinheit verbraucht.
Wirkstoffverfügbarkeit: Wenn nicht genügend Wirkstoff verfügbar ist, wird die Produktion entsprechend reduziert.

4. Bestandsmanagement
Lagerbestand: Verfolgt den aktuellen Lagerbestand des Medikaments auf nationaler Ebene.
Wirkstoffbestand: Verfolgt den aktuellen Bestand des Wirkstoffs.
Restock-Intervalle: Das Medikament und der Wirkstoff werden in festgelegten Intervallen wieder aufgefüllt.
Restock-Mengen: Die Mengen, die bei jedem Restock produziert bzw. gekauft werden.
Verkaufs-Guardrails: Legen die minimalen und maximalen Verkaufszahlen fest, um unrealistische Verkäufe zu vermeiden.

6. Engpassanalyse und Prävention
Knappheitslevel: Ein Wert zwischen 1 und 10, der basierend auf dem aktuellen Lagerbestand berechnet wird.
Kumulative Engpässe: Verfolgt die Anzahl der Monate, in denen ein Engpass aufgetreten ist.
Produktionsboost: Bei hohen Knappheitsleveln wird ein Produktionsboost geplant, um den Lagerbestand wieder aufzufüllen.
Vorhersage durch ML-Modell: Das Modell nutzt maschinelles Lernen, um zukünftige Knappheiten vorherzusagen und dem Schweizer Staat frühzeitige Interventionen zu ermöglichen.


# Wichtige Parameter und Variablen
population: Die Gesamtbevölkerung der Schweiz, die als Basis für die Nachfrage dient.
variance: Die Varianz, die zur Nachfrage hinzugefügt wird, um natürliche Schwankungen zu simulieren.
production_variance: Die Varianz, die zur Produktion hinzugefügt wird.
max_production_capacity: Die maximale Produktionskapazität pro Monat.
production_cycle: Der Wirkstoffverbrauch pro Produktionseinheit.
restock_interval: Das Intervall in Monaten, in dem das Medikament produziert wird.
wirkstoff_restock_interval: Das Intervall in Monaten, in dem der Wirkstoff gekauft wird.
base_restock_amount: Die Basismenge, die bei jedem Restock produziert wird.
wirkstoff_restock_amount: Die Menge an Wirkstoff, die bei jedem Restock gekauft wird.
seasonality: Ein Dictionary, das saisonale Faktoren für jeden Monat enthält.
Ablauf der Simulation
Initialisierung: Setzt die Anfangswerte für Lagerbestand, Wirkstoffbestand und andere Variablen.
Monatliche Iteration: Für jeden Monat im Simulationszeitraum werden folgende Schritte durchgeführt:
Nachfrageberechnung: Berechnet die monatliche Nachfrage unter Berücksichtigung von Saisonalität und Varianz.
Produktion:
Überprüft, ob ein Restock ansteht.
Berechnet die mögliche Produktionsmenge basierend auf Kapazität, Varianz und Wirkstoffverfügbarkeit.
Aktualisiert den Lagerbestand und den Wirkstoffbestand.
Verkauf:
Berechnet die Verkaufsmenge unter Berücksichtigung von Nachfrage und Guardrails.
Aktualisiert den Lagerbestand.
Engpassbewertung:
Berechnet das Knappheitslevel.
Verfolgt kumulative Engpässe.
Plant gegebenenfalls einen Produktionsboost.
Vorhersage durch ML-Modell: Nutzt historische Daten, um zukünftige Knappheiten vorherzusagen.
Datenaufzeichnung: Speichert alle relevanten Variablen für die Analyse.
Verwendung der Simulation
Die Simulation kann mit den Standardparametern ausgeführt werden oder durch Anpassen der Parameter an spezifische Szenarien angepasst werden.


# Ergebnisse anzeigen
print(simulation_df)
Interpretation der Ergebnisse
sales: Die Verkaufsmenge in Millionen Einheiten pro Monat.
stock: Der aktuelle Lagerbestand des Medikaments in Millionen Einheiten.
wirkstoff_stock: Der aktuelle Wirkstoffbestand in Millionen Einheiten.
demand_spike_indicator: Gibt an, ob in diesem Monat eine Nachfragespitze aufgetreten ist (1) oder nicht (0).
stock_to_demand_ratio: Verhältnis von Lagerbestand zur Nachfrage.
time_since_last_shortage_event: Anzahl der Monate seit dem letzten Engpassereignis.
months_since_prod_issue: Anzahl der Monate seit dem letzten Produktionsproblem.
production_to_demand_ratio: Verhältnis von Produktion zur Nachfrage.
cumulative_shortages: Kumulative Anzahl der Engpässe.
shortage_level: Aktuelles Knappheitslevel (1-10), wobei 1 ausreichend Lagerbestand und 10 akuten Mangel anzeigt.
Bedeutung für den Schweizer Staat
Diese Simulation ermöglicht es dem Schweizer Staat, einen detaillierten Einblick in die Versorgungssituation eines wichtigen Medikaments zu erhalten. Durch die Integration eines maschinellen Lernmodells können zukünftige Engpässe frühzeitig vorhergesagt werden, was eine proaktive Planung und Intervention ermöglicht. Dies trägt dazu bei, die Versorgungssicherheit der Bevölkerung zu gewährleisten und die Auswirkungen von Medikamentenknappheiten zu minimieren.
