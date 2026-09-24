import duckdb
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("transform.log"),
        logging.StreamHandler()],
        )
logger = logging.getLogger(__name__)

DB_PATH = "emissions.duckdb"
TABLES = ("yellow_trips", "green_trips")

NEW_COLUMNS = {
    "trip_co2_kgs": "DOUBLE",
    "avg_mph": "DOUBLE",
    "hour_of_day": "INTEGER",
    "day_of_week": "INTEGER",
    "week_of_year": "INTEGER",
    "month_of_year": "INTEGER",
}

# Adding the correct number values from miles -> kg 
def add_columns(con, table: str):
    try:
        for column, dtype in NEW_COLUMNS.items():
            con.execute(f"ALTER TABLE {table} ADD COLUMN IF NOT EXISTS {column} {dtype};")
        logger.info(f"{table}: ensured columns {list(NEW_COLUMNS)} exist")
    except Exception as e:
            print(f"An error occurred during the creation of the 6 new columns: {e}")
            logger.error(f"An error occurred during transformation: {e}")

# Adding the information to the columns we just created above
def populate_columns(con, table: str, vehicle_type: str, pickup_col: str, dropoff_col: str):
    try: 
        con.execute(f"""
            UPDATE {table}
            SET trip_co2_kgs = (
                SELECT ({table}.trip_distance * ve.co2_grams_per_mile) / 1000.0
                FROM vehicle_emissions ve
                WHERE ve.vehicle_type = '{vehicle_type}'
            );
        """)
        logger.info(f"{table}: calculated trip_co2_kgs")

        con.execute(f"""
            UPDATE {table}
            SET avg_mph = trip_distance / (date_diff('second', {pickup_col}, {dropoff_col}) / 3600.0);
        """)
        logger.info(f"{table}: calculated avg_mph")

        con.execute(f"""
            UPDATE {table}
            SET hour_of_day = date_part('hour', {pickup_col}),
                day_of_week = date_part('dow', {pickup_col}),
                week_of_year = date_part('week', {pickup_col}),
                month_of_year = date_part('month', {pickup_col});
        """)
        logger.info(f"{table}: calculated temporal date_part columns")

    except Exception as e:
        print(f"An error occurred during the addition of information to the 6 new columns: {e}")
        logger.error(f"An error occurred during transformation: {e}")

# Allows us to activate the functions we created with their generic names as they haev their label here
def transform_func():
    try:
        with duckdb.connect(DB_PATH, read_only=False) as con:
            logger.info("Connected to emissions.duckdb for transformation")

# Memory safeguards for Codespaces, if this is not included the code says "terminated" because it runs out of ram
            con.execute("SET memory_limit = '1GB';")
            con.execute("SET threads = 2;")

# Transforms the yellow_trips maps to 'yellow_taxi' in vehicle_emissions
            add_columns(con, "yellow_trips")
            populate_columns(
                con, 
                table="yellow_trips", 
                vehicle_type="yellow_taxi", 
                pickup_col="tpep_pickup_datetime", 
                dropoff_col="tpep_dropoff_datetime"
            )

# Transforms the green_trips maps to 'green_taxi' in vehicle_emissions
            add_columns(con, "green_trips")
            populate_columns(
                con, 
                table="green_trips", 
                vehicle_type="green_taxi", 
                pickup_col="lpep_pickup_datetime", 
                dropoff_col="lpep_dropoff_datetime"
            )

    except Exception as e:
        print(f"An error occurred during transformation: {e}")
        logger.error(f"An error occurred during transformation: {e}")

if __name__ == "__main__":
    transform_func()