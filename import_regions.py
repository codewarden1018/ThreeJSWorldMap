"""
Import GeoJSON regions into the database
"""
import sqlite3
import json
import requests

DATABASE = 'database/globe.db'

def get_db():
    """Connect to the SQLite database"""
    db = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row
    return db

def import_geojson_from_url(url, region_type='state', parent_code=None):
    """
    Import regions from a GeoJSON URL

    Args:
        url: URL to GeoJSON file
        region_type: Type of region (state, province, etc.)
        parent_code: Parent country/region code (e.g., 'USA')
    """
    print(f"Fetching GeoJSON from: {url}")
    response = requests.get(url)
    data = response.json()

    db = get_db()
    cursor = db.cursor()

    # Get parent_id if parent_code is provided
    parent_id = None
    if parent_code:
        cursor.execute('SELECT id FROM regions WHERE code = ?', (parent_code,))
        parent = cursor.fetchone()
        if parent:
            parent_id = parent['id']
            print(f"Found parent region: {parent_code} (ID: {parent_id})")
        else:
            print(f"Warning: Parent region '{parent_code}' not found. Creating regions without parent.")

    imported = 0
    for feature in data['features']:
        properties = feature['properties']
        geometry = feature['geometry']

        # Try to get name from common property names
        name = (properties.get('name') or
                properties.get('NAME') or
                properties.get('NAME_1') or
                properties.get('admin') or
                properties.get('ADMIN') or
                'Unknown')

        # Try to get code from common property names
        code = (properties.get('code') or
                properties.get('iso_3166_2') or
                properties.get('postal') or
                properties.get('POSTAL') or
                properties.get('iso_a2') or
                None)

        # If no code, generate one from name
        if not code:
            code = f"{parent_code}-{name.replace(' ', '').upper()[:3]}" if parent_code else name[:3].upper()

        try:
            cursor.execute('''
                INSERT OR REPLACE INTO regions
                (name, code, parent_id, region_type, geojson_data)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                name,
                code,
                parent_id,
                region_type,
                json.dumps(geometry)
            ))
            imported += 1
            print(f"  [OK] Imported: {name} ({code})")
        except Exception as e:
            print(f"  [ERROR] Error importing {name}: {e}")

    db.commit()
    db.close()

    print(f"\nSuccessfully imported {imported} regions!")
    return imported

def import_geojson_from_file(filepath, region_type='state', parent_code=None):
    """
    Import regions from a local GeoJSON file

    Args:
        filepath: Path to GeoJSON file
        region_type: Type of region (state, province, etc.)
        parent_code: Parent country/region code (e.g., 'USA')
    """
    print(f"Reading GeoJSON from: {filepath}")
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    db = get_db()
    cursor = db.cursor()

    # Get parent_id if parent_code is provided
    parent_id = None
    if parent_code:
        cursor.execute('SELECT id FROM regions WHERE code = ?', (parent_code,))
        parent = cursor.fetchone()
        if parent:
            parent_id = parent['id']
            print(f"Found parent region: {parent_code} (ID: {parent_id})")
        else:
            print(f"Warning: Parent region '{parent_code}' not found. Creating regions without parent.")

    imported = 0
    features = data.get('features', [])

    for feature in features:
        properties = feature['properties']
        geometry = feature['geometry']

        # Try to get name from common property names
        name = (properties.get('name') or
                properties.get('NAME') or
                properties.get('NAME_1') or
                properties.get('admin') or
                properties.get('ADMIN') or
                'Unknown')

        # Try to get code from common property names
        code = (properties.get('code') or
                properties.get('iso_3166_2') or
                properties.get('postal') or
                properties.get('POSTAL') or
                properties.get('iso_a2') or
                None)

        # If no code, generate one from name
        if not code:
            code = f"{parent_code}-{name.replace(' ', '').upper()[:3]}" if parent_code else name[:3].upper()

        try:
            cursor.execute('''
                INSERT OR REPLACE INTO regions
                (name, code, parent_id, region_type, geojson_data)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                name,
                code,
                parent_id,
                region_type,
                json.dumps(geometry)
            ))
            imported += 1
            print(f"  [OK] Imported: {name} ({code})")
        except Exception as e:
            print(f"  [ERROR] Error importing {name}: {e}")

    db.commit()
    db.close()

    print(f"\nSuccessfully imported {imported} regions!")
    return imported

def create_usa_country():
    """Create USA country entry as parent for states"""
    db = get_db()
    cursor = db.cursor()

    try:
        cursor.execute('''
            INSERT OR IGNORE INTO regions (name, code, region_type)
            VALUES (?, ?, ?)
        ''', ('United States', 'USA', 'country'))
        db.commit()
        print("Created USA country entry")
    except Exception as e:
        print(f"Error creating USA: {e}")

    db.close()

if __name__ == '__main__':
    print("="*60)
    print("GeoJSON Region Importer")
    print("="*60)

    # Example: Import US States
    print("\n1. Creating USA parent country...")
    create_usa_country()

    print("\n2. Importing US States...")
    # US States GeoJSON from a reliable source
    us_states_url = "https://raw.githubusercontent.com/PublicaMundi/MappingAPI/master/data/geojson/us-states.json"

    try:
        import_geojson_from_url(
            url=us_states_url,
            region_type='state',
            parent_code='USA'
        )
    except Exception as e:
        print(f"Error: {e}")
        print("\nAlternatively, you can download GeoJSON manually and import from file:")
        print("  import_geojson_from_file('path/to/file.geojson', 'state', 'USA')")

    print("\n" + "="*60)
    print("Import complete! Restart the Flask server to see changes.")
    print("="*60)
