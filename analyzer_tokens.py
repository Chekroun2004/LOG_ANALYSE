# analyzer_tokens.py - Script d'analyse des logs Odoo par utilisateur et type

# Importation du module re pour les expressions régulières
import re
# Importation de defaultdict pour créer des dictionnaires avec valeurs par défaut
from collections import defaultdict
# Importation de pyplot pour la génération de graphiques
import matplotlib.pyplot as plt
# Importation du module sys pour la gestion des sorties du programme
import sys
# Importation du module json pour la manipulation de fichiers JSON
import json

# Compilation d'une regex pour détecter les mots-clés d'erreur (optimisation des performances)
ERROR_KEYWORDS = re.compile(r"error|exception|failed")
# Compilation d'une regex pour détecter les warnings
WARNING_KEYWORDS = re.compile(r"warning")
# Compilation d'une regex pour extraire l'utilisateur des logs Odoo
USER_PATTERN = re.compile(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d+\s+\d+\s+(INFO|ERROR|WARNING)\s+(\w+)")

def categorize_log(line):
    """Fonction de catégorisation des lignes de log"""
    # Conversion en minuscules pour une comparaison insensible à la casse
    line_lower = line.lower()
    
    # Vérification des faux positifs (messages contenant "no error" etc.)
    if "no error" in line_lower or "without error" in line_lower:
        return "info"  # Classé comme info si c'est un faux positif
    
    # Recherche des motifs d'erreur
    if ERROR_KEYWORDS.search(line_lower):
        return "error"  # Classé comme erreur si motif trouvé
    
    # Recherche des warnings
    elif WARNING_KEYWORDS.search(line_lower):
        return "warning"  # Classé comme warning si motif trouvé
    
    # Par défaut, classé comme info
    return "info"

def extract_user(line):
    """Fonction d'extraction du nom d'utilisateur"""
    # Application de la regex pour trouver l'utilisateur
    match = USER_PATTERN.search(line)
    # Retourne le nom d'utilisateur en minuscules si trouvé, sinon "unknown"
    return match.group(2).lower() if match else "unknown"

def main():
    """Fonction principale du script"""
    try:
        # Ouverture du fichier de logs en lecture avec encodage UTF-8
        with open("odoo.log.txt", "r", encoding="utf-8") as f:
            # Lecture et nettoyage des lignes (suppression des espaces et lignes vides)
            lines = [line.strip() for line in f if line.strip()]
        
        # Vérification si le fichier est vide
        if not lines:
            print("Aucun log à analyser : le fichier est vide.")
            sys.exit(0)  # Sortie propre du programme
    
    except FileNotFoundError:
        # Gestion de l'erreur si le fichier n'existe pas
        print("Erreur : fichier odoo.log.txt introuvable.")
        sys.exit(1)  # Sortie avec code d'erreur
    except UnicodeDecodeError:
        # Gestion des problèmes d'encodage
        print("Erreur : problème d'encodage (utilisez UTF-8).")
        sys.exit(1)  # Sortie avec code d'erreur

    # Initialisation d'un dictionnaire pour les statistiques par utilisateur
    # Format: {user: {"error": count, "warning": count, "info": count}}
    user_stats = defaultdict(lambda: {"error": 0, "warning": 0, "info": 0})
    
    # Analyse ligne par ligne
    for line in lines:
        # Catégorisation de la ligne (error/warning/info)
        category = categorize_log(line)
        # Extraction du nom d'utilisateur
        user = extract_user(line)
        # Incrémentation du compteur approprié
        user_stats[user][category] += 1

    # Préparation des données pour le graphique
    users = sorted(user_stats.keys())  # Liste triée des utilisateurs
    categories = ["error", "warning", "info"]  # Types de logs à afficher
    # Couleurs associées à chaque catégorie (rouge, jaune, bleu)
    colors = {"error": "#E74C3C", "warning": "#F1C40F", "info": "#3498DB"}

    # Création d'une nouvelle figure avec une taille spécifique (14x6 pouces)
    plt.figure(figsize=(14, 6))
    
    # Création des barres pour chaque catégorie
    for i, cat in enumerate(categories):
        # Récupération des valeurs pour chaque utilisateur
        values = [user_stats[user][cat] for user in users]
        # Dessin des barres avec décalage pour chaque catégorie
        plt.bar(
            [x + i * 0.2 for x in range(len(users))],  # Position horizontale
            values,                                    # Hauteur des barres
            width=0.2,                                # Largeur des barres
            label=cat.upper(),                        # Libellé pour la légende
            color=colors[cat]                         # Couleur associée
        )
    
    # Configuration de l'axe X (noms d'utilisateurs)
    plt.xticks(
        [x + 0.2 for x in range(len(users))],  # Positions des ticks
        users,                                 # Étiquettes
        rotation=45                           # Rotation des étiquettes
    )
    
    # Ajout du label de l'axe Y
    plt.ylabel("Nombre de logs")
    # Ajout du titre du graphique (en gras)
    plt.title("Logs Odoo par utilisateur et type", weight="bold")
    # Affichage de la légende
    plt.legend()
    # Ajout d'une grille horizontale (style pointillé, semi-transparente)
    plt.grid(axis="y", linestyle="--", alpha=0.3)
    # Ajustement automatique de la mise en page
    plt.tight_layout()
    # Sauvegarde du graphique en PNG
    plt.savefig("log_report.png")
    # Affichage du graphique
    plt.show()

    # Sauvegarde des statistiques au format JSON
    with open("user_stats.json", "w") as f:
        # Écriture avec indentation pour une meilleure lisibilité
        json.dump(user_stats, f, indent=4)
    
    # Message de confirmation
    print("Terminé ! Rapport sauvegardé dans log_report.png et user_stats.json")

# Point d'entrée principal du script
if __name__ == "__main__":
    main()