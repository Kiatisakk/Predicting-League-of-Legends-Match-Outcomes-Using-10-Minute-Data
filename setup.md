# 🛠️ Setup Guide

## Prerequisites

- **Python 3.9+** installed
- **pip** package manager
- **Kaggle account** (free) — [Sign up here](https://www.kaggle.com/)

---

## 1. Clone the Repository

```bash
git clone https://github.com/Kiatisakk/Predicting-League-of-Legends-Match-Outcomes-Using-10-Minute-Data.git
cd Predicting-League-of-Legends-Match-Outcomes-Using-10-Minute-Data
```

---

## 2. Install Dependencies

```bash
pip install pandas numpy scikit-learn matplotlib seaborn kaggle
```

---

## 3. Set Up Kaggle API Credentials

The dataset is hosted on Kaggle. You need an API token to download it.

1. Go to [https://www.kaggle.com/settings](https://www.kaggle.com/settings)
2. Scroll down to the **API** section
3. Click **"Create New Token"** — this will download a file called `kaggle.json`
4. Place the file in your Kaggle config directory:

| OS | Path |
|---|---|
| **Windows** | `C:\Users\<YourUsername>\.kaggle\kaggle.json` |
| **macOS / Linux** | `~/.kaggle/kaggle.json` |

> **Note:** Create the `.kaggle` folder manually if it doesn't exist.

---

## 4. Download the Dataset

Run the setup script to automatically download and extract the data:

```bash
python setup_data.py
```

This will download the dataset from [Kaggle: cpe232-lol-10min-dataset](https://www.kaggle.com/datasets/kiatisakkk/cpe232-lol-10min-dataset) into the `data/` folder.

### Manual Download (Alternative)

If the script doesn't work, you can download manually:

1. Visit [https://www.kaggle.com/datasets/kiatisakkk/cpe232-lol-10min-dataset](https://www.kaggle.com/datasets/kiatisakkk/cpe232-lol-10min-dataset)
2. Click **"Download"** button
3. Extract the ZIP file into the `data/` folder of this project

---

## 5. Verify the Setup

After downloading, your project structure should look like this:

```
📁 Predicting-Match-Result-LOL-DataModels/
├── 📄 01_data_merging.ipynb
├── 📄 03_modeling.ipynb
├── 📄 setup_data.py
├── 📄 setup.md              ← You are here
├── 📄 .gitignore
└── 📁 data/
    ├── 📁 t1_raw/
    │   ├── 📁 match_details/
    │   │   ├── MatchStatsTbl.csv
    │   │   ├── MatchTbl.csv
    │   │   ├── SummonerMatchTbl.csv
    │   │   └── TeamMatchTbl.csv
    │   └── 📁 metadata/
    │       ├── ChampionTbl.csv
    │       ├── ItemTbl.csv
    │       ├── KeystoneTbl.csv
    │       ├── RankTbl.csv
    │       └── SummonerSpellTbl.csv
    └── 📁 t2_transformed/
        └── merged_v1.csv
```

---

## 6. Run the Notebooks

Open the notebooks in order:

1. **`01_data_merging.ipynb`** — Merges raw CSV tables into a single dataset
2. **`03_modeling.ipynb`** — Trains and evaluates ML models for match prediction

```bash
jupyter notebook
```

---

## Troubleshooting

| Problem | Solution |
|---|---|
| `kaggle: command not found` | Run `pip install kaggle` |
| `403 - Forbidden` when downloading | Make sure `kaggle.json` is in the correct folder |
| `OSError: Could not find kaggle.json` | See Step 3 above |
| Large file error on `git push` | The `data/` folder is in `.gitignore` — do **not** remove it |
