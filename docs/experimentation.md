# Model Experimentation

## 1. Task Definition

Regression task: Predict house prices based on structural and location-related features.

Dataset:
- 21,613 records
- 20 numerical features after preprocessing
- Target variable: `price`

The dataset is stored in Google BigQuery:
`bq://valore-mlsd-project.valore.housing_raw`

The model training pipeline reads data directly from BigQuery.

---

## 2. Data Split

| Set       | Size | Strategy |
|------------|------|----------|
| Train      | 70%  | Random split (random_state=42) |
| Validation | 10%  | Held-out validation |
| Test       | 20%  | Final evaluation set |

Hyperparameter tuning is performed using 10-fold cross-validation on the training set only.
The test set is strictly reserved for final evaluation.

---

## 3. Model Comparison (Baseline)

Three regression models were evaluated on the validation set:

- Linear Regression
- Random Forest (500 trees)
- XGBoost (500 trees, learning_rate=0.2, max_depth=6)

### Validation Results

| Model             | MAE       | RMSE        | R²     |
|------------------|------------|-------------|--------|
| XGBoost          | 64,279.80  | 119,566.27  | 0.8848 |
| Random Forest    | 70,547.48  | 135,946.08  | 0.8511 |
| Linear Regression| 125,638.94 | 188,894.14  | 0.7126 |

XGBoost achieved the best baseline performance in terms of RMSE and R².

---

## 4. Hyperparameter Tuning

XGBoost was selected for hyperparameter optimization using GridSearchCV.

Search space:

| Parameter       | Values Tested         |
|-----------------|----------------------|
| n_estimators    | [300, 500, 800]      |
| learning_rate   | [0.05, 0.1, 0.2]     |
| max_depth       | [4, 6, 8]            |

Cross-validation:
- 10-fold CV
- Scoring metric: RMSE

### Best Parameters

| Parameter        | Value |
|------------------|--------|
| n_estimators     | 800    |
| learning_rate    | 0.1    |
| max_depth        | 4      |

Best CV RMSE: 124,551.78

---

## 5. Final Model Performance (Test Set)

After retraining the model on train + validation data:

| Metric | Value |
|--------|--------|
| MAE    | 62,549.77 |
| RMSE   | 107,557.43 |
| R²     | 0.9063 |

The test performance indicates strong generalization capability.


---

## 6. Reproducibility

The experiment can be reproduced using:

```bash
python -m src.model --data bq://valore-mlsd-project.valore.housing_raw

