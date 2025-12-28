import os
from configparser import ConfigParser

# project root directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# read configuration file
config = ConfigParser()
config_file = os.path.join(BASE_DIR, 'config.ini')
config.read(config_file, encoding='utf-8')

# application config
APP_NAME = config.get('APP', 'NAME')
APP_VERSION = config.get('APP', 'VERSION')
APP_DESCRIPTION = config.get('APP', 'DESCRIPTION')

# database config
DB_TYPE = config.get('DATABASE', 'TYPE')

if DB_TYPE == 'sqlite':
    # SQLite database configuration
    DB_NAME = config.get('DATABASE', 'SQLITE_NAME')
    DB_PATH = config.get('DATABASE', 'SQLITE_PATH')

    # create full path for SQLite database
    db_full_path = os.path.join(BASE_DIR, DB_PATH, DB_NAME)
    # ensure the directory exists
    os.makedirs(os.path.dirname(db_full_path), exist_ok=True)
    DB_URL = f"sqlite:///{db_full_path}"
elif DB_TYPE == 'mysql':
    # MySQL database configuration
    MYSQL_HOST = config.get('DATABASE', 'MYSQL_HOST')
    MYSQL_PORT = config.get('DATABASE', 'MYSQL_PORT')
    MYSQL_USER = config.get('DATABASE', 'MYSQL_USER')
    MYSQL_PASSWORD = config.get('DATABASE', 'MYSQL_PASSWORD')
    MYSQL_DB_NAME = config.get('DATABASE', 'MYSQL_DB_NAME')

    # create MySQL connection URL
    DB_URL = (f"mysql+pymysql://"
              f"{MYSQL_USER}:"
              f"{MYSQL_PASSWORD}@"
              f"{MYSQL_HOST}:"
              f"{MYSQL_PORT}/"
              f"{MYSQL_DB_NAME}")
else:
    raise ValueError(f"Unsupported database type: {DB_TYPE}")

print(f"{DB_URL}")

# JWT settings
JWT_SECRET_KEY = config.get('JWT', 'SECRET', fallback=None)
JWT_ALGORITHM = config.get('JWT', 'ALGORITHM', fallback='HS256')
JWT_ACCESS_EXPIRES_DAYS = config.get('JWT', 'ACCESS_EXPIRES_DAYS', fallback=7)
