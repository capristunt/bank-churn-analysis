# Bank churn analysis

A retrospective study of bank customer retention, with four analytical notebooks and one consolidated publication notebook. The report distinguishes observed associations, predictive performance and hypothetical retention economics.

## Read the report

- [Consolidated notebook](notebooks/bank-churn-summary.ipynb)
- [Downloadable, self-contained HTML report](reports/html/bank-churn.html)

Download the HTML file and open it in a browser to view the complete report offline. Its figures are embedded and no external scripts are required.

## Main findings

The sigmoid-calibrated random forest, selected on validation data, achieves test ROC-AUC **0.857**, average precision **0.685** and Brier score **0.105**. At a 20% contact quota, it targets **248 of 407 departure labels** in the 2,000-customer holdout: **62% precision**, **60.9% recall**, and **3.05 lift**. The frozen business rule targets 169 labels and the fixed random draw targets 85, with the same 400-contact capacity.

These are retrospective targeting results, not customers successfully retained. Under an illustrative 20% retention effect, US\$500 preserved margin and US\$10 per contact, the predictive strategy produces US\$20,800 of **simulated** net gain. With no retention effect, it loses US\$4,000. No campaign effectiveness or actual ROI has been measured. All scenario and pilot-planning amounts are US dollars (USD) in this edition: the numeric assumptions are unchanged, with no exchange-rate conversion. The original source-data currency remains unknown.

## Repository structure

| File or directory | Purpose |
| --- | --- |
| `notebooks/01-data-cleaning.ipynb` | Data audit, structural preparation and frozen splitting |
| `notebooks/02-data-analysis.ipynb` | Training-set distributions and segment associations |
| `notebooks/03-prediction.ipynb` | Models, validation, calibration and cached final evaluation |
| `notebooks/04-business-insights.ipynb` | Retention scenarios, interpretation and proposed pilot |
| `notebooks/bank-churn-summary.ipynb` | Single English report summarizing the four analytical stages |
| `src/` | Fresh-kernel execution, shared rendering and HTML export |
| `data/results/` | Aggregate evidence, frozen protocol and cached evaluation |
| `data/processed/contract.json` | Aggregate data contract and source fingerprints |
| `brief.md` | Original business scope and unresolved questions |
| `reports/html/bank-churn.html` | Single report exported without code |

## Reproduce the published report

Use Python **3.14.6** and the pinned dependencies:

```bash
python3.14 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python src/run_study.py summary
python src/export_html.py
```

The summary reads the committed aggregates only. It requires no customer-level file, does not retrain models and does not reevaluate the test set. It contains native Markdown for the narrative and code only for loading, checks, tables and figures. The executor starts each notebook in a separate process with a fresh IPython kernel.

## Data and full-analysis scope

The original `Churn_Modelling.csv`, prepared customer records and row-level split assignments are intentionally excluded from this public repository. Provenance and redistribution rights have not been certified, and customer identifiers and individual records must not be published. No source dataset licence is implied by this repository.

The four analytical notebooks document the existing experiment. Running them requires the original local working dataset and the original sealed workspace artifacts, including private review material. The public package supports reproducing the report from aggregate results; it does not claim to reconstruct the entire experiment from publicly distributed raw data.

Keep the original `frozen_protocol.json` and `test_evaluation.json` intact, together with the presentation-provenance record. Historical `_eur` field names are retained in those sealed numerical artifacts; the presentation record explicitly documents the later USD convention. Do not delete the test cache or weaken its checks to select new models, thresholds or targeting rules after reading test results.

## Method and limitations

The original file contains 10,000 rows and 14 columns, with unique supplied customer IDs. The split was frozen before exploration: 60% training, 20% validation and 20% test, seed 42. Learned preprocessing is fitted on training data inside pipelines. Model/calibration choices and economic assumptions precede the final holdout evaluation.

`Exited=1` is interpreted as departure/account closure using a documented match with the [Microsoft Learn example](https://learn.microsoft.com/en-us/fabric/data-science/customer-churn). This does not certify the exact file's provenance or operational definition. The label horizon, snapshot/decision dates and availability of features before departure remain unknown. Segment rates are not annual rates, associations are not causal effects, and the random split is not temporal validation.

The recommendation is a randomized pilot with a usual-service control and net contribution per assigned customer as the primary outcome, after validating chronology, eligibility, costs and margin. The report specifies the proposed intention-to-treat design and its remaining prerequisites.
