import csv
import json

# Nome del file CSV di input
csv_filename = '../Hackapizza Dataset/Misc/Distanze.csv'

# Nome del file JSON di output
json_filename = '../database/distance.json'

# Inizializza una lista per memorizzare i dati JSON
data = []

# Leggi il file CSV
with open(csv_filename, 'r') as csvfile:
    csvreader = csv.reader(csvfile)

    # Leggi l'intestazione
    header = next(csvreader)[1:]

    # Leggi le righe successive
    for row in csvreader:
        # Nome del pianeta (prima colonna)
        planet = row[0]

        # Distanze verso gli altri pianeti
        distances = row[1:]

        # Crea un dizionario per il pianeta corrente
        planet_data = {
            'planet': planet,
            'distances': {}
        }

        # Aggiungi le distanze al dizionario
        for i, distance in enumerate(distances):
            planet_data['distances'][header[i]] = int(distance)

        # Aggiungi il dizionario alla lista dei dati
        data.append(planet_data)

# Scrivi i dati JSON nel file di output
with open(json_filename, 'w') as jsonfile:
    json.dump(data, jsonfile, indent=4)
