# Architecture

```text
Synthetic telemetry
      |
Data quality + drift
      |
Feature engineering
      |
+-----+----------------+
|                      |
Isolation Forest     Random Forest
anomaly score       failure probability
|                      |
+----------+-----------+
           |
       RUL + Health
           |
 Maintenance priority
           |
 Dashboard + audit
```

The AI layer has no command path to PLCs, SCADA or physical equipment. It is decision support only.
