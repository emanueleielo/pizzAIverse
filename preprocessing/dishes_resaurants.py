import json

# Nome dei file JSON
primo_json_file = "../database/restaurants.json"  # Contiene la lista dei piatti
secondo_json_file = "../database/dish_mapping.json"  # Contiene il mapping nome -> ID
output_json_file = "../database/restaurants.json"  # Nome del file di output

# Carica il primo JSON (lista di piatti)
with open(primo_json_file, "r", encoding="utf-8") as file:
    ristoranti = json.load(file)

# Carica il secondo JSON (mappatura nome -> ID)
with open(secondo_json_file, "r", encoding="utf-8") as file:
    piatti_mapping = json.load(file)

# Funzione ricorsiva per rimuovere chiavi con valore None/null
def remove_nulls(data):
    if isinstance(data, dict):
        return {k: remove_nulls(v) for k, v in data.items() if v is not None}
    elif isinstance(data, list):
        return [remove_nulls(v) for v in data if v is not None]
    return data

# Aggiungi l'ID ai piatti corrispondenti e rimuovi i null
for ristorante in ristoranti:
    for piatto in ristorante["menu"]:
        nome_piatto = piatto.get("nome")
        if nome_piatto in piatti_mapping:
            piatto["ID"] = piatti_mapping[nome_piatto]

# Rimuove eventuali valori null prima di salvare
ristoranti = remove_nulls(ristoranti)

# Salva il nuovo JSON aggiornato
with open(output_json_file, "w", encoding="utf-8") as file:
    json.dump(ristoranti, file, indent=4, ensure_ascii=False)

print(f"Il file aggiornato è stato salvato come {output_json_file}")
