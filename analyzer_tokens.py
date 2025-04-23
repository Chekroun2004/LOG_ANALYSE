# Importation des modules nécessaires
import re                                                                                               # Pour l'utilisation d'expressions régulières (recherche de motifs dans le texte)
from collections import defaultdict                                                                     # Pour créer un dictionnaire avec des valeurs par défaut
import matplotlib.pyplot as plt                                                                         # Pour générer des graphiques (bibliothèque matplotlib)

# === Fonction pour catégoriser une ligne de log selon son contenu ===
def categorize_log(line):
    line_lower = line.lower()                                                                           # Convertit toute la ligne en minuscules pour simplifier la détection

                                                                                                        # Si la ligne contient une forme négative d'erreur (donc pas une vraie erreur), on la classe comme info
    if any(neg in line_lower for neg in ["no error", "without error", "no exception"]):
        return "info"

                                                                                                        # Si la ligne contient des mots-clés indiquant une erreur, on la classe comme "error"
    if any(word in line_lower for word in ["error", "exception", "failed"]):
        return "error"
                                                                                                        # Si la ligne contient le mot "warning", on la classe comme "warning"
    elif "warning" in line_lower:
        return "warning"
                                                                                                        # Par défaut, on classe comme "info"
    return "info"

# === Fonction pour extraire un utilisateur à partir d'une ligne de log ===
def extract_user(line):
    match = re.search(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d+\s+\d+\s+(INFO|ERROR|WARNING)\s+(\w+)", line, re.IGNORECASE)
    if match:
        return match.group(2).lower()
    return "unknown"
                                                                                                        # Si aucun utilisateur trouvé, retourne "unknown"

# === Lire le fichier log ligne par ligne ===
try:
    with open("odoo.log.txt", "r", encoding="utf-8") as f:
                                                                                                        # On lit toutes les lignes et on enlève les lignes vides avec strip()
        lines = [line.strip() for line in f if line.strip()]
except FileNotFoundError:
                                                                                                        # Si le fichier n'existe pas, afficher une erreur et arrêter le programme
    print("Erreur : fichier odoo.log introuvable.")
    exit(1)

# === Créer un dictionnaire pour compter les logs par utilisateur et par catégorie ===
user_stats = defaultdict(lambda: {"error": 0, "warning": 0, "info": 0})

# === Parcourir chaque ligne et mettre à jour les statistiques ===
for line in lines:
    category = categorize_log(line)  # Déterminer la catégorie (info, warning, error)
    user = extract_user(line)  # Extraire l’utilisateur responsable
    user_stats[user][category] += 1  # Incrémenter le compteur correspondant

# === Préparer les données pour le graphique ===
users = sorted(user_stats.keys())  # Liste triée des utilisateurs
categories = ["error", "warning", "info"]  # Types de logs à afficher
colors = {  # Définition de couleurs personnalisées pour chaque catégorie
    "error": "#E74C3C",
    "warning": "#F1C40F",
    "info": "#3498DB"
}

x = range(len(users))  # Positions sur l’axe X pour chaque utilisateur
bar_width = 0.2  # Largeur des barres dans l’histogramme

plt.figure(figsize=(14, 6))  # Définir la taille du graphique

# === Affichage de chaque catégorie sous forme de barres empilées ===
for i, cat in enumerate(categories):
    # Récupère les valeurs (nombre de logs) pour chaque utilisateur pour cette catégorie
    values = [user_stats[user][cat] for user in users]
    # Affiche les barres correspondantes avec décalage selon la catégorie
    plt.bar([x_pos + i * bar_width for x_pos in x], values,
            width=bar_width, label=cat.upper(), color=colors[cat])

# === Configuration de l’axe X et des labels ===
plt.xticks([x_pos + bar_width for x_pos in x], users, rotation=45)  # Positionne les labels utilisateurs
plt.ylabel("Nombre de logs")  # Légende de l’axe Y
plt.title("Nombre de logs par utilisateur et par type (INFO / WARNING / ERROR)", weight="bold")  # Titre
plt.legend()  # Affiche la légende des couleurs
plt.grid(axis="y", linestyle="--", alpha=0.3)  # Grille horizontale pour meilleure lisibilité
plt.tight_layout()  # Ajuste automatiquement les marges pour ne pas couper les éléments
plt.show()  # Affiche le graphique à l’écran
