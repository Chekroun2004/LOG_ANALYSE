# analyzer_tokens.py - Script d'analyse des logs Odoo par utilisateur et type

import re                                                                                                            # Importation du module re pour les expressions régulières
from collections import defaultdict                                                                                  # Importation de defaultdict pour créer des dictionnaires avec valeurs par défaut
import matplotlib.pyplot as plt                                                                                      # Importation de pyplot pour la génération de graphiques
import sys                                                                                                           # Importation du module sys pour la gestion des sorties du programme
import json                                                                                                          # Importation du module json pour la manipulation de fichiers JSON

ERROR_KEYWORDS = re.compile(r"error|exception|failed")                                                               # Regex pour les erreurs
WARNING_KEYWORDS = re.compile(r"warning")                                                                            # Regex pour les warnings
USER_PATTERN = re.compile(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d+\s+\d+\s+(INFO|ERROR|WARNING)\s+(\w+)")           # Regex pour extraire l'utilisateur

def categorize_log(line):                                                                                            # Fonction de catégorisation des lignes de log
    line_lower = line.lower()                                                                                        # Conversion en minuscules

    if "no error" in line_lower or "without error" in line_lower: return "info"                                      # Faux positif → info
    if ERROR_KEYWORDS.search(line_lower): return "error"                                                             # Mot-clé d'erreur → error
    if WARNING_KEYWORDS.search(line_lower): return "warning"                                                         # Mot-clé de warning → warning
    return "info"                                                                                                    # Par défaut → info

def extract_user(line):                                                                                              # Fonction d'extraction de l'utilisateur
    match = USER_PATTERN.search(line)                                                                                # Application de la regex
    return match.group(2).lower() if match else "unknown"                                                            # Retourne l'utilisateur ou "unknown"

def main():                                                                                                          # Fonction principale
    try:
        with open("odoo.log.txt", "r", encoding="utf-8") as f: lines = [line.strip() for line in f if line.strip()]  # Lecture et nettoyage du log
        if not lines: print("Aucun log à analyser : le fichier est vide."); sys.exit(0)                              # Fichier vide
    except FileNotFoundError: print("Erreur : fichier odoo.log.txt introuvable."); sys.exit(1)                       # Fichier introuvable
    except UnicodeDecodeError: print("Erreur : problème d'encodage (utilisez UTF-8)."); sys.exit(1)                  # Problème d'encodage

    user_stats = defaultdict(lambda: {"error": 0, "warning": 0, "info": 0})                                          # Stats par utilisateur

    for line in lines:                                                                                               # Parcours des lignes
        category = categorize_log(line)                                                                              # Déterminer la catégorie
        user = extract_user(line)                                                                                    # Extraire l'utilisateur
        user_stats[user][category] += 1                                                                              # Incrémenter le compteur

    users = sorted(user_stats.keys())                                                                                # Tri des utilisateurs
    categories = ["error", "warning", "info"]                                                                        # Types à afficher
    colors = {"error": "#E74C3C", "warning": "#F1C40F", "info": "#3498DB"}                                           # Couleurs des barres

    plt.figure(figsize=(14, 6))                                                                                      # Taille de la figure

    for i, cat in enumerate(categories):                                                                             # Pour chaque type
        values = [user_stats[user][cat] for user in users]                                                           # Récupère les valeurs
        plt.bar([x + i * 0.2 for x in range(len(users))], values, width=0.2, label=cat.upper(), color=colors[cat])   # Barres empilées

    plt.xticks([x + 0.2 for x in range(len(users))], users, rotation=45)                                             # Noms utilisateurs
    plt.ylabel("Nombre de logs")                                                                                     #Axe Y
    plt.title("Logs Odoo par utilisateur et type", weight="bold")                                                    # Titre
    plt.legend()                                                                                                     # Légende
    plt.grid(axis="y", linestyle="--", alpha=0.3)                                                                    # Grille horizontale
    plt.tight_layout()                                                                                               # Ajustement auto
    plt.savefig("log_report.png")                                                                                    # Sauvegarde du graphique
    plt.show()                                                                                                       # Affichage

    with open("user_stats.json", "w") as f: json.dump(user_stats, f, indent=4)                                      # Export JSON

    print("Terminé ! Rapport sauvegardé dans log_report.png et user_stats.json")                                    # Confirmation

if __name__ == "__main__": main()                                                                                   # Point d'entrée
