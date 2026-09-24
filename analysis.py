import duckdb
import logging
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    filename="analysis.log"
)
logger = logging.getLogger(__name__)

DB_PATH = "emissions.duckdb"
TABLES = {"YELLOW": "yellow_trips", "GREEN": "green_trips"}

# Dictionaries for formatting numbers into readable names
DAY_NAMES = {
    0: "Sunday", 1: "Monday", 2: "Tuesday", 3: "Wednesday",
    4: "Thursday", 5: "Friday", 6: "Saturday"
}

MONTH_NAMES = {
    1: "January", 2: "February", 3: "March", 4: "April",
    5: "May", 6: "June", 7: "July", 8: "August",
    9: "September", 10: "October", 11: "November", 12: "December"
}

def report(message):
    print(message)      
    logger.info(message) 

def largest_trip(con, label, table):
    # Dynamically select the correct timestamp column based on table
    time_col = "tpep_pickup_datetime" if "yellow" in table else "lpep_pickup_datetime"
    
    row = con.execute(f"""
        SELECT trip_co2_kgs, trip_distance, {time_col}
        FROM {table}
        ORDER BY trip_co2_kgs DESC LIMIT 1
    """).fetchone()
    report(f"[{label}] Largest single-trip CO2 of 2024: "
           f"{row[0]:.2f} kg ({row[1]:.2f} mi, picked up {row[2]})")

def heaviest_lightest(con, label, table, column, description, names=None):
    rows = con.execute(f"""
        SELECT {column}, AVG(trip_co2_kgs) AS avg_co2
        FROM {table} 
        WHERE {column} IS NOT NULL
        GROUP BY {column} 
        ORDER BY avg_co2 DESC
    """).fetchall()
    
    pretty = lambda v: names[int(v)] if (names and int(v) in names) else str(v)
    high, low = rows[0], rows[-1]
    report(f"[{label}] Most carbon-heavy {description}: "
           f"{pretty(high[0])} ({high[1]:.3f} kg avg/trip)")
    report(f"[{label}] Most carbon-light {description}: "
           f"{pretty(low[0])} ({low[1]:.3f} kg avg/trip)")

def monthly_plot(con, filename="co2_by_month_2024.png"):
    fig, ax = plt.subplots(figsize=(10, 6))
    for label, table in TABLES.items():
        rows = con.execute(f"""
            SELECT month_of_year, SUM(trip_co2_kgs) AS total_co2
            FROM {table} 
            WHERE month_of_year IS NOT NULL
            GROUP BY month_of_year 
            ORDER BY 1
        """).fetchall()
        months = [r[0] for r in rows]
        totals = [r[1] / 1000.0 for r in rows]   # kg -> tonnes
        ax.plot(months, totals, marker="o", label=f"{label} taxis")
    
    ax.set_xlabel("Month")
    ax.set_ylabel("Total CO2 (tonnes)")
    ax.set_title("Total CO2 Emissions by Month (2024)")
    ax.legend()
    fig.savefig(filename, dpi=150)
    report(f"Plot written to {filename}")

def main():
    con = duckdb.connect(DB_PATH, read_only=True)
    for label, table in TABLES.items():
        largest_trip(con, label, table)
        heaviest_lightest(con, label, table, "hour_of_day",   "hour of day")
        heaviest_lightest(con, label, table, "day_of_week",   "day of week", DAY_NAMES)
        heaviest_lightest(con, label, table, "week_of_year",  "week of year")
        heaviest_lightest(con, label, table, "month_of_year", "month of year", MONTH_NAMES)
    monthly_plot(con)
    con.close()

if __name__ == "__main__":  
    main()