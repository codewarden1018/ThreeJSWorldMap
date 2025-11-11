# Database Configuration
# Update these values according to your MySQL setup

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',          # From phpMyAdmin: root@localhost
    'password': '',          # Try empty password first
    'database': 'globe_db',
    'charset': 'utf8mb4',
    'port': 3306             # Standard MySQL port
}

# Flask Configuration
FLASK_CONFIG = {
    'debug': True,
    'host': '0.0.0.0',
    'port': 5000
}
