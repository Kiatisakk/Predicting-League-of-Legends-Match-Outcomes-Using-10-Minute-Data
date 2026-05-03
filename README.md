# Predicting League of Legends Match Outcomes Using 10-Minute Data

โปรเจคนี้สร้างโมเดล Machine Learning สำหรับทำนายผลแพ้ชนะของเกม League of Legends จากข้อมูลสถานะเกมช่วง 10 นาทีแรก โดยใช้ข้อมูลด้าน economy, combat, objective, champion composition และ setup ของผู้เล่น เพื่อเปรียบเทียบว่า feature แต่ละกลุ่มช่วยเพิ่มประสิทธิภาพของโมเดลมากน้อยแค่ไหน

## Project Objective

เป้าหมายหลักของโปรเจคคือทำนายว่า Blue Team จะชนะหรือไม่จากข้อมูลในช่วงต้นเกม โดยใช้ `AUC-ROC` เป็น metric หลัก และใช้ `Accuracy` กับ `F1` เป็น metric สนับสนุน

แนวคิดสำคัญของโปรเจคคือข้อมูล 10 นาทีแรกสะท้อนสถานะสำคัญของเกม เช่น gold lead, CS lead, kill lead, objective control และ damage output ซึ่งสามารถใช้ประเมินความได้เปรียบของแต่ละทีมได้

## Notebook Structure

ให้รัน notebook ตามลำดับนี้

| Notebook | Purpose |
|---|---|
| `01_data_merging.ipynb` | รวม raw tables หลายไฟล์ให้เป็น match-level dataset หนึ่งแถวต่อหนึ่งเกม |
| `02_EDA.ipynb` | สำรวจความสัมพันธ์ของ gold, CS, kills, KDA, objectives, damage และ lane matchup กับผลแพ้ชนะ |
| `03_baseline_model_kaggle.ipynb` | สร้าง baseline ด้วย Logistic Regression จาก raw encoded features โดยยังไม่ทำ feature engineering หลัก |
| `04_modeling_aggregate_only_kaggle.ipynb` | เทรนและ tune โมเดลด้วย aggregate/team-level และ difference features |
| `05_modeling_all_features_kaggle.ipynb` | เทรนและ tune โมเดลด้วย aggregate features รวมกับ champion/setup features |
| `06_result_summary.ipynb` | รวมผลลัพธ์จาก 03/04/05 เพื่อสรุป model comparison, improvement และ feature importance |

## Data Flow

1. โหลด raw match/player/team metadata จาก `data/t1_raw/`
2. รวมข้อมูลผู้เล่นและทีมให้อยู่ในระดับ match
3. สร้าง target ว่า Blue Team ชนะหรือไม่
4. ทำ EDA เพื่อดู signal สำคัญในช่วง 10 นาที
5. สร้าง feature set หลายแบบเพื่อเปรียบเทียบ
6. เทรนโมเดลหลายตัวและ tune hyperparameters
7. สรุปผลลัพธ์ข้าม notebook ใน `06_result_summary.ipynb`

## Feature Sets

โปรเจคนี้แบ่งการทดลอง modeling เป็น 3 ระดับหลัก

| Experiment | Feature Set | Description |
|---|---|---|
| Baseline | Raw encoded features | ใช้ข้อมูลที่ encode แล้วแบบพื้นฐาน ยังไม่เน้น feature engineering |
| Aggregate-only | Team-level + difference features | ใช้ feature เช่น gold diff, CS diff, kill diff, KDA diff, objective diff |
| All-features | Aggregate + champion/setup | เพิ่ม champion multi-hot, summoner spell, keystone และ lane/setup features |

## Models

โมเดลที่ใช้ในส่วน modeling ได้แก่

- Logistic Regression
- Decision Tree
- Random Forest
- XGBoost
- LightGBM
- CatBoost

`Logistic Regression` ถูกใช้เป็น baseline สำคัญ เพราะตีความ coefficient ได้ง่าย และเหมาะกับ engineered difference features ที่มีความสัมพันธ์ค่อนข้างตรงกับผลแพ้ชนะ

## Current Result Summary

ผลลัพธ์สรุปล่าสุดจาก `outputs/final_summary/overall_model_summary.csv`

| Experiment | Selected Model | Test AUC | Test Accuracy | Test F1 |
|---|---|---:|---:|---:|
| Baseline raw encoded features | Logistic Regression | 0.7828 | 0.7053 | 0.7028 |
| Aggregate-only engineered features | CatBoost | 0.7824 | 0.7035 | 0.7002 |
| Aggregate-only Logistic Regression | Logistic Regression | 0.7812 | 0.7036 | 0.7012 |
| All-features best model | CatBoost | 0.8001 | 0.7187 | 0.7160 |
| All-features Logistic Regression | Logistic Regression | 0.7971 | 0.7174 | 0.7157 |

สรุปจากผลล่าสุด:

- Best overall experiment คือ `05 All features` โดยใช้ `CatBoost`
- Best Test AUC = `0.8001`
- All-features ดีขึ้นจาก aggregate-only best model ประมาณ `+0.0177` AUC
- All-features ดีขึ้นจาก baseline ประมาณ `+0.0173` AUC
- Logistic Regression ยังทำคะแนนใกล้ best model มาก โดยเฉพาะเมื่อใช้ feature ที่มี signal ชัดเจน

## Output Files

ผลลัพธ์ถูกแยกตาม experiment

```text
outputs/
  baseline/
  aggregate_only/
  all_features/
  final_summary/
```

ไฟล์สำคัญใน `outputs/final_summary/`

| File | Description |
|---|---|
| `overall_model_summary.csv` | ตารางรวมผล baseline, aggregate-only และ all-features |
| `best_model_by_feature_set.csv` | best model ของแต่ละ feature set |
| `all_model_comparison.csv` | ตารางเปรียบเทียบทุกโมเดลจาก 04 และ 05 |
| `feature_set_improvement.csv` | ความต่างของ metric ระหว่าง feature set |
| `logistic_regression_vs_best_model.csv` | เปรียบเทียบ Logistic Regression กับ best model |
| `feature_importance_summary.csv` | รวม top feature importance จาก experiment หลัก |
| `numeric_conclusion.txt` | conclusion ที่สร้างจากตัวเลขจริง |
| `feature_set_auc_comparison.svg` | กราฟเปรียบเทียบ AUC ข้าม feature set |
| `feature_set_auc_improvement.svg` | กราฟ improvement ของ AUC |

## Kaggle Notebooks

สามารถดูและรัน modeling notebooks บน Kaggle ได้จากลิงก์นี้

- [Aggregate-Only Modeling Notebook](https://www.kaggle.com/code/flamelyy1337/notebook7b3fd4e470)
- [All / Combined Features Modeling Notebook](https://www.kaggle.com/code/kiatisakkk/notebooke42f10f3ea)

## Main Takeaway

ข้อมูลในช่วง 10 นาทีแรกมี predictive signal สูง โดยเฉพาะ feature ที่สะท้อนความได้เปรียบของทีม เช่น gold, CS, kills, damage และ objective control ส่วน champion/setup features ช่วยเพิ่ม performance เมื่อรวมกับ aggregate features ทำให้ all-features + CatBoost เป็นผลลัพธ์ที่ดีที่สุดในชุดทดลองปัจจุบัน
