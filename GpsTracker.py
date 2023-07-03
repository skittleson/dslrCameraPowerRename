# pip install pynmea2 pyserial pysqlite3

#  For Windows
# pip install pysqlite-binary
import serial
import pynmea2
import sqlite3


class GpsTracker:
    """Collect moving gps device to a sqlite database file"""

    def __init__(self, port):
        self.port = port

    def __del__(self):
        if self.ser is not None:
            if self.ser.is_open:
                self.ser.close()
            self.ser = None

    def get_current_position(self):
        self.ser = serial.Serial(self.port, baudrate=9600, timeout=1.0)
        while True:
            newdata = self.ser.readline().decode("utf-8")
            if newdata[0:6] == "$GPRMC":
                gprmc = pynmea2.parse(newdata)
                return {'timestamp': gprmc.datetime, 'latitude': gprmc.latitude, 'longitude': gprmc.longitude}

    def tracking(self, sqlite_database_name, track_at_speed: float = 0, ):
        self.ser = serial.Serial(self.port, baudrate=9600, timeout=1.0)
        conn = sqlite3.connect(sqlite_database_name)
        cursor = conn.cursor()
        cursor.execute(""" 
        CREATE TABLE IF NOT EXISTS gps (
        timestamp INTEGER NOT NULL,
        status TEXT NOT NULL,
        lat REAL NOT NULL,
        lat_dir TEXT NOT NULL,
        lon REAL NOT NULL,
        lon_dir TEXT NOT NULL,
        spd_over_grnd REAL NOT NULL,
        true_course TEXT,
        datestamp INTEGER NOT NULL,
        mag_variation TEXT,
        mag_var_dir TEXT,
        mode_indicator TEXT)""")
        conn.commit()

        # Start collecting data
        while True:
            newdata = self.ser.readline().decode("utf-8")
            if newdata[0:6] == "$GPRMC":
                gprmc = pynmea2.parse(newdata, True)
                if len(gprmc.data) == 12:
                    speed = float(gprmc.data[6])
                    if speed > track_at_speed:
                        cursor.execute(
                            "INSERT INTO gps VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",  gprmc.data)
                        conn.commit()


if __name__ == '__main__':
    # GpsTracker('COM4').tracking('gps.db', 2)
    print(GpsTracker('COM4').get_current_position())
