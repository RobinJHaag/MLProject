
# Pharmazeutische Produktions- und Vertriebssimulation

Diese Simulation modelliert aus der Perspektive des Schweizer Staates die Produktion, den Verkauf und das Bestandsmanagement eines wichtigen Medikaments auf nationaler Ebene über einen Zeitraum von 48 Monaten. Sie dient als Prototyp, um Engpässe frühzeitig zu erkennen und effektiver darauf reagieren zu können.

Das Ziel der Simulation ist es, dem Schweizer Staat zu ermöglichen, mithilfe von maschinellem Lernen zukünftige Knappheiten vorherzusagen. Dadurch können Maßnahmen früher eingeleitet und die Versorgungssicherheit der Bevölkerung verbessert werden.

## Ziele der Simulation

1. **Nationale Bestandsübersicht:** Bereitstellung eines umfassenden Überblicks über die Verfügbarkeit eines Medikaments in der Schweiz.
2. **Nachfragevorhersage:** Simulation der monatlichen Nachfrage unter Berücksichtigung saisonaler Schwankungen und zufälliger Nachfragespitzen.
3. **Produktionsplanung:** Modellierung der Produktionsprozesse unter Berücksichtigung von Produktionskapazitäten, Wirkstoffverfügbarkeit und möglichen Produktionsproblemen.
4. **Engpassanalyse und Prävention:** Identifizierung potenzieller Engpässe und Unterstützung des Schweizer Staates bei der frühzeitigen Planung von Gegenmaßnahmen.
5. **Unterstützung durch maschinelles Lernen:** Einsatz eines ML-Modells zur Vorhersage von Knappheiten, das dem Schweizer Staat proaktive Entscheidungen ermöglicht.

## Hauptkomponenten der Simulation

### 1. Nachfragemodellierung
Die monatliche Nachfrage wird berechnet durch:
- **Basisnachfrage:** Abhängig von der Schweizer Bevölkerung und einem festgelegten Prozentsatz der Bevölkerung, die das Medikament benötigt.
- **Saisonale Schwankungen:** Monatliche saisonale Faktoren, die die Nachfrage beeinflussen.
- **Varianz:** Ein zufälliger Wert zur Simulation natürlicher Schwankungen in der Nachfrage.
- **Nachfragespitzen:** Mit einer gewissen Wahrscheinlichkeit treten plötzliche Nachfragespitzen auf, die die Nachfrage verdoppeln, um unvorhergesehene Ereignisse wie Krankheitsausbrüche zu simulieren.

### 2. Produktionsmodellierung
- **Produktionskapazität:** Maximale Produktionskapazität pro Monat.
- **Basis-Restock-Menge:** Menge, die zu festen Intervallen produziert wird.
- **Produktionsvarianz:** Ein zufälliger Wert, um Schwankungen in der Produktion zu simulieren.
- **Produktionsprobleme:** Mit einer gewissen Wahrscheinlichkeit treten Produktionsprobleme auf, die die Produktionsmenge verringern.
- **Wirkstoffverbrauch:** Menge des Wirkstoffs, die pro Produktionseinheit verbraucht wird.
- **Wirkstoffverfügbarkeit:** Verfügbarkeit des Wirkstoffs zur Produktion.

### 3. Bestandsmanagement
- **Lagerbestand:** Aktueller Lagerbestand des Medikaments.
- **Wirkstoffbestand:** Aktueller Bestand des Wirkstoffs.
- **Restock-Intervalle:** Intervall in Monaten, in dem das Medikament und der Wirkstoff nachproduziert werden.
- **Restock-Mengen:** Die Mengen, die bei jedem Restock produziert oder gekauft werden.

### 4. Engpassanalyse und Prävention
- **Knappheitslevel:** Wert zwischen 1 und 10, der basierend auf dem Lagerbestand berechnet wird.
- **Kumulative Engpässe:** Anzahl der Monate mit Engpässen.
- **Produktionsboost:** Gegebenenfalls wird bei hohen Knappheitsleveln ein Produktionsboost aktiviert.
- **Vorhersage durch ML-Modell:** Maschinelles Lernen wird verwendet, um zukünftige Engpässe vorherzusagen und rechtzeitig einzugreifen.

## Wichtige Parameter und Variablen
- **population:** Die Gesamtbevölkerung der Schweiz, als Basis für die Nachfrage.
- **variance:** Die Varianz, die zur Nachfrage hinzugefügt wird, um Schwankungen zu simulieren.
- **production_variance:** Die Varianz, die zur Produktion hinzugefügt wird.
- **max_production_capacity:** Maximale Produktionskapazität pro Monat.
- **production_cycle:** Der Verbrauch von Wirkstoff pro Produktionseinheit.
- **restock_interval:** Intervall in Monaten für Restocks des Medikaments.
- **wirkstoff_restock_interval:** Intervall in Monaten für Restocks des Wirkstoffs.
- **base_restock_amount:** Basismenge für Restocks.
- **wirkstoff_restock_amount:** Menge an Wirkstoff für Restocks.
- **seasonality:** Saisonale Faktoren für jeden Monat.

## Ablauf der Simulation

1. **Initialisierung:** Setzt Anfangswerte für Lagerbestand, Wirkstoffbestand und andere Variablen.
2. **Monatliche Iteration:** Für jeden Monat im Simulationszeitraum:
   - **Nachfrageberechnung:** Berechnet die monatliche Nachfrage basierend auf Saisonalität und Varianz.
   - **Produktion:** Berechnet die Produktionsmenge unter Berücksichtigung der Produktionskapazität und Wirkstoffverfügbarkeit.
   - **Verkauf:** Berechnet und aktualisiert die Verkaufsmenge.
   - **Engpassbewertung:** Berechnet das Knappheitslevel und plant gegebenenfalls einen Produktionsboost.
   - **Vorhersage durch ML-Modell:** Das Modell wird genutzt, um zukünftige Knappheiten vorherzusagen.
   - **Datenaufzeichnung:** Alle relevanten Daten werden für die Analyse gespeichert.

## Verwendung der Simulation

Die Simulation kann mit den Standardparametern ausgeführt werden oder durch Anpassen der Parameter an spezifische Szenarien angepasst werden.


## Interpretation der Ergebnisse

- **sales**: Verkaufsmenge in Millionen Einheiten pro Monat.
- **stock**: Aktueller Lagerbestand in Millionen Einheiten.
- **wirkstoff_stock**: Aktueller Wirkstoffbestand in Millionen Einheiten.
- **demand_spike_indicator**: Gibt an, ob eine Nachfragespitze aufgetreten ist (1) oder nicht (0).
- **stock_to_demand_ratio**: Verhältnis von Lagerbestand zur Nachfrage.
- **time_since_last_shortage_event**: Anzahl der Monate seit dem letzten Engpass.
- **months_since_prod_issue**: Anzahl der Monate seit dem letzten Produktionsproblem.
- **production_to_demand_ratio**: Verhältnis von Produktion zur Nachfrage.
- **cumulative_shortages**: Kumulative Anzahl der Engpässe.
- **shortage_level**: Aktuelles Knappheitslevel (1-10), wobei 1 ausreichend Lagerbestand und 10 akuten Mangel anzeigt.

## Bedeutung für den Schweizer Staat

Diese Simulation ermöglicht es dem Schweizer Staat, einen detaillierten Einblick in die Versorgungssituation eines wichtigen Medikaments zu erhalten. Durch die Integration eines maschinellen Lernmodells können zukünftige Engpässe frühzeitig vorhergesagt werden, was eine proaktive Planung und Intervention ermöglicht. Dies trägt dazu bei, die Versorgungssicherheit der Bevölkerung zu gewährleisten und die Auswirkungen von Medikamentenknappheiten zu minimieren.

## Machine Learning Modelle

In der Simulation werden verschiedene maschinelle Lernmodelle verwendet, um zukünftige Knappheiten vorherzusagen. Die Hauptmodelle sind:

- **Lineare Regression**: Ein einfaches Modell, das gut für lineare Beziehungen zwischen Variablen geeignet ist.
- **XGBoost**: Ein leistungsfähiges Modell für strukturierte Daten, das auf einem Gradient Boosting-Algorithmus basiert und besonders bei komplexeren Datenstrukturen eine gute Leistung zeigt.
- **Support Vector Machine (SVM)**: Ein Modell, das besonders bei kleinen Datensätzen gut funktioniert und oft eine hohe Genauigkeit bei Klassifikationsaufgaben erzielt.

### Hyperparameter-Tuning

Für jedes der Modelle wurde **GridSearchCV** verwendet, um die besten Hyperparameter zu finden:

- **Linear Regression**: Es wurden verschiedene Parameter getestet, aber letztendlich wurde der Parameter `fit_intercept` optimiert.
- **XGBoost**: Wichtige Parameter wie `learning_rate`, `max_depth`, und `n_estimators` wurden durch GridSearchCV optimiert.
- **SVM**: Hier wurden die Parameter `C`, `epsilon`, und `gamma` abgestimmt, um die beste Leistung zu erzielen.

Die Modelle wurden auf den Trainingsdaten trainiert und auf den Testdaten evaluiert, wobei die MSE (Mean Squared Error) als Metrik verwendet wurde.

## Prophet zur Modellierung saisonaler Effekte

**Prophet** wurde verwendet, um saisonale Schwankungen in der Nachfrage zu modellieren. Es handelt sich um ein Modell von Facebook, das speziell für Zeitreihendaten entwickelt wurde und saisonale, wöchentliche und jährliche Effekte berücksichtigt. In der Simulation wurden die Vorhersagen des Prophet-Modells verwendet, um saisonale Schwankungen in der Nachfrage zu simulieren, was zu einer realistischeren Modellierung der Medikamentennachfrage führt.

Durch diese Integration konnte die Genauigkeit der Vorhersagen verbessert und unvorhergesehene Nachfragespitzen berücksichtigt werden.



