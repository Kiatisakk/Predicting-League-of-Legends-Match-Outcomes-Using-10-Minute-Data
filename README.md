# 🎮 Predicting League of Legends Match Outcomes Using 10-Minute Data

<div align="center">

![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![scikit-learn](https://img.shields.io/badge/scikit--learn-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white)
![XGBoost](https://img.shields.io/badge/XGBoost-189FDD?style=for-the-badge&logo=xgboost&logoColor=white)
![LightGBM](https://img.shields.io/badge/LightGBM-02569B?style=for-the-badge&logo=lightgbm&logoColor=white)
![CatBoost](https://img.shields.io/badge/CatBoost-FFCC00?style=for-the-badge&logoColor=black)
![Pandas](https://img.shields.io/badge/Pandas-150458?style=for-the-badge&logo=pandas&logoColor=white)
![Jupyter](https://img.shields.io/badge/Jupyter-F37626?style=for-the-badge&logo=jupyter&logoColor=white)

**โมเดล Machine Learning สำหรับทำนายผลแพ้ชนะของเกม League of Legends จากข้อมูลสถานะเกมช่วง 10 นาทีแรก**

[📊 ผลลัพธ์](#-result-summary) · [🚀 เริ่มต้นใช้งาน](#-getting-started) · [📓 Kaggle Notebooks](#-kaggle-notebooks)

</div>

---

## 📋 Table of Contents

- [Project Overview](#-project-overview)
- [Project Objective](#-project-objective)
- [Dataset](#-dataset)
- [Notebook Pipeline](#-notebook-pipeline)
- [Data Flow](#-data-flow)
- [Feature Engineering Strategy](#-feature-engineering-strategy)
- [Models](#-models)
- [Result Summary](#-result-summary)
- [Key Findings](#-key-findings)
- [Project Structure](#-project-structure)
- [Getting Started](#-getting-started)
- [Kaggle Notebooks](#-kaggle-notebooks)

---

## 🔍 Project Overview

โปรเจคนี้เป็นการวิเคราะห์และสร้างโมเดล Machine Learning สำหรับทำนายผลแพ้ชนะของเกม **League of Legends** จากข้อมูลสถานะเกมใน **10 นาทีแรก** โดยใช้ข้อมูลหลากหลายด้าน ได้แก่ economy (gold, CS), combat (kills, KDA, damage), objective control (dragon, herald), champion composition และ player setup (summoner spells, keystones, lanes) เพื่อเปรียบเทียบว่า feature แต่ละกลุ่มส่งผลต่อประสิทธิภาพของโมเดลมากน้อยเพียงใด

> **แนวคิดหลัก:** ข้อมูลในช่วง 10 นาทีแรกของเกมสะท้อนสถานะสำคัญ เช่น gold lead, CS lead, kill lead, objective control และ damage output ซึ่งสามารถใช้ประเมินความได้เปรียบของแต่ละทีมและทำนายผลลัพธ์ของเกมได้

---

## 🎯 Project Objective

| หัวข้อ | รายละเอียด |
|---|---|
| **เป้าหมาย** | ทำนายว่า **Blue Team จะชนะหรือไม่** จากข้อมูลในช่วงต้นเกม (10 นาทีแรก) |
| **Primary Metric** | `AUC-ROC` — วัดความสามารถในการจำแนกคลาสโดยรวม |
| **Supporting Metrics** | `Accuracy` และ `F1-Score` — วัดความแม่นยำและความสมดุลระหว่าง precision/recall |
| **การเปรียบเทียบ** | เปรียบเทียบ 3 ระดับ feature set × 6 โมเดล เพื่อหาส่วนผสมที่ดีที่สุด |

---

## 📁 Dataset

- **แหล่งข้อมูล:** [Kaggle — cpe232-lol-10min-dataset](https://www.kaggle.com/datasets/kiatisakkk/cpe232-lol-10min-dataset)
- **ระดับข้อมูล:** Match-level (หนึ่งแถวต่อหนึ่งเกม) หลังจาก merge จาก raw tables
- **Raw Tables:**

| Table | คำอธิบาย |
|---|---|
| `MatchTbl.csv` | ข้อมูลทั่วไปของแมตช์ |
| `MatchStatsTbl.csv` | สถิติรายละเอียดของแมตช์ |
| `SummonerMatchTbl.csv` | ข้อมูลผู้เล่นแต่ละคนในแมตช์ |
| `TeamMatchTbl.csv` | ข้อมูลระดับทีม |
| `ChampionTbl.csv` | ข้อมูล champion metadata |
| `KeystoneTbl.csv` | ข้อมูล keystone rune |
| `SummonerSpellTbl.csv` | ข้อมูล summoner spell |

---

## 📓 Notebook Pipeline

ให้รัน notebook ตามลำดับดังนี้:

```
01 → 02 → 03 → 04 → 05 → 06
```

| # | Notebook | จุดประสงค์ |
|:---:|---|---|
| 1 | `01_data_merging.ipynb` | รวม raw tables หลายไฟล์ให้เป็น match-level dataset (หนึ่งแถวต่อหนึ่งเกม) |
| 2 | `02_EDA.ipynb` | สำรวจ (EDA) ความสัมพันธ์ของ gold, CS, kills, KDA, objectives, damage และ lane matchup กับผลแพ้ชนะ |
| 3 | `03_baseline_model_kaggle.ipynb` | สร้าง **baseline** ด้วย Logistic Regression จาก raw encoded features (ไม่ทำ feature engineering หลัก) |
| 4 | `04_modeling_aggregate_only_kaggle.ipynb` | เทรนและ tune โมเดลด้วย **aggregate/team-level** + difference features |
| 5 | `05_modeling_all_features_kaggle.ipynb` | เทรนและ tune โมเดลด้วย aggregate features **รวมกับ** champion/setup features |
| 6 | `06_result_summary.ipynb` | รวมผลลัพธ์จาก notebook 03, 04, 05 เพื่อสรุป model comparison, improvement และ feature importance |

---

## 🔄 Data Flow

```mermaid
graph TD
    A[📥 Raw CSV Tables<br/>data/t1_raw/] --> B[01 Data Merging<br/>รวมข้อมูลผู้เล่น + ทีม]
    B --> C[📄 merged_v1.csv<br/>data/t2_transformed/]
    C --> D[02 EDA<br/>สำรวจ signal สำคัญ]
    D --> E[03 Baseline<br/>Logistic Regression]
    D --> F[04 Aggregate-only<br/>6 Models + Tuning]
    D --> G[05 All-features<br/>6 Models + Tuning]
    E --> H[06 Result Summary<br/>สรุปผลข้าม experiments]
    F --> H
    G --> H
    H --> I[📊 outputs/final_summary/]
```

---

## 🧪 Feature Engineering Strategy

โปรเจคนี้แบ่งการทดลอง modeling เป็น **3 ระดับ** เพื่อเปรียบเทียบผลกระทบของ feature แต่ละกลุ่ม:

| Experiment | Feature Set | คำอธิบาย | ตัวอย่าง Features |
|---|---|---|---|
| 🔹 **Baseline** | Raw encoded features | ใช้ข้อมูลที่ encode แล้วแบบพื้นฐาน ไม่เน้น feature engineering | `TotalGold_P1`, `MinionsKilled_P7`, ... |
| 🔸 **Aggregate-only** | Team-level + difference features | รวม feature ระดับทีมและสร้าง diff features | `Diff_TotalGold`, `Diff_Kills`, `Blue_KDA_avg`, ... |
| 🔶 **All-features** | Aggregate + champion/setup | เพิ่ม champion composition, summoner spell, keystone และ lane features | + `Champion_*`, `PrimaryKeyStone_*`, `Lane_*` |

---

## 🤖 Models

โมเดลที่ใช้ในทุก experiment (ยกเว้น baseline ที่ใช้เฉพาะ Logistic Regression):

| โมเดล | ประเภท | หมายเหตุ |
|---|---|---|
| **Logistic Regression** | Linear | ใช้เป็น baseline หลัก — ตีความ coefficient ได้ง่าย เหมาะกับ difference features |
| **Decision Tree** | Tree-based | เรียบง่าย แต่มักจะ overfit |
| **Random Forest** | Ensemble (Bagging) | ลด variance จาก Decision Tree |
| **XGBoost** | Ensemble (Boosting) | Gradient boosting ที่ได้รับความนิยมสูง |
| **LightGBM** | Ensemble (Boosting) | เร็วกว่า XGBoost ในหลายกรณี |
| **CatBoost** | Ensemble (Boosting) | จัดการ categorical features ได้ดี — **ได้ผลดีที่สุดในโปรเจคนี้** |

ทุกโมเดลถูก tune hyperparameters ด้วย cross-validation และประเมินผลบน test set ที่แยกไว้

---

## 📊 Result Summary

### Best Model per Experiment

| Experiment | Best Model | Test AUC | Test Accuracy | Test F1 |
|---|---|---:|---:|---:|
| Baseline (raw encoded) | Logistic Regression | 0.7828 | 0.7053 | 0.7028 |
| Aggregate-only | CatBoost | 0.7822 | 0.7031 | 0.6994 |
| **All-features** | **CatBoost** | **0.7989** | **0.7160** | **0.7131** |

### All Models — All-features Experiment (Best Experiment)

| Model | Val AUC | Test AUC | Test Accuracy | Test F1 | Rank |
|---|---:|---:|---:|---:|:---:|
| **CatBoost** | **0.7933** | **0.7989** | **0.7160** | **0.7131** | 🥇 |
| LightGBM | 0.7921 | 0.7980 | 0.7158 | 0.7128 | 🥈 |
| XGBoost | 0.7929 | 0.7975 | 0.7143 | 0.7106 | 🥉 |
| Logistic Regression | 0.7927 | 0.7971 | 0.7174 | 0.7157 | 4 |
| Random Forest | 0.7721 | 0.7807 | 0.7023 | 0.6981 | 5 |
| Decision Tree | 0.7659 | 0.7755 | 0.6996 | 0.6911 | 6 |

### Improvement Summary

| เปรียบเทียบ | Δ Test AUC |
|---|---:|
| All-features vs Baseline | **+0.0161** |
| All-features vs Aggregate-only | **+0.0166** |
| Aggregate-only vs Baseline | −0.0006 |

---

## 💡 Key Findings

1. **🏆 Best Overall:** `All-features + CatBoost` ได้ **Test AUC = 0.7989** ซึ่งดีที่สุดในทุก experiment

2. **📈 Champion/Setup features ช่วยได้จริง:** การเพิ่ม champion composition, keystone, summoner spell และ lane features ทำให้ AUC ดีขึ้น **+0.0166** เมื่อเทียบกับ aggregate-only

3. **💰 Gold difference คือ feature ที่สำคัญที่สุด:** `Diff_TotalGold` เป็น feature ที่มี importance สูงสุดในทั้ง aggregate-only และ all-features experiments

4. **📉 Aggregate-only ไม่ดีกว่า Baseline:** การ engineer difference features อย่างเดียว (ไม่เพิ่ม champion features) ไม่ได้ช่วยเพิ่ม performance อย่างมีนัยสำคัญ (Δ AUC = −0.0006)

5. **⚖️ Logistic Regression ทำได้ใกล้เคียง Best Model:** ช่องว่างระหว่าง Logistic Regression กับ CatBoost อยู่ที่เพียง **+0.0018 AUC** แสดงว่า engineered features มี linear signal ที่ดีมาก

6. **🎯 10 นาทีแรกมี predictive power สูง:** ข้อมูลช่วงต้นเกม (gold, CS, kills, objectives, damage) สามารถทำนายผลได้ถึง ~80% AUC

---

## 📂 Project Structure

```
📁 Predicting-Match-Result-LOL-DataModels/
├── 📓 01_data_merging.ipynb              # รวม raw tables → match-level dataset
├── 📓 02_EDA.ipynb                       # Exploratory Data Analysis
├── 📓 03_baseline_model_kaggle.ipynb     # Baseline — Logistic Regression
├── 📓 04_modeling_aggregate_only_kaggle.ipynb  # Aggregate-only modeling
├── 📓 05_modeling_all_features_kaggle.ipynb    # All-features modeling
├── 📓 06_result_summary.ipynb            # สรุปผลลัพธ์ข้าม experiments
├── 📄 setup_data.py                      # สคริปต์ดาวน์โหลดข้อมูลจาก Kaggle
├── 📄 setup.md                           # คู่มือการติดตั้งแบบละเอียด
├── 📄 kaggle_notebooks.md                # ลิงก์ Kaggle notebooks
├── 📄 Criteria.html                      # เกณฑ์การให้คะแนนโปรเจค
├── 📄 .gitignore
│
├── 📁 data/
│   ├── 📁 t1_raw/                        # Raw CSV tables จาก Kaggle
│   │   ├── 📁 match_details/             # MatchTbl, MatchStatsTbl, SummonerMatchTbl, TeamMatchTbl
│   │   └── 📁 metadata/                  # ChampionTbl, KeystoneTbl, SummonerSpellTbl, ...
│   └── 📁 t2_transformed/                # Merged dataset (merged_v1.csv)
│
└── 📁 outputs/
    ├── 📁 baseline/                      # ผลลัพธ์ baseline experiment
    ├── 📁 aggregate_only/                # ผลลัพธ์ aggregate-only experiment
    ├── 📁 all_features/                  # ผลลัพธ์ all-features experiment
    └── 📁 final_summary/                 # สรุปรวมทุก experiment
        ├── overall_model_summary.csv
        ├── best_model_by_feature_set.csv
        ├── all_model_comparison.csv
        ├── feature_set_improvement.csv
        ├── logistic_regression_vs_best_model.csv
        ├── feature_importance_summary.csv
        ├── numeric_conclusion.txt
        ├── feature_set_auc_comparison.png
        ├── feature_set_metric_comparison.png
        └── feature_importance_side_by_side.png
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.9+
- Kaggle account (ฟรี) — [สมัครที่นี่](https://www.kaggle.com/)

### 1. Clone Repository

```bash
git clone https://github.com/Kiatisakk/Predicting-League-of-Legends-Match-Outcomes-Using-10-Minute-Data.git
cd Predicting-League-of-Legends-Match-Outcomes-Using-10-Minute-Data
```

### 2. Install Dependencies

```bash
pip install pandas numpy scikit-learn matplotlib seaborn xgboost lightgbm catboost kaggle
```

### 3. Setup Kaggle API & Download Data

ตั้งค่า Kaggle API token แล้วรันสคริปต์ดาวน์โหลดข้อมูล:

```bash
# วาง kaggle.json ไว้ที่ ~/.kaggle/kaggle.json (Linux/macOS)
# หรือ C:\Users\<YourUsername>\.kaggle\kaggle.json (Windows)

python setup_data.py
```

> 📖 ดูคู่มือติดตั้งแบบละเอียดที่ [setup.md](setup.md)

### 4. Run Notebooks

```bash
jupyter notebook
```

เปิด notebook ตามลำดับ `01` → `02` → `03` → `04` → `05` → `06`

---

## 📓 Kaggle Notebooks

สามารถดูและรัน modeling notebooks บน Kaggle ได้โดยตรง:

| Notebook | ลิงก์ |
|---|---|
| Aggregate-Only Modeling | [🔗 เปิดบน Kaggle](https://www.kaggle.com/code/flamelyy1337/notebook7b3fd4e470) |
| All / Combined Features Modeling | [🔗 เปิดบน Kaggle](https://www.kaggle.com/code/kiatisakkk/notebooke42f10f3ea) |

---

## 🏁 Conclusion

ข้อมูลในช่วง **10 นาทีแรก** ของเกม League of Legends มี **predictive signal สูง** โดยเฉพาะ feature ที่สะท้อนความได้เปรียบของทีม เช่น gold difference, CS, kills, damage output และ objective control

การเพิ่ม **champion composition** และ **player setup features** (keystones, summoner spells, lanes) ช่วยเพิ่ม performance อย่างชัดเจน ทำให้ชุดทดลอง **All-features + CatBoost** ได้ผลลัพธ์ดีที่สุดที่ **Test AUC = 0.7989**

อย่างไรก็ตาม **Logistic Regression** ยังคงทำคะแนนได้ใกล้เคียงกับ best model มาก ซึ่งแสดงว่า engineered features ที่สร้างขึ้นมี linear relationship กับ target ที่ชัดเจน

---

<div align="center">

**Made with ❤️ for CPE232 Data Modeling Course**

</div>
