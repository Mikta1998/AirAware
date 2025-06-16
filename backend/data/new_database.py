import psycopg2
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

class PostgresDB:
    def __init__(self):
        '''
        This function connect the database and ensures that the aqi_data table exists.
        '''
        self.conn = psycopg2.connect(
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT")
        )
        self.create_table()

    def create_table(self):
        '''
        This function initialize the aqi_data table if it does not exist.
        Columns: id, country, city=capital, lat=latitude, lon=longitude, aqi, timestamp
        '''
        query = """
        CREATE TABLE IF NOT EXISTS aqi_data (
            id SERIAL PRIMARY KEY,
            country TEXT,
            city TEXT,
            lat REAL,
            lon REAL,
            aqi INTEGER,
            timestamp TIMESTAMP
        );
        """
        with self.conn.cursor() as cur:
            cur.execute(query)
            self.conn.commit()

    def insert_aqi(self, country, city, lat, lon, aqi, timestamp=None):
        '''
        This function inserts new data into the database.
        If no timestamp exists the current time is taken.
        '''
        if timestamp is None:
            timestamp = datetime.utcnow()
        query = """
        INSERT INTO aqi_data (country, city, lat, lon, aqi, timestamp)
        VALUES (%s, %s, %s, %s, %s, %s);
        """
        with self.conn.cursor() as cur:
            cur.execute(query, (country, city, lat, lon, aqi, timestamp))
            self.conn.commit()

    def get_latest_aqi(self):
        '''
        This function returns the newest aqi data.
        '''
        query = """
        SELECT country, city, lat, lon, aqi, timestamp
        FROM (
            SELECT *, ROW_NUMBER() OVER (PARTITION BY country ORDER BY timestamp DESC) as rn
            FROM aqi_data
        ) sub
        WHERE rn = 1;
        """
        with self.conn.cursor() as cur:
            cur.execute(query)
            rows = cur.fetchall()
        result = {}
        for row in rows:
            country, city, lat, lon, aqi, timestamp = row
            result[country] = {
                "city": city,
                "lat": lat,
                "lon": lon,
                "aqi": aqi,
                "timestamp": timestamp.isoformat()
            }
        return result

    def get_all_aqi(self):
        '''
        This function gets all aqi data.
        '''
        query = "SELECT * FROM aqi_data ORDER BY timestamp DESC;"
        with self.conn.cursor() as cur:
            cur.execute(query)
            return cur.fetchall()

    def count_entries(self):
        '''
        This function returns the amount of entries in the database.
        '''
        query = "SELECT COUNT(*) FROM aqi_data;"
        with self.conn.cursor() as cur:
            cur.execute(query)
            return cur.fetchone()[0]

    def get_latest_aqi_per_city(self):
        '''
        This function returns the newest aqi data for every capital.
        Uses DISTINCT ON to get only the current entry.
        '''
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT DISTINCT ON (country, city)
                    country, city, lat, lon, aqi, timestamp
                FROM aqi_data
                ORDER BY country, city, timestamp DESC
            """)
            rows = cur.fetchall()
            columns = ["country", "city", "lat", "lon", "aqi", "timestamp"]
            return [dict(zip(columns, row)) for row in rows]
