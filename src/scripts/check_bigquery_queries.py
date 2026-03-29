from src.cloud.bigquery_io import query_to_dataframe
from src.config import BQ_TABLE_FULL

TABLE = f"`{BQ_TABLE_FULL}`"


def main():
    q1 = f"SELECT COUNT(*) AS n_rows FROM {TABLE}"
    print("\nRow count")
    print(query_to_dataframe(q1))

    q2 = f"SELECT * FROM {TABLE} LIMIT 5"
    print("\nSample rows")
    print(query_to_dataframe(q2))

    q3 = f"""
    SELECT
      AVG(price) AS avg_price,
      MIN(price) AS min_price,
      MAX(price) AS max_price
    FROM {TABLE}
    """
    print("\nTarget stats")
    print(query_to_dataframe(q3))

    q4 = f"SELECT COUNT(*) AS n_price_null FROM {TABLE} WHERE price IS NULL"
    print("\nMissing price check")
    print(query_to_dataframe(q4))


if __name__ == "__main__":
    main()
