import re
import os
import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA

# Toujours trouver le fichier par rapport au script
base_dir = os.path.dirname(os.path.abspath(__file__))
chemin_log = os.path.join(base_dir, "odoo.log")

print(f"[DEBUG] Chemin du log utilisé : {chemin_log}")

if not os.path.exists(chemin_log):
    print(f"[ERREUR] Le fichier '{chemin_log}' est introuvable.")
    exit(1)


def lire_logs_odoo(fichier):
    """
    Lit un fichier de logs Odoo et extrait les messages structurés, y compris les logs multi-lignes (ex: stacktrace).
    :param fichier: Chemin vers le fichier log Odoo.
    :return: Liste de dictionnaires (timestamp, niveau, source, message complet).
    """
    debut_log_pattern = re.compile(
        r'^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d+)\s+\d+\s+(\w+)\s+([^\s:]+):\s+(.*)'
    )

    logs = []
    log_en_cours = None

    try:
        with open(fichier, 'r', encoding='utf-8') as f:
            for ligne in f:
                ligne = ligne.rstrip()
                match = debut_log_pattern.match(ligne)

                if match:
                    if log_en_cours:
                        logs.append(log_en_cours)

                    timestamp, niveau, source, message = match.groups()
                    log_en_cours = {
                        'timestamp': timestamp,
                        'niveau': niveau,
                        'source': source,
                        'message': message
                    }
                else:
                    if log_en_cours:
                        log_en_cours['message'] += '\n' + ligne
                    else:
                        print(f"[WARN] Ligne isolée ignorée : {ligne[:80]}...")

            if log_en_cours:
                logs.append(log_en_cours)

        print(f"[INFO] {len(logs)} logs extraits avec succès.")
        return logs

    except Exception as e:
        print(f"[ERREUR] Problème lors de la lecture du fichier : {e}")
        return []


def kmeans_sur_logs(logs, n_clusters=3):
    """
    Applique le clustering KMeans sur les messages de logs.
    """
    messages = [log['message'] for log in logs]
    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(messages)

    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    kmeans.fit(X)

    for i, log in enumerate(logs):
        log['cluster'] = int(kmeans.labels_[i])

    return logs, X


def visualiser_clusters(logs, X):
    """
    Affiche les clusters en 2D (réduction par PCA).
    """
    if X.shape[0] < 2:
        print("Pas assez de données pour afficher un graphique.")
        return

    pca = PCA(n_components=2)
    donnees_reduites = pca.fit_transform(X.toarray())

    couleurs = ['red', 'blue', 'green', 'purple', 'orange']
    plt.figure(figsize=(10, 6))

    labels_déjà_vus = set()
    for i, log in enumerate(logs):
        cluster_id = log['cluster']
        label = f"Cluster {cluster_id}"
        if label not in labels_déjà_vus:
            plt.scatter(donnees_reduites[i, 0], donnees_reduites[i, 1],
                        color=couleurs[cluster_id % len(couleurs)],
                        label=label)
            labels_déjà_vus.add(label)
        else:
            plt.scatter(donnees_reduites[i, 0], donnees_reduites[i, 1],
                        color=couleurs[cluster_id % len(couleurs)])

    plt.title("Clustering des logs Odoo")
    plt.xlabel("Composante principale 1")
    plt.ylabel("Composante principale 2")
    plt.legend()
    plt.grid(True)
    plt.show()


# === Exécution principale ===
if __name__ == "__main__":
    logs = lire_logs_odoo(chemin_log)

    if not logs:
        print("[INFO] Aucun log reconnu, arrêt du programme.")
        exit(1)

    for i, log in enumerate(logs[:5]):  # Affiche les 5 premiers logs
        print(f"\n--- Log {i+1} ---")
        print(f"[{log['timestamp']}] {log['niveau']} - {log['source']}")
        print(log['message'])

    try:
        logs_clusterises, matrice_vecteurs = kmeans_sur_logs(logs, n_clusters=3)
        visualiser_clusters(logs_clusterises, matrice_vecteurs)
    except Exception as e:
        print(f"[ERREUR] : {e}")
