# Research Methodology

Equipment archetypes: pump, compressor, turbine, generator.

Scenarios: normal, bearing degradation, pump cavitation, compressor overheating, sensor drift.

Models:
- Isolation Forest for anomaly detection.
- Random Forest for failure-within-horizon classification.
- Transparent degradation equation for RUL.

Evaluate precision, recall, F1, ROC-AUC, false-positive/negative rate, RUL error, latency and sensitivity to data quality/drift.

Record CPU, OS, Python, package versions, random seeds, training samples and model hyperparameters. Synthetic results are not field validation.
