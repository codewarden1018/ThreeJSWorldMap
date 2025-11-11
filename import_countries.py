"""
Import world countries into the database
This imports the same data that the globe.js was loading externally
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

def import_world_countries():
    """
    Import world countries from the same source used by globe.js
    """
    # Same URL that globe.js was using
    url = "https://raw.githubusercontent.com/datasets/geo-countries/master/data/countries.geojson"

    print(f"Fetching world countries from: {url}")
    response = requests.get(url)
    data = response.json()

    db = get_db()
    cursor = db.cursor()

    imported = 0
    skipped = 0

    for feature in data['features']:
        properties = feature['properties']
        geometry = feature['geometry']

        # Get country name
        name = properties.get('ADMIN') or properties.get('name') or 'Unknown'

        # Get ISO code - try multiple property names
        code = (properties.get('ISO_A3') or
                properties.get('iso_a3') or
                properties.get('ADM0_A3') or
                properties.get('SOV_A3'))

        # If code is '-99' or similar placeholder, use alternative code
        if not code or code == '-99' or code == -99:
            # Try alternative code fields
            code = (properties.get('WB_A3') or
                    properties.get('BRK_A3') or
                    properties.get('ADM0_A3'))

            # If still no valid code, generate from name
            if not code or code == '-99' or code == -99:
                code = name[:3].upper().replace(' ', '')
                print(f"  [WARN] Generated code for {name}: {code}")

        try:
            # Store additional properties as custom_data
            custom_data = {
                'iso_a2': properties.get('ISO_A2'),
                'continent': properties.get('CONTINENT'),
                'region_un': properties.get('REGION_UN'),
                'subregion': properties.get('SUBREGION'),
                'color': '#66ffcc'  # Default cyan color
            }

            cursor.execute('''
                INSERT OR REPLACE INTO regions
                (name, code, region_type, geojson_data, custom_data)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                name,
                code,
                'country',
                json.dumps(geometry),
                json.dumps(custom_data)
            ))
            imported += 1
            print(f"  [OK] Imported: {name} ({code})")
        except Exception as e:
            print(f"  [ERROR] Error importing {name}: {e}")

    db.commit()
    db.close()

    print(f"\nSuccessfully imported {imported} countries!")
    print(f"Skipped {skipped} regions (invalid/missing codes)")
    return imported

if __name__ == '__main__':
    print("="*60)
    print("World Countries Importer")
    print("="*60)
    print("\nImporting world countries from GitHub...")
    print("(Same data source as globe.js external fallback)")
    print()

    try:
        import_world_countries()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "="*60)
    print("Import complete!")
    print("The Flask server will auto-reload and use database data.")
    print("="*60)
