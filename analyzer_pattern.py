import json                                                                     # Importation du module json pour lire les fichiers JSON
import re                                                                       # Importation du module re pour utiliser les expressions régulières

# ----------------Charger les patterns connus----------------
try:
    with open("known_anomalies.json", "r") as f:                                # Ouvrir le fichier des anomalies connues en lecture
        known_patterns = json.load(f)                                           # Charger les motifs d'erreurs à partir du fichier JSON
except FileNotFoundError:                                                       # Si le fichier n'existe pas
    print("Erreur : Le fichier 'known_anomalies.json' est introuvable.")        # Message d'erreur
    exit(1)                                                                     # Arrêt du programme



# ----------------Charger les faux positifs----------------
try:
    with open("false_positives.json", "r") as f:                                # Ouvrir le fichier des faux positifs en lecture
        false_positives = json.load(f)                                          # Charger les faux positifs depuis le fichier JSON
except FileNotFoundError:                                                       # Si le fichier n'existe pas
    false_positives = []                                                        # Initialiser une liste vide de faux positifs




# ----------------Charger le fichier log----------------
try:
    with open("odoo.log.txt", "r", encoding="utf-8") as f:                      # Ouvrir le fichier de log
        log_lines = f.readlines()                                               # Lire toutes les lignes du fichier de log
except FileNotFoundError:                                                       # Si le fichier n'existe pas
    print("Erreur : Le fichier 'odoo.log.txt' est introuvable.")                # Message d'erreur
    exit(1)                                                                     # Arrêt du programme



# ----------------Analyse----------------
anomalies = []                                                                  # Liste pour stocker les anomalies détectées

print("Analyse des logs...\n")                                                  # Message de début d'analyse

# ----------------Parcourir chaque ligne du fichier log avec son numéro---------
for i, line in enumerate(log_lines, start=1):
    line = line.strip()                                                         # Supprimer les espaces blancs en début et fin de ligne

    # Extraire la vraie partie message : tout ce qui est après le dernier ":"
    if ':' in line:                                                             # Vérifie si la ligne contient un caractère ":"
        message = line.split(':')[-1].strip()                                   # Prendre la dernière partie après les ":"
    else:
        continue                                                                # Si la ligne est mal formée (pas de ":"), on l’ignore

    # ----------------Vérifier les faux positifs----------------
    if any(re.search(fp, message, re.IGNORECASE) for fp in false_positives):    # Vérifie si un faux positif est présent dans le message
        continue                                                                # Si oui, ignorer cette ligne

    # Chercher les anomalies dans le message uniquement
    for pattern in known_patterns:                                              # Pour chaque motif d'erreur connu
        if re.search(pattern, message, re.IGNORECASE):                          # Si le motif est trouvé dans le message
            print(f"Ligne {i} | Pattern: {pattern} | Log: {line}")              # Afficher l’anomalie trouvée
            anomalies.append({                                                  # Ajouter l’anomalie à la liste
                "line_number": i,                                               # Numéro de ligne
                "log": line,                                                    # Contenu de la ligne
                "pattern": pattern                                              # Motif détecté
            })
            break                                                               # Une seule détection par ligne est suffisante

# Résumé
if not anomalies:                                                               # Si aucune anomalie détectée
    print("Aucune anomalie détectée.")                                          # Message d’absence d’erreurs
else:
    print(f"Nombre total d'anomalies détectées : {len(anomalies)}")             # Afficher le total détecté

    # Export du rapport
    with open("anomalies_report.txt", "w", encoding="utf-8") as report:         # Créer/écraser le fichier rapport
        for a in anomalies:                                                     # Parcourir les anomalies
            report.write(f"Ligne {a['line_number']} | Pattern: {a['pattern']} | Log: {a['log']}\n")  # Écrire chaque anomalie sur une seule ligne

    print("Rapport sauvegardé dans anomalies_report.txt")                       # Confirmation de sauvegarde
