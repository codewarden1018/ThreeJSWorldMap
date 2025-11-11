"""
Test MySQL Connection
This script helps you find the correct MySQL connection settings
"""
import pymysql

def test_connection(host, user, password, port):
    """Test a MySQL connection with given parameters"""
    try:
        conn = pymysql.connect(
            host=host,
            user=user,
            password=password,
            port=port,
            charset='utf8mb4'
        )
        print(f"✓ SUCCESS! Connected to MySQL at {host}:{port}")
        print(f"  Username: {user}")
        print(f"  Password: {'(empty)' if password == '' else password}")

        # Try to show databases
        cursor = conn.cursor()
        cursor.execute("SHOW DATABASES")
        databases = cursor.fetchall()
        print(f"\n  Available databases:")
        for db in databases:
            print(f"    - {db[0]}")

        conn.close()
        return True
    except Exception as e:
        print(f"✗ Failed to connect to {host}:{port}")
        print(f"  Error: {e}")
        return False

print("Testing MySQL Connection Settings...\n")
print("=" * 60)

# Common configurations to try
configs = [
    ('localhost', 'root', 'root', 8889, 'MAMP default'),
    ('localhost', 'root', '', 8889, 'MAMP with no password'),
    ('localhost', 'root', 'root', 3306, 'Standard MySQL with MAMP password'),
    ('localhost', 'root', '', 3306, 'Standard MySQL with no password'),
    ('127.0.0.1', 'root', 'root', 8889, 'MAMP via 127.0.0.1'),
    ('127.0.0.1', 'root', '', 3306, 'Standard MySQL via 127.0.0.1'),
]

successful_config = None

for host, user, password, port, description in configs:
    print(f"\nTrying: {description}")
    print(f"  Host: {host}, Port: {port}, User: {user}, Pass: {'(empty)' if password == '' else password}")

    if test_connection(host, user, password, port):
        successful_config = (host, user, password, port)
        print("\n" + "=" * 60)
        print("SUCCESS! Use these settings in config.py:")
        print("=" * 60)
        print(f"""
DB_CONFIG = {{
    'host': '{host}',
    'user': '{user}',
    'password': '{password}',
    'database': 'globe_db',
    'charset': 'utf8mb4',
    'port': {port}
}}
        """)
        break
    print("-" * 60)

if not successful_config:
    print("\n" + "=" * 60)
    print("❌ Could not connect with any common configuration!")
    print("=" * 60)
    print("\nPlease check:")
    print("1. Is MAMP/MySQL running?")
    print("2. Check phpMyAdmin - what port does it show?")
    print("3. Try starting MySQL/MAMP and run this script again")
    print("\nIf you know your MySQL settings, edit config.py manually:")
    print("  - Host (usually 'localhost' or '127.0.0.1')")
    print("  - Port (usually 3306 or 8889)")
    print("  - Username (usually 'root')")
    print("  - Password (might be empty, 'root', or something else)")
