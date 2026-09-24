import duckdb
import logging

logging.basicConfig(
    level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s',
    filename='clean.log'
)
logger = logging.getLogger(__name__)


# Cleaning and transforming the data from my yellow and green trip data, will remove duplicates, remove 0-passenger trips, remove 0-mile trips, remove trips with less than 100 miles, remove trips that are greater than 1 day, and I will create a verification query per rule proving the count is now zero, printed and logged
def clean_parquet_files(con, table_name: str, pickup_time: str, dropoff_time: str):

# Removing duplicates 
    try:
        cleaned_table = f"{table_name}_cleaned"
        con.execute(f"""
        CREATE TABLE {table_name}_clean AS
        SELECT DISTINCT * FROM {table_name};
        DROP TABLE {table_name};
        ALTER TABLE {table_name}_clean RENAME TO {table_name};
    """)
        print(con.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0])

    except Exception as e:
        print(f"An error occurred with the dropped variables: {e}")
        logger.error(f"An error occurred: {e}")

# Removing 0-passenger trips from the data
    try:
        before = con.execute(f"""
            SELECT COUNT(*) FROM {table_name}
            WHERE passenger_count = 0
        """).fetchone()[0]
        print(f'Before delete: {before}')

        con.execute(f"DELETE FROM {table_name} WHERE passenger_count = 0")
        after = con.execute(f"""
            SELECT COUNT(*) FROM {table_name}
            WHERE passenger_count = 0
        """).fetchone()[0]
        print(f'After delete (verify): {after}')

    except Exception as e:
        print(f"An error occurred with the dropped 0-passenger variables: {e}")
        logger.error(f"An error occurred: {e}")

# Removing 0-mile trips from the data
    try:
        before = con.execute(f"""
            SELECT COUNT(*) FROM {table_name}
            WHERE trip_distance = 0
        """).fetchone()[0]
        print(f'Before delete: {before}')

        con.execute(f"DELETE FROM {table_name} WHERE trip_distance = 0")
        after = con.execute(f"""
            SELECT COUNT(*) FROM {table_name}
            WHERE trip_distance = 0
        """).fetchone()[0]
        print(f'After delete (verify): {after}')

    except Exception as e:
        print(f"An error occurred with the dropped 0-mile variables: {e}")
        logger.error(f"An error occurred: {e}")

# Removing trips over 100 miles from the data
    try:
        before = con.execute(f"""
            SELECT COUNT(*) FROM {table_name}
            WHERE trip_distance > 100
        """).fetchone()[0]
        print(f'Before delete: {before}')

        con.execute(f"DELETE FROM {table_name} WHERE trip_distance > 100")
        after = con.execute(f"""
            SELECT COUNT(*) FROM {table_name}
            WHERE trip_distance > 100
        """).fetchone()[0]
        print(f'After delete (verify): {after}')

    except Exception as e:
        print(f"An error occurred with the dropped of trips over 100 miles: {e}")
        logger.error(f"An error occurred: {e}")

# Removing trips over 1 day from the data
    try:
        before = con.execute(f"""
            SELECT COUNT(*) FROM {table_name}
            WHERE date_diff('second', {pickup_time}, {dropoff_time}) > 86400
        """).fetchone()[0]
        print(f'Before delete: {before}')

        con.execute(f"DELETE FROM {table_name} WHERE date_diff('second', {pickup_time}, {dropoff_time}) > 86400")
        after = con.execute(f"""
            SELECT COUNT(*) FROM {table_name}
            WHERE date_diff('second', {pickup_time}, {dropoff_time}) > 86400
        """).fetchone()[0]
        print(f'After delete (verify): {after}')

    except Exception as e:
        print(f"An error occurred with the dropped variables of trips over 1 day: {e}")
        logger.error(f"An error occurred: {e}")


# This is the function that will assign names to the general labels used in the clean_parquet_files function, this is more effecient as seen in class!
def name_table_files():
    try:
        with duckdb.connect('emissions.duckdb', read_only=False) as con:
            logger.info("Connected to emissions.duckdb for cleaning")
            con.execute("SET memory_limit = '1GB';")
            con.execute("SET threads = 2;")
            con.execute("SET preserve_insertion_order = false;")

            clean_parquet_files(
                con=con,
                table_name='yellow_trips',
                pickup_time='tpep_pickup_datetime',
                dropoff_time='tpep_dropoff_datetime'
            )
        
        
            clean_parquet_files(
                con=con,
                table_name='green_trips',
                pickup_time='lpep_pickup_datetime',
                dropoff_time='lpep_dropoff_datetime'
            )

    except Exception as e:
        print(f"An error occurred with the general variables: {e}")
        logger.error(f"An error occurred: {e}")

if __name__ == "__main__":
    name_table_files()     