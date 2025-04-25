# analyzer_clust.py
import re
import os
import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from collections import defaultdict
import json
from datetime import datetime

# Configuration
LOG_FILE = "odoo.log.txt"
OUTPUT_DIR = "results"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def setup_logging():
    """Configure le chemin des fichiers"""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    chemin_log = os.path.join(base_dir, LOG_FILE)
    
    print(f"[CONFIG] Dossier de travail : {base_dir}")
    print(f"[CONFIG] Fichier de log : {chemin_log}")
    
    if not os.path.exists(chemin_log):
        print(f"[ERREUR] Fichier '{chemin_log}' introuvable")
        exit(1)
        
    return chemin_log

def parse_logs(file_path):
    """Parse les logs Odoo avec gestion des erreurs améliorée"""
    pattern = re.compile(
        r'^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d+)\s+(\d+)\s+(\w+)\s+(\w+)\s+([\w\.]+):\s+(.*)'
    )
    
    logs = []
    current_log = None
    
    with open(file_path, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
                
            match = pattern.match(line)
            if match:
                if current_log:
                    logs.append(current_log)
                
                timestamp, pid, level, user, module, message = match.groups()
                current_log = {
                    'line': line_num,
                    'timestamp': timestamp,
                    'level': level,
                    'user': user,
                    'module': module,
                    'message': message
                }
            elif current_log:
                current_log['message'] += '\n' + line
            else:
                print(f"[WARN] Ligne {line_num} ignorée (format non reconnu)")
    
    if current_log:
        logs.append(current_log)
        
    print(f"[SUCCÈS] {len(logs)} logs parsés")
    return logs

def cluster_logs(logs, n_clusters=5):
    """Clusterisation des logs avec paramètres optimisés"""
    vectorizer = TfidfVectorizer(
        max_features=1000,
        stop_words='english',
        ngram_range=(1, 2)  # <-- Parenthèse fermée ici
    )  # <-- Et ici pour fermer l'appel à TfidfVectorizer
    
    X = vectorizer.fit_transform([log['message'] for log in logs])
    
    kmeans = KMeans(
        n_clusters=n_clusters,
        init='k-means++',
        max_iter=300,
        random_state=42
    ).fit(X)  # <-- Parenthèse fermée ici
    
    for i, log in enumerate(logs):
        log['cluster'] = int(kmeans.labels_[i])
    
    return logs, X, vectorizer

def analyze_clusters(logs):
    """Analyse approfondie des clusters"""
    analysis = {
        'cluster_stats': defaultdict(lambda: defaultdict(int)),
        'error_patterns': defaultdict(set)
    }
    
    for log in logs:
        cluster = log['cluster']
        analysis['cluster_stats'][cluster]['total'] += 1
        analysis['cluster_stats'][cluster][log['level']] += 1
        
        if log['level'] == 'ERROR':
            analysis['error_patterns'][cluster].add(
                ' '.join(log['message'].split()[:5]))
    
    return analysis

def visualize_results(logs, X):
    """Visualisation améliorée des clusters"""
    pca = PCA(n_components=2).fit_transform(X.toarray())
    
    plt.figure(figsize=(12, 8))
    for cluster in set(log['cluster'] for log in logs):
        indices = [i for i, log in enumerate(logs) if log['cluster'] == cluster]
        plt.scatter(
            pca[indices, 0], pca[indices, 1],
            label=f'Cluster {cluster}',
            alpha=0.6)
    
    plt.title("Clustering des Logs Odoo\nAnalyse PCA", pad=20)
    plt.xlabel("Composante Principale 1")
    plt.ylabel("Composante Principale 2")
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.grid(alpha=0.2)
    plt.tight_layout()
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = os.path.join(OUTPUT_DIR, f"clusters_{timestamp}.png")
    plt.savefig(output_file, dpi=120, bbox_inches='tight')
    plt.show()
    print(f"[VISUALISATION] Graphique sauvegardé dans {output_file}")

def export_results(logs, analysis):
    """Export des résultats en JSON"""
    output = {
        'metadata': {
            'timestamp': datetime.now().isoformat(),
            'total_logs': len(logs),
            'clusters_count': len(analysis['cluster_stats'])
        },
        'clusters': analysis['cluster_stats'],
        'error_patterns': {k: list(v) for k, v in analysis['error_patterns'].items()},
        'sample_logs': []
    }
    
    # Ajout d'exemples de logs pour chaque cluster
    for cluster in output['clusters']:
        sample = next(log for log in logs if log['cluster'] == cluster)
        output['sample_logs'].append({
            'cluster': cluster,
            'line': sample['line'],
            'level': sample['level'],
            'message': sample['message'][:200]
        })
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = os.path.join(OUTPUT_DIR, f"analysis_{timestamp}.json")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print(f"[EXPORT] Résultats exportés dans {output_file}")

if __name__ == "__main__":
    try:
        # 1. Configuration
        log_file = setup_logging()
        
        # 2. Parsing des logs
        logs = parse_logs(log_file)
        if not logs:
            raise ValueError("Aucun log valide à analyser")
        
        # 3. Clusterisation
        logs, X, vectorizer = cluster_logs(logs)
        
        # 4. Analyse
        analysis = analyze_clusters(logs)
        
        # 5. Visualisation
        visualize_results(logs, X)
        
        # 6. Export
        export_results(logs, analysis)
        
        print("\n[TERMINÉ] Analyse complétée avec succès!")
        
    except Exception as e:
        print(f"\n[ERREUR] {str(e)}")
        exit(1)