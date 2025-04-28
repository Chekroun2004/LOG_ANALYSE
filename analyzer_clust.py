# analyzer_hierarchical.py - Version améliorée

import matplotlib.pyplot as plt
import re
from collections import defaultdict

# Constantes améliorées
LINE_SPACING = 3.0
PADDING_BETWEEN_USERS = 20
LEVEL_SPACING = 5.0
MARGIN = 15
MAX_MSG_LEN = 80
BLOCK_PADDING = 2.0  # Ajout de cette nouvelle constante

COLORS = {
    'user': '#4b8bbe',
    'error': '#ff6b6b',
    'warning': '#ffd166',
    'info': '#7fb800',
    'message': '#f7f7f7'
}

def parse_logs(filepath):
    """Version plus robuste du parsing"""
    pattern = re.compile(
        r"(?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}) "
        r"(?P<pid>\d+) "
        r"(?P<level>[A-Z]+) "
        r"(?P<user>\w+) "
        r"(?P<module>[\w\.]+): "
        r"(?P<message>.+)"
    )

    logs = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
    
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            for line in f:
                if match := pattern.match(line):
                    data = match.groupdict()
                    msg = re.sub(r"\b\d+\b", "#", data["message"])  # Meilleure normalisation
                    logs[data["user"]][data["level"]][msg].append(data["message"])
    except Exception as e:
        print(f"Erreur de lecture: {str(e)}")
    
    return logs

def get_block_height(data):
    """Version optimisée"""
    height = sum(
        len(v) if isinstance(v, list) else 
        max(get_block_height(v), 1) if isinstance(v, dict) else 
        1 for v in data.values()
    )
    return max(height, 2)

def draw_bracket(ax, data, x=0, y=0, depth=0):
    """Version améliorée avec gestion de profondeur"""
    y_cursor = y
    
    for key, val in data.items():
        # Détermination de la couleur
        if depth == 0:
            color = COLORS['user']
        else:
            color = COLORS.get(key.lower(), COLORS['info'])
        
        # Création du label
        if isinstance(val, dict):
            count = sum(len(v) for v in val.values() if isinstance(v, list))
            label = f"{key} ({count})"
        else:
            label = key
        
        # Dessin du noeud
        ax.text(x, y_cursor, label,
                ha="left", va="center",
                fontsize=10 - depth,  # Taille de police relative à la profondeur
                bbox=dict(boxstyle="round",
                         facecolor=color,
                         edgecolor="black",
                         alpha=0.8))
        
        # Traitement des enfants
        if isinstance(val, dict):
            child_x = x + LEVEL_SPACING
            block_height = get_block_height(val) * LINE_SPACING
            draw_bracket(ax, val, child_x, y_cursor, depth + 1)
            y_cursor -= block_height + BLOCK_PADDING
            
        elif isinstance(val, list):
            for i, msg in enumerate(val):
                leaf_y = y_cursor - i * LINE_SPACING
                msg_display = msg[:MAX_MSG_LEN//2] + "..." + msg[-MAX_MSG_LEN//2:] if len(msg) > MAX_MSG_LEN else msg
                
                ax.text(x + LEVEL_SPACING, leaf_y, msg_display,
                        fontsize=9,
                        color='#333',
                        va='center',
                        bbox=dict(boxstyle="round",
                                 facecolor=COLORS['message'],
                                 edgecolor="#ddd",
                                 pad=0.3))
                
                ax.plot([x + 1, x + LEVEL_SPACING - 1], [y_cursor, leaf_y],
                        ':', color='#999', lw=0.8)
            
            y_cursor -= len(val) * LINE_SPACING

if __name__ == "__main__":
    # Chargement des données
    logs = parse_logs("odoo.log.txt")
    
    # Calcul des dimensions
    total_lines = sum(get_block_height(c) + PADDING_BETWEEN_USERS for c in logs.values())
    total_height = total_lines * LINE_SPACING + MARGIN
    
    # Création de la figure
    fig_height = max(10, min(30, total_height / 4))
    fig, ax = plt.subplots(figsize=(28, fig_height))
    ax.set_xlim(0, 30)  # Espace horizontal augmenté
    ax.set_ylim(-total_height, 10)
    ax.axis('off')
    
    # Dessin
    current_y = 0
    for user, content in logs.items():
        draw_bracket(ax, {user: content}, y=current_y)
        current_y -= (get_block_height(content) + PADDING_BETWEEN_USERS) * LINE_SPACING
    
    # Finalisation
    plt.title("Analyse Hiérarchique des Logs Odoo\nPar Utilisateur → Niveau → Message", 
              pad=20, fontsize=16, fontweight='bold')
    plt.tight_layout()
    
    # Sauvegarde
    output_file = "odoo_logs_hierarchy.png"
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"Visualisation sauvegardée dans '{output_file}'")
    plt.show()