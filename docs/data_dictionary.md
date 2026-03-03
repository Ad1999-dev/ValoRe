# Data Dictionary

This document describes every column in the dataset.

## Column definitions

| Column name | Type (raw) | Type (used) | Allowed values / format | Description |
|------------|------------|-------------|--------------------------|-------------|
| **id** | int64 | string (identifier) | Positive integer ID (10-digit-ish). Not guaranteed unique. | House/property sale identifier. |
| **date** | object | datetime (date) | Raw format: `YYYYMMDDT000000` (e.g., `20141013T000000`). | Sale date (time part always `000000`). |
| **price** | float64 | float (target) | 75,000 to 7,700,000 | Sale price of the house. |
| **bedrooms** | int64 | int | 0 to 33 | Number of bedrooms. |
| **bathrooms** | float64 | float | 0.0 to 8.0 (values in increments like 0.25/0.5) | Number of bathrooms (can be fractional). |
| **sqft_living** | int64 | int | 290 to 13,540 | Interior living area in square feet. |
| **sqft_lot** | int64 | int | 520 to 1,651,359 | Lot size in square feet. |
| **floors** | float64 | float (or categorical) | {1.0, 1.5, 2.0, 2.5, 3.0, 3.5} | Number of floors. |
| **waterfront** | int64 | boolean (0/1) | {0, 1} | Whether the property has a waterfront view/access. |
| **view** | int64 | ordinal int | {0, 1, 2, 3, 4} | View rating (higher means better view). |
| **condition** | int64 | ordinal int | {1, 2, 3, 4, 5} | Overall condition rating. |
| **grade** | int64 | ordinal int | {1, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13} | Overall construction/building grade. |
| **sqft_above** | int64 | int | 290 to 9,410 | Square feet of interior space above ground. |
| **sqft_basement** | int64 | int | 0 to 4,820 | Basement area in square feet. |
| **yr_built** | int64 | int | 1900 to 2015 | Year the house was built. |
| **yr_renovated** | int64 | int (with sentinel 0) | 0 or a year (1934 to 2015) | Year the house was renovated. |
| **zipcode** | int64 | category/string | 70 unique zipcodes (range 98001 to 98199) | ZIP code of the property location. |
| **lat** | float64 | float | 47.1559 to 47.7776 | Latitude coordinate. |
| **long** | float64 | float | -122.519 to -121.315 | Longitude coordinate. |
| **sqft_living15** | int64 | int | 399 to 6,210 | Living area of nearby homes (15-nearest reference). |
| **sqft_lot15** | int64 | int | 651 to 871,200 | Lot size of nearby homes (15-nearest reference). |

## Target variable
- Target column: price
- Meaning: house sale price (currency not specified in the CSV)
- Any transformation used (e.g., log): None

## Feature groups
- Numeric features: bedrooms, bathrooms, sqft_living, sqft_lot, floors, sqft_above, sqft_basement, yr_built, yr_renovated, lat, long, sqft_living15, sqft_lot15
- Categorical features: zipcode, waterfront (binary), view, condition, grade (ordinal)
- Derived features: None
-
