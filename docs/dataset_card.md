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

## Data description
- Data type: tabular / structured
- Row count: 21,614
- Number of features: 21

| Variable | Type | Description |
| :--- | :--- | :--- |
| **id** | Discrete | Unique identifier for each property. |
| **date** | Datetime | Date of property listing (useful for seasonality analysis). |
| **price** | **Target** | Property price in currency (Continuous). |
| **bedrooms** | Integer | Number of bedrooms. |
| **bathrooms** | Continuous | Number of bathrooms (includes half-baths, e.g., 2.25). |
| **sqft_living** | Continuous | Total squared foot of the interior living space. |
| **sqft_lot** | Continuous | Total squared foot of the land lot. |
| **floors** | Continuous | Number of floors in the house. |
| **waterfront** | Binary | 1 if property has a waterfront view. |
| **view** | Ordinal | Quality rating of the property view (0 to 4). |
| **condition** | Ordinal | Overall condition rating of the house (1 to 5). |
| **grade** | Ordinal | Construction quality/design grade (1 to 13). |
| **sqft_above** | Continuous | Square foot of the house apart from the basement. |
| **sqft_basement**| Continuous | Square foot of the basement. |
| **yr_built** | Integer | The year the property was originally built. |
| **yr_renovated** | Integer | Year of last renovation (0 if never renovated). |
| **zipcode** | Categorical | 5-digit zip code area. |
| **lat** | Continuous | Latitude coordinate of the property. |
| **long** | Continuous | Longitude coordinate of the property. |
| **sqft_living15**| Continuous | Average living area of the 15 closest neighbors. |
| **sqft_lot15** | Continuous | Average lot size of the 15 closest neighbors. |

## Limitations
- **Region:** Limited to King County, Washington State.
- **Time:** Data represents a snapshot of the 2014-2015 market.
- **Provenance:** Random real estate website data mixed.

## License and usage constraints
- Kaggle license / terms: CC0: Public Domain
<<<<<<< HEAD
=======

## Data description (high level)
- Data type: tabular / structured
- Row count: 21,613
- Number of features: 21
- Target variable: `price`
>>>>>>> develop
