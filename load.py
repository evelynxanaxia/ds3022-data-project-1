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
# Vehicle emissions loading data
    try:
        # Connect to local DuckDB instance
        con = duckdb.connect(database='emissions.duckdb', read_only=False)
        logger.info("Connected to DuckDB instance")

# This creates the table from the csv file
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

    except Exception as e:
        print(f"An error occurred: {e}")
        logger.error(f"An error occurred: {e}")


# Yellow trips loading data
    try:
        og_urly = 'https://d37ci6vzurychx.cloudfront.net/trip-data/'

# Creating an empty table to prevent a catalog eror, this code creates a table from the same link but instead of reading all the data it just reads the headings

        first_urly = f"{og_urly}yellow_tripdata_2024-01.parquet"
        con.execute(f"""
            DROP TABLE IF EXISTS yellow_trips;
            CREATE TABLE yellow_trips AS
            SELECT * FROM read_parquet('{first_urly}')
            LIMIT 0;
        """)
        logger.info("Initialized empty yellow_trips table")

        for month in range(1, 13):
            urly = f"{og_urly}yellow_tripdata_2024-{month:02d}.parquet"
            con.execute(
                f"INSERT INTO yellow_trips "
                f"SELECT * FROM read_parquet('{urly}')"
                )
        m = con.execute(
            "SELECT COUNT(*) FROM yellow_trips"
            ).fetchone()[0]
        logger.info(f"yellow_trips: {m} rows loaded, yellow loop working")

    except Exception as e:
        print(f"An error occurred with yellow_trips data: {e}")
        logger.error(f"An error occurred: {e}")

# Green trip loading data
    try:
            og_urlg = 'https://d37ci6vzurychx.cloudfront.net/trip-data/'
    
# Creating an empty table to prevent a catalog eror, this code creates a table from the same link but instead of reading all the data it just reads the headings
    
            first_urlg = f"{og_urlg}green_tripdata_2024-01.parquet"
            con.execute(f"""
                DROP TABLE IF EXISTS green_trips;
                CREATE TABLE green_trips AS
                SELECT * FROM read_parquet('{first_urlg}')
                LIMIT 0;
            """)
            logger.info("Initialized empty green_trips table")
    
            for month in range(1, 13):
                urlg = f"{og_urlg}green_tripdata_2024-{month:02d}.parquet"
                con.execute(
                    f"INSERT INTO green_trips "
                    f"SELECT * FROM read_parquet('{urlg}')"
                    )
            p = con.execute(
                "SELECT COUNT(*) FROM green_trips"
                ).fetchone()[0]
            logger.info(f"green_trips: {p} rows loaded, green loop working")
    
    except Exception as e:
        print(f"An error occurred with green_trips data: {e}")
        logger.error(f"An error occurred: {e}")

if __name__ == "__main__":
    load_parquet_files() 