# Error Analysis: Linear vs Tree-Based

รายงานนี้สรุปผลจาก `07_error_analysis_linear_vs_treebased.ipynb` เพื่อช่วยอ่าน output ในโฟลเดอร์นี้ได้ง่ายขึ้น โดยเปรียบเทียบโมเดล 2 กลุ่ม:

- **Linear model:** `LogisticRegression`
- **Tree-based model:** `RandomForestClassifier`

เหตุผลที่ใช้ Random Forest: environment ปัจจุบันยังไม่มี `optuna`, `xgboost`, `lightgbm`, และ `catboost` จึงใช้ tree-based model จาก `sklearn` ที่รันได้ทันทีในเครื่องนี้

## Quick Summary

| Model Family | Model | Test Accuracy | Test AUC | Test F1 |
|---|---|---:|---:|---:|
| Linear | LogisticRegression | 0.7174 | 0.7971 | 0.7157 |
| Tree-based | RandomForestClassifier | 0.7005 | 0.7806 | 0.6974 |

**ข้อสรุปหลัก:** Logistic Regression ทำผลรวมดีกว่า Random Forest ในรอบนี้ เพราะ feature สำคัญของเกมช่วง 10 นาทีแรก เช่น `Diff_TotalGold`, `Diff_DmgDealt`, `Diff_MinionsKilled` มีความสัมพันธ์ค่อนข้างเป็นทิศทางตรงกับผลแพ้ชนะ ทำให้ linear model จับ signal หลักได้ดี

## Case Buckets

| Case Bucket | Count | Share | ความหมาย |
|---|---:|---:|---|
| `both_correct` | 8,699 | 63.45% | ทั้ง linear และ tree-based ทายถูก |
| `both_wrong` | 2,969 | 21.66% | ทั้งสองโมเดลทายผิด |
| `linear_correct_tree_wrong` | 1,137 | 8.29% | linear ทายถูก แต่ tree-based ทายผิด |
| `linear_wrong_tree_correct` | 905 | 6.60% | linear ทายผิด แต่ tree-based ทายถูก |

## How To Read Predictions

ในไฟล์ prediction/case CSV:

| Column | ความหมาย |
|---|---|
| `actual` | ผลจริง: `1` = Blue win, `0` = Red win |
| `linear_pred` | คำทำนายของ Logistic Regression |
| `tree_pred` | คำทำนายของ Random Forest |
| `linear_prob_blue` | ความน่าจะเป็นที่ linear คิดว่า Blue จะชนะ |
| `tree_prob_blue` | ความน่าจะเป็นที่ tree-based คิดว่า Blue จะชนะ |
| `linear_correct` | linear ทายถูกหรือไม่ |
| `tree_correct` | tree-based ทายถูกหรือไม่ |
| `case_bucket` | ประเภทของเคส เช่น `both_wrong` |
| `prob_gap_tree_minus_linear` | probability ของ tree ลบ linear; ค่าบวกแปลว่า tree เอนไปทาง Blue มากกว่า linear |
| `abs_prob_gap` | ขนาดความต่างของ probability ระหว่างสองโมเดล |

## Why Models Differ

### 1. Linear Correct, Tree Wrong

ไฟล์: `linear_correct_tree_wrong_cases.csv`

เคสกลุ่มนี้คือ linear รวม evidence หลายตัวแล้วได้ทิศทางที่ถูก แต่ Random Forest อาจให้ความสำคัญกับ split บาง feature มากเกินไปในเคสนั้น

ค่าเฉลี่ยของ bucket นี้:

- `Diff_TotalGold` ประมาณ `+90`: Blue นำ gold เล็กน้อย
- `Diff_kills` ประมาณ `+0.23`: Blue นำ kill เล็กน้อย
- `Diff_DmgDealt` ประมาณ `+35.65`: damage แทบใกล้เคียง
- `tree_prob_blue` เฉลี่ยประมาณ `0.498`: tree อยู่ใกล้ decision boundary มาก

ตีความได้ว่าเป็นเคสที่ signal ไม่แรงมาก และ tree-based model อาจแกว่งกับ threshold ของ feature บางตัว

### 2. Linear Wrong, Tree Correct

ไฟล์: `linear_wrong_tree_correct_cases.csv`

เคสกลุ่มนี้คือ tree-based ช่วยจับ pattern ที่ไม่เป็นเส้นตรงได้ดีกว่า linear เช่น หลาย signal ขัดกัน หรือมี threshold interaction ระหว่าง gold, kill, damage, objective

ค่าเฉลี่ยของ bucket นี้:

- `Diff_TotalGold` ประมาณ `+38`: Blue นำ gold เล็กน้อย
- `Diff_MinionsKilled` ประมาณ `+0.42`: CS ใกล้เคียง
- `Diff_DmgDealt` ประมาณ `+83.19`: Blue ทำ damage มากกว่าเล็กน้อย
- `linear_prob_blue` เฉลี่ยประมาณ `0.503`
- `tree_prob_blue` เฉลี่ยประมาณ `0.495`

แม้ค่าเฉลี่ยดูใกล้ 50/50 แต่รายเคสบางเกมมี signal เฉพาะที่แรงมาก เช่น kill สูงผิดปกติ, tower/objective swing, หรือ damage ต่างมาก ทำให้ tree-based แยก decision ได้ถูกในบางกรณี

### 3. Both Wrong

ไฟล์: `both_wrong_cases.csv`

เคสนี้สำคัญที่สุดสำหรับ error analysis เพราะเป็นจุดที่ข้อมูล 10 นาทีแรกไม่พอ หรือ early-game signal หลอกทั้งสองโมเดล

ค่าเฉลี่ยของ bucket นี้:

- `Diff_TotalGold` ประมาณ `-20.95`: gold ใกล้เคียงมาก
- `Diff_MinionsKilled` ประมาณ `-1.72`: CS ใกล้เคียง
- `Diff_kills` ประมาณ `+0.08`: kill ใกล้เคียง
- `Diff_DmgDealt` ประมาณ `-42.53`: damage ใกล้เคียง
- `linear_prob_blue` เฉลี่ยประมาณ `0.488`
- `tree_prob_blue` เฉลี่ยประมาณ `0.490`

ตีความได้ว่าโมเดลมักพลาดในเกมที่สถานะนาทีที่ 10 ยังไม่ชัด หรือมีเหตุการณ์หลังนาทีที่ 10 เช่น comeback, throw, scaling composition, objective fight, หรือ teamfight execution ที่ dataset ช่วง 10 นาทีแรกยังไม่เห็น

## Global Feature Signals

### Top Linear Coefficients

ไฟล์: `linear_coefficients.csv`

| Rank | Feature | Direction | Importance |
|---:|---|---|---:|
| 1 | `Diff_TotalGold` | Blue-favored | 0.3723 |
| 2 | `Diff_DmgDealt` | Blue-favored | 0.2171 |
| 3 | `Diff_MinionsKilled` | Blue-favored | 0.1998 |
| 4 | `TotalGold_P1` | Blue-favored | 0.1896 |
| 5 | `TotalGold_P8` | Red-favored | 0.1589 |

Linear model อ่านง่ายเพราะ coefficient มีทิศทาง:

- coefficient บวก = ดัน prediction ไปทาง Blue win
- coefficient ลบ = ดัน prediction ไปทาง Red win

### Top Tree-Based Importance

ไฟล์: `tree_feature_importance.csv`

| Rank | Feature | Feature Group | Importance |
|---:|---|---|---:|
| 1 | `Diff_TotalGold` | aggregate_difference | 0.0659 |
| 2 | `Diff_kills` | aggregate_difference | 0.0318 |
| 3 | `Diff_KDA` | aggregate_difference | 0.0306 |
| 4 | `Blue_KDA` | team_aggregate | 0.0290 |
| 5 | `Diff_deaths` | aggregate_difference | 0.0270 |

Tree importance บอกว่า feature ไหนช่วย split ได้มาก แต่ไม่ได้บอกทิศทางตรง ๆ ว่าเข้าข้าง Blue หรือ Red

## LoL Interpretation: Why The Model Can Be Wrong

มุมมองนี้แปลผลจากตัวเลขให้เป็นเหตุผลในเกม League of Legends โดยเฉพาะ เพราะข้อมูลที่ใช้มีแค่สถานะช่วง **10 นาทีแรก** ดังนั้นโมเดลเห็น early game แต่ยังไม่เห็น mid/late game decision เช่น dragon stacking ต่อจากนั้น, Herald usage, Baron fight, shutdown, split push, scaling, teamfight execution และการ throw/comeback

### When Only One Model Is Wrong

| Case | Model ที่ถูก | มุมมองเชิงโมเดล | มุมมองใน LoL |
|---|---|---|---|
| `linear_correct_tree_wrong` | Logistic Regression | linear รวม signal หลักแบบ smooth แล้วถูก แต่ tree อาจแกว่งกับ split/threshold บางจุด | เกมมักมีพื้นฐานโดยรวมไปทางทีมที่ชนะ เช่น gold/CS/damage/objective พอเอนไปด้านเดียวกัน แม้บาง feature จะ noisy; linear เลยอ่านภาพรวม early advantage ได้ดีกว่า |
| `linear_wrong_tree_correct` | Random Forest | tree จับ interaction หรือ threshold ที่ linear มองเป็นเส้นตรงไม่ได้ | เกมอาจมี signal ปนกัน เช่น gold นำแต่ objective เสีย, kill เยอะแต่ tower/dragon ตาม, หรือบาง lane snowball หนัก; tree มีโอกาสจับ pattern เฉพาะแบบ "ถ้า A และ B เกิดพร้อมกัน" ได้ดีกว่า |

### Linear Correct, Tree Wrong

Bucket นี้มี `1,137` เกม หรือ `8.29%` ของ test set

ค่าเฉลี่ยสำคัญ:

- `Diff_TotalGold` ประมาณ `+90`
- `Diff_kills` ประมาณ `+0.23`
- `Diff_DmgDealt` ประมาณ `+35.65`
- `tree_prob_blue` เฉลี่ยประมาณ `0.498`

**ตีความแบบ LoL:** เกมกลุ่มนี้ไม่ได้เป็น stomp ชัด ๆ แต่ signal หลักค่อนข้างอ่อนและใกล้ 50/50 มาก การที่ linear ถูกแปลว่า evidence รวม เช่น gold, CS, damage, kill และ objective อาจเอนไปในทิศทางเดียวกับผลจริงแบบบาง ๆ ขณะที่ tree-based model อาจโดน feature เฉพาะบางตัวหลอก เช่น lane dummy, rune/spell setup, หรือ split ของ objective count ที่ทำให้ผลทายพลิก

ตัวอย่างเหตุผลที่พบได้ในเกมจริง:

- early gold lead เล็ก ๆ กระจายหลาย lane ดีกว่า kill lead ที่กองอยู่คนเดียว
- team ที่ดูเสีย objective บางอย่างอาจยังมี lane economy ดีกว่า
- kill score ใกล้กันมาก ทำให้ tree split บางจุดตัดสินผิดง่าย
- feature บางตัวมีค่า rare เช่น lane/keystone/spell combination ทำให้ tree overreact

### Linear Wrong, Tree Correct

Bucket นี้มี `905` เกม หรือ `6.60%` ของ test set

ค่าเฉลี่ยสำคัญ:

- `Diff_TotalGold` ประมาณ `+38`
- `Diff_MinionsKilled` ประมาณ `+0.42`
- `Diff_DmgDealt` ประมาณ `+83.19`
- `linear_prob_blue` เฉลี่ยประมาณ `0.503`
- `tree_prob_blue` เฉลี่ยประมาณ `0.495`

**ตีความแบบ LoL:** ค่าเฉลี่ยทั้ง bucket ใกล้ 50/50 มาก แปลว่าโดยรวมเป็นเกมที่ early signal ไม่ชัด แต่รายเกมบางเคสมี pattern เฉพาะ เช่น objective swing, tower lead, kill distribution หรือ damage gap ที่ไม่สามารถอธิบายด้วยเส้นตรงง่าย ๆ ได้ Tree-based model จึงอาจอ่าน "เงื่อนไขผสม" ได้ถูกกว่า

ตัวอย่างเหตุผลที่พบได้ในเกมจริง:

- ทีมหนึ่งนำ kill แต่เสีย tower/dragon ทำให้ gold lead ไม่ได้แปลว่า map control ดีกว่า
- jungler หรือ bot lane snowball หนักจน pattern ไม่เหมือนค่าเฉลี่ยทั่วไป
- damage สูงมากแต่ไม่ convert เป็น objective อาจหลอก linear
- kill/death/KDA interaction มี threshold เช่น kill lead มากพอจึงเริ่มมีผลจริง ไม่ใช่เพิ่มทีละนิดแบบ linear
- champion/setup feature อาจสะท้อน composition ที่เล่นต่อจาก early state ได้ต่างกัน

### Both Wrong

Bucket นี้มี `2,969` เกม หรือ `21.66%` ของ test set

ค่าเฉลี่ยสำคัญ:

- `Diff_TotalGold` ประมาณ `-20.95`
- `Diff_MinionsKilled` ประมาณ `-1.72`
- `Diff_kills` ประมาณ `+0.08`
- `Diff_DmgDealt` ประมาณ `-42.53`
- `linear_prob_blue` เฉลี่ยประมาณ `0.488`
- `tree_prob_blue` เฉลี่ยประมาณ `0.490`

**ตีความแบบ LoL:** นี่คือกลุ่มที่น่าสนใจที่สุด เพราะทั้งสองโมเดลผิดพร้อมกัน และค่าเฉลี่ย signal หลักแทบเสมอกันหมด เกมพวกนี้มีโอกาสสูงว่า **ข้อมูลนาทีที่ 10 ยังไม่พอ** หรือ early state ชี้ผิดทางเมื่อเทียบกับผลสุดท้าย

เหตุผลใน LoL ที่น่าจะทำให้ผิดทั้งคู่:

- **Comeback หลัง 10 นาที:** ทีมที่ตามเล็กน้อยกลับมาจาก shutdown, teamfight หรือ objective fight
- **Throw:** ทีมที่นำ early game พลาดไฟต์ใหญ่หรือพลาด objective สำคัญหลังจากนั้น
- **Scaling composition:** ทีมที่แพ้ early แต่ champion scale ดีกว่าใน mid/late game
- **Objective conversion ไม่เท่ากัน:** early kill/gold lead ไม่ได้กลายเป็น dragon, tower, Herald หรือ Baron control
- **Gold distribution:** gold lead อาจกองที่ role ที่ carry เกมต่อไม่ได้ หรือกระจายไม่ดี
- **Map state ที่ไม่มีใน feature:** vision, wave state, tempo, summoner spell cooldown, jungle path, item timing หลังนาที 10
- **Queue/game mode noise:** บาง queue อาจมีพฤติกรรมการเล่นไม่เหมือน Classic Summoner's Rift ranked-style game

### What To Inspect In Real Match Review

ถ้าจะหยิบเคสจาก CSV ไปอธิบายเป็นรายเกม แนะนำดูตามลำดับนี้:

1. `Diff_TotalGold`: ทีมไหนนำ gold ตอน 10 นาที
2. `Diff_MinionsKilled`: gold lead มาจาก farming หรือ kill
3. `Diff_kills` และ `Diff_KDA`: fight lead ชัดแค่ไหน
4. `Diff_DmgDealt`: teamfight/trading pressure เอนไปทางไหน
5. `Diff_DragonKills` และ `Diff_TowerKills`: early lead convert เป็น objective หรือไม่
6. champion/setup/lane features: มี composition หรือ role pattern ที่อาจทำให้เกมพลิกหลัง 10 นาทีไหม

สรุปแบบสั้น: ถ้าโมเดลผิดตัวเดียว ให้มองว่า model family หนึ่งอ่าน pattern บางแบบได้ดีกว่าอีกตัว แต่ถ้าผิดทั้งคู่ ให้มองว่าเกมนั้นอาจถูกตัดสินโดยสิ่งที่ไม่ได้อยู่ในข้อมูล 10 นาทีแรก

## File Guide

### Summary Files

| File | ใช้ทำอะไร |
|---|---|
| `model_metrics.csv` | ดูคะแนนรวมของ linear และ tree-based |
| `case_bucket_counts.csv` | ดูจำนวนเคสแต่ละประเภท |
| `bucket_signal_summary.csv` | ดูค่าเฉลี่ย signal สำคัญแยกตาม bucket |
| `lol_interpretation_by_bucket.csv` | อ่านคำอธิบายเชิง LoL ของแต่ละ error bucket แบบตารางสั้น |

### Prediction Case Files

| File | ใช้ทำอะไร |
|---|---|
| `prediction_disagreement_cases.csv` | master table ของ test cases ทั้งหมด |
| `both_wrong_cases.csv` | เคสที่ทั้งสองโมเดลผิด |
| `linear_wrong_tree_correct_cases.csv` | เคสที่ tree ถูก แต่ linear ผิด |
| `linear_correct_tree_wrong_cases.csv` | เคสที่ linear ถูก แต่ tree ผิด |

### Example And Explanation Files

| File | ใช้ทำอะไร |
|---|---|
| `example_cases_summary.csv` | ตัวอย่างเคสสำคัญพร้อมเหตุผลภาษาไทย อ่านง่ายที่สุด |
| `example_both_wrong.csv` | ตัวอย่างเฉพาะเคสผิดทั้งคู่ |
| `example_linear_wrong_tree_correct.csv` | ตัวอย่างเฉพาะเคส tree ถูก linear ผิด |
| `example_linear_correct_tree_wrong.csv` | ตัวอย่างเฉพาะเคส linear ถูก tree ผิด |
| `detailed_case_explanations.csv` | feature-level explanation ของตัวอย่างเคส |

### Feature Importance Files

| File | ใช้ทำอะไร |
|---|---|
| `linear_coefficients.csv` | coefficient ของ Logistic Regression พร้อมทิศทาง Blue/Red |
| `tree_feature_importance.csv` | feature importance ของ Random Forest |

### Visual Files

| File | ใช้ทำอะไร |
|---|---|
| `confusion_matrices.png` | ดู confusion matrix ของทั้งสองโมเดล |
| `probability_disagreement_scatter.png` | ดูว่า probability ของสองโมเดลต่างกันตรงไหน |
| `bucket_signal_summary.png` | ดู signal เฉลี่ยแยกตาม bucket |
| `global_model_signals.png` | ดู top global features ของ linear และ tree-based |

## Recommended Reading Order

1. เปิด `model_metrics.csv` เพื่อดูว่าโมเดลไหนดีกว่าโดยรวม
2. เปิด `case_bucket_counts.csv` เพื่อดู error distribution
3. เปิด `example_cases_summary.csv` เพื่ออ่านตัวอย่างเคสพร้อมเหตุผล
4. เปิด `both_wrong_cases.csv` เพื่อวิเคราะห์จุดที่ข้อมูล 10 นาทีแรกยังไม่พอ
5. เปิด `linear_coefficients.csv` และ `tree_feature_importance.csv` เพื่ออธิบายว่าโมเดลใช้ feature อะไร
6. ดูรูป `probability_disagreement_scatter.png` และ `global_model_signals.png` ถ้าต้องการภาพประกอบในรายงาน

## Report-Ready Takeaway

เมื่อเทียบ linear model กับ tree-based model บน all-features setup พบว่า Logistic Regression ทำผลรวมดีกว่า Random Forest ทั้ง AUC, Accuracy และ F1 แสดงว่า signal หลักจากข้อมูล 10 นาทีแรกมีลักษณะค่อนข้างเป็นทิศทางตรง เช่น Blue นำ gold, damage, CS หรือ objective แล้วมีโอกาสชนะสูงขึ้น อย่างไรก็ตาม Random Forest ยังทายถูกในบางเคสที่ linear พลาด โดยเฉพาะเคสที่ signal หลายตัวขัดกันหรือมี interaction ที่ไม่เป็นเส้นตรง ส่วนเคสที่ผิดทั้งสองโมเดลมักเป็นเกมที่สถานะนาทีที่ 10 ยังไม่ชัด หรือผลลัพธ์สุดท้ายได้รับอิทธิพลจากเหตุการณ์หลังนาทีที่ 10 ซึ่งไม่อยู่ใน feature set นี้
