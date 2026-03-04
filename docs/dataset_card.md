# Dataset Card
The dataset represents house/property sales in King County, USA (area around Seattle) between May 2014 and May 2015.

## Source
- Dataset Name: Housing Price Dataset
- Platform: Kaggle
- Dataset page: https://www.kaggle.com/datasets/sukhmandeepsinghbrar/housing-price-dataset/data
- File used: `Housing.csv`
- Collected / published by: Sukhmandeep Singh Brar
- Date accessed: 2026-02-15

## Context and intended use
This dataset contains structured housing-related features intended for predicting house prices.
In ValoRe, we use it to build an end-to-end ML system that demonstrates MLOps practices
(online data access, reproducible experiments, CI/CD), rather than optimizing model complexity.

## Limitations
- **Region:** Limited to King County, Washington State.
- **Time:** Data represents a snapshot of the 2014-2015 market.
- **Provenance:** Random real estate website data mixed.

## License and usage constraints
- Kaggle license / terms: CC0: Public Domain

## Data description (high level)
- Data type: tabular / structured
- Row count: 21,613
- Number of features: 21
- Target variable: `price`
