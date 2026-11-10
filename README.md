# Bank churn analysis

A retrospective study of bank customer retention, with four analytical notebooks and one consolidated publication notebook. The report distinguishes observed associations, predictive performance and hypothetical retention economics.

## Read the report

- [Consolidated notebook](notebooks/bank-churn-summary.ipynb) — the published report, with its narrative, tables and figures

This repository holds the notebooks and the original dataset. The exported HTML report is produced locally with the command below; it is not committed here.

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
| `data/raw/Churn_Modelling.csv` | The original source dataset, redistributed as received |
| `requirements.txt` | Pinned dependencies |

## Reproduce the published report

Use Python **3.14.6** and the pinned dependencies:

```bash
python3.14 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python src/run_study.py summary
python src/export_html.py
```

Run the four analytical notebooks first, in order, then the summary:

```bash
python src/run_study.py          # 01 -> 04, each in a fresh kernel
python src/run_study.py summary
python src/export_html.py        # writes reports/html/bank-churn.html locally
```

The summary notebook reads aggregates only: it retrains nothing and reevaluates nothing. Its narrative is in native Markdown, and its code loads, checks, tabulates and plots. The executor starts each notebook in a separate process with a fresh IPython kernel.

**One consequence of publishing without the derived artifacts.** The aggregate outputs of 02, 03 and 04 are not committed, including `frozen_protocol.json` and the `test_evaluation.json` cache. In the original workspace, that cache is what keeps the test set closed: notebook 03 reads it instead of scoring the test again, and checks that the frozen protocol is byte-identical. On a fresh clone both files are absent, so the first run of 03 **evaluates the test set itself** and writes a new cache. The protocol, the splits and the seed are unchanged, so the published figures are reproduced — but the guard that prevents a second, tuned look at the test set only becomes active from that first run onwards. Keep the regenerated files; do not delete them to try other models, thresholds or targeting rules.

## Data and full-analysis scope

`data/raw/Churn_Modelling.csv` is redistributed here exactly as received, with its 14 original columns, which include `CustomerId` and `Surname`. **Its provenance and licence are not certified.** It matches the structure of the public [Microsoft Learn example](https://learn.microsoft.com/en-us/fabric/data-science/customer-churn) dataset, but this repository implies no licence, grants no rights over the file and makes no claim about how it was collected or whether its records describe real people. Anyone reusing it should establish those rights independently.

Nothing derived from it is published: prepared customer records, row-level split assignments and every aggregate output are excluded, and the notebooks regenerate them locally. No individual record, identifier or score appears in the report, and the report publishes aggregates only.

Historical `_eur` field names are retained inside the regenerated numerical artifacts; the presentation-provenance record documents the later USD convention and the declared post hoc revisions.

## Method and limitations

The original file contains 10,000 rows and 14 columns, with unique supplied customer IDs. The split was frozen before exploration: 60% training, 20% validation and 20% test, seed 42. Learned preprocessing is fitted on training data inside pipelines. Model/calibration choices and economic assumptions precede the final holdout evaluation.

`Exited=1` is interpreted as departure/account closure using a documented match with the [Microsoft Learn example](https://learn.microsoft.com/en-us/fabric/data-science/customer-churn). This does not certify the exact file's provenance or operational definition. The label horizon, snapshot/decision dates and availability of features before departure remain unknown. Segment rates are not annual rates, associations are not causal effects, and the random split is not temporal validation.

The recommendation is a randomized pilot with a usual-service control and net contribution per assigned customer as the primary outcome, after validating chronology, eligibility, costs and margin. The report specifies the proposed intention-to-treat design and its remaining prerequisites.
