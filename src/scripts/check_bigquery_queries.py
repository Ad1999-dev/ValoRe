from src.cloud.bigquery_io import query_to_dataframe

PROJECT_ID = "valore-mlsd-project"
DATASET_ID = "valore"
TABLE_NAME = "housing_raw"

TABLE = f"`{PROJECT_ID}.{DATASET_ID}.{TABLE_NAME}`"


def main():
    # 1) Row count
    q1 = f"SELECT COUNT(*) AS n_rows FROM {TABLE}"
    print("\n--- Row count ---")
    print(query_to_dataframe(q1))

    # 2) Column sample
    q2 = f"SELECT * FROM {TABLE} LIMIT 5"
    print("\n--- Sample rows ---")
    print(query_to_dataframe(q2))

    # 3) Basic target stats (replace 'price' if needed)
    q3 = f"""
    SELECT
      AVG(price) AS avg_price,
      MIN(price) AS min_price,
      MAX(price) AS max_price
    FROM {TABLE}
    """
    print("\n--- Target stats ---")
    print(query_to_dataframe(q3))

    # 4) Missing check example (replace columns if needed)
    # Example: count rows where price is NULL
    q4 = f"SELECT COUNT(*) AS n_price_null FROM {TABLE} WHERE price IS NULL"
    print("\n--- Missing price ---")
    print(query_to_dataframe(q4))


if __name__ == "__main__":
    main()