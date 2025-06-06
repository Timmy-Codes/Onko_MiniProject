"""
this is the configuration database class to handle access to the
SQLite database file that stores the user directories
"""
import sqlite3
import ctypes
import os
from pathlib import Path
import platform
from src.ConfigurationInterface import ConfigInterface
#from src.Singleton import Singleton


# class can one have one instance (singleton), and inherits from abstract class
class Configuration(ConfigInterface):
    def __init__(self, db_file="OnkoDICOM.db"):
        super().__init__()
        self.setup_hidden_directory()
        self.db_file_path = Path(os.environ['USER_ONKODICOM_HIDDEN']).joinpath(db_file)
        self.setup_configuration_database()

    def setup_hidden_directory(self):
        """
        Creates hidden directory to store the user directories
        inside an SQLite database file
        """
        path = Path.home().joinpath(".onkoDICOM")
        os.environ['USER_ONKODICOM_HIDDEN'] = str(path) # maps path to os environment key

        if not path.exists():
            path.mkdir()
            if platform.system() == "Windows":
                # access Windows API to set file attribute of path to hidden (2)
                ctypes.windll.shell32.SetFileAttributesW(str(path), 2)

    def setup_configuration_database(self):
        """
        Create the CONFIGURATION table inside the SQLite database
        """
        connection = sqlite3.connect(self.db_file_path)
        cursor = connection.cursor()
        cursor.execute("""
                CREATE TABLE IF NOT EXISTS CONFIGURATION (
                id INTEGER PRIMARY KEY,
                default_dir TEXT,
                csv_dir TEXT
                );
                """)

        # commit the changes
        connection.commit()
        # close the db connection
        connection.close()

    def get_default_directory(self) -> str:
        # connect to database
        connection = sqlite3.connect(self.db_file_path)

        cursor = connection.cursor()
        cursor.execute("SELECT default_dir FROM CONFIGURATION WHERE id = 1;")
        record = cursor.fetchone()
        connection.close()

        return None if record is None else record[0]

    def update_default_directory(self, new_directory: str) -> None:
        # connect to database
        connection = sqlite3.connect(self.db_file_path)
        cursor = connection.cursor()
        # first check if there is a default dir
        cursor.execute("SELECT COUNT(*) FROM CONFIGURATION;""")
        result = cursor.fetchone()
        if result[0] == 0: # no default dir
            # insert the new directory into the table
            cursor.execute("INSERT INTO CONFIGURATION (default_dir) VALUES (?)", (new_directory,))
        else:   # default dir exists
            # update the default dir
            cursor.execute("UPDATE CONFIGURATION SET default_dir = ? WHERE id = 1;", (new_directory,))

        # commit changes and close connection
        connection.commit()
        connection.close()
