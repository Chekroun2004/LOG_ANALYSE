# 🔍 LOG_ANALYSE — Odoo Log Analysis Pipeline

[![Python](https://img.shields.io/badge/Python-3.8+-3776AB?logo=python&logoColor=white)](https://python.org)
[![scikit-learn](https://img.shields.io/badge/scikit--learn-1.x-F7931E?logo=scikit-learn&logoColor=white)](https://scikit-learn.org)
[![matplotlib](https://img.shields.io/badge/matplotlib-3.x-11557C?logo=python&logoColor=white)](https://matplotlib.org)
[![License](https://img.shields.io/badge/license-academic-green)](#license)

Multi-module Python pipeline for analyzing **Odoo ERP logs** — combining regex pattern matching, tokenization, hierarchical clustering, and KMeans (TF-IDF + PCA) to detect anomalies and visualize log behavior by user and severity.

---

## Features

| Module | Description |
|---|---|
| `analyzer_pattern.py` | Regex-based anomaly detection against a configurable known-pattern database |
| `analyzer_tokens.py` | Per-user log statistics (ERROR / WARNING / INFO) with grouped bar chart |
| `analyzer_clust.py` | Hierarchical tree visualization — user → severity level → message |
| `analyzer_kmeans.py` | KMeans clustering of log messages via TF-IDF vectorization + PCA projection |

---

## Stack

- **Python 3.8+** — core language
- **scikit-learn** — TF-IDF vectorization, KMeans, PCA
- **matplotlib** — all visualizations
- **re / json / collections** — log parsing and config handling

---

## Architecture

```
odoo.log.txt  (input)
      │
      ├── analyzer_pattern.py  ──→  anomalies_report.txt
      ├── analyzer_tokens.py   ──→  log_report.png  ·  user_stats.json
      ├── analyzer_clust.py    ──→  odoo_logs_hierarchy.png
      └── analyzer_kmeans.py   ──→  results/clusters_*.png  ·  results/analysis_*.json

Config files: known_anomalies.json  ·  false_positives.json
```

---

## Quick Start

```bash
# 1. Install dependencies
pip install scikit-learn matplotlib

# 2. Place your Odoo log file
cp your_odoo_file.log odoo.log.txt

# 3. Run any analyzer
python analyzer_pattern.py    # Anomaly detection
python analyzer_tokens.py     # Per-user statistics
python analyzer_clust.py      # Hierarchical visualization
python analyzer_kmeans.py     # KMeans clustering
```

---

## Repo Layout

```
LOG_ANALYSE/
├── analyzer_pattern.py       # Pattern matching & anomaly detection
├── analyzer_tokens.py        # Tokenization & per-user stats
├── analyzer_clust.py         # Hierarchical log tree
├── analyzer_kmeans.py        # KMeans + TF-IDF + PCA
├── known_anomalies.json      # Known error patterns (config)
├── false_positives.json      # False positive exclusions (config)
├── odoo.log.txt              # Sample Odoo log (input)
└── results/                  # Generated outputs (charts, JSON reports)
```

---

## Sample Outputs

| Output | Description |
|---|---|
| `anomalies_report.txt` | Detected anomalies with line numbers and matched patterns |
| `log_report.png` | Grouped bar chart — log counts per user by severity |
| `odoo_logs_hierarchy.png` | Hierarchical tree — user → level → deduplicated messages |
| `results/clusters_*.png` | KMeans PCA scatter plot per run |
| `results/analysis_*.json` | Cluster statistics export |
| `user_stats.json` | Per-user error / warning / info counters |

---

## Authors

**Omar Chekroun** & **Haytam Belghali** — PFE Licence SMI, Faculté des Sciences, Université Mohammed V de Rabat
[![GitHub](https://img.shields.io/badge/GitHub-Chekroun2004-181717?logo=github)](https://github.com/Chekroun2004)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-omar--chekroun-0A66C2?logo=linkedin)](https://linkedin.com/in/omar-chekroun)

---

## License

Internal academic project — UM5 Rabat. Not licensed for commercial use.
