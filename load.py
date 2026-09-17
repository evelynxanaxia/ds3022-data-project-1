import duckdb
import os
import logging

logging.basicConfig(
    level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s',
    filename='load.log'
)
logger = logging.getLogger(__name__)

def load_parquet_files():

    con = None

    try:
        # Connect to local DuckDB instance
        con = duckdb.connect(database='emissions.duckdb', read_only=False)
        logger.info("Connected to DuckDB instance")

        con.execute(f"""
            DROP TABLE IF EXISTS vehicle_emissions;
            CREATE TABLE vehicle_emissions AS
            SELECT * FROM read_csv_auto(
            'data/vehicle_emissions.csv');
        """)
        logger.info("Dropped table if exists")

        n = con.execute(
            "SELECT COUNT(*) FROM vehicle_emissions"
        ).fetchone()[0]
        logger.info(f"vehicle_emissions: {n} rows loaded")

        og_url = 'https://d37ci6vzurychx.cloudfront.net/trip-data/'

        for month in range(1, 13):
            url = f'{og_url}yellow_tripdata_2024-{month:02d}.parquet'
            if month == 1:
                con.execute(f"""
                DROP TABLE IF EXISTS yellow_trips;
                CREATE TABLE yellow_trips AS
                SELECT * FROM read_parquet(
                '{og_url}yellow_tripdata_2024-{month:02d}.parquet');
                """)
#  for month in range(1, 13):
#         url = (f'{og_url}yellow_tripdata_2024-{month:02d}.parquet')

                con.execute(
                    f"INSERT INTO yellow_trips "
                    f"SELECT * FROM read_parquet('{url}')"
                    )
                con.execute("""
                "SELECT 
                VendorID,
                tpep_picup_datetime AS pickup_time, -- lpep_pickup_datetime on GREEN
                tpep_dropoff_datetime AS dropoff_time, --lpep_dropoff_datetime on GREEN
                passenger_count,
                trip_distance
                FROM read_parquet(url)
                """)

    except Exception as e:
        print(f"An error occurred: {e}")
        logger.error(f"An error occurred: {e}")

if __name__ == "__main__":
    load_parquet_files()