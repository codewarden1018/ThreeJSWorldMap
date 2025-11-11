from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import sqlite3
import json
import os

app = Flask(__name__)
CORS(app)

# Database configuration
DATABASE = 'database/globe.db'

def get_db():
    """Connect to the SQLite database"""
    db = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row
    return db

def init_db():
    """Initialize the database with schema"""
    os.makedirs('database', exist_ok=True)
    db = get_db()
    cursor = db.cursor()

    # Create regions table (supports countries and sub-regions)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS regions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            code TEXT UNIQUE,
            parent_id INTEGER,
            region_type TEXT DEFAULT 'country',
            geojson_data TEXT,
            custom_data TEXT,
            owner TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (parent_id) REFERENCES regions(id)
        )
    ''')

    db.commit()
    db.close()
    print("Database initialized successfully!")

@app.route('/')
def index():
    """Render the main SPA page"""
    return render_template('index.html')

@app.route('/api/regions', methods=['GET'])
def get_regions():
    """Get all regions or filter by type/parent"""
    region_type = request.args.get('type', None)
    parent_id = request.args.get('parent_id', None)

    db = get_db()
    cursor = db.cursor()

    query = 'SELECT * FROM regions WHERE 1=1'
    params = []

    if region_type:
        query += ' AND region_type = ?'
        params.append(region_type)

    if parent_id:
        query += ' AND parent_id = ?'
        params.append(parent_id)

    cursor.execute(query, params)
    regions = cursor.fetchall()
    db.close()

    return jsonify([dict(row) for row in regions])

@app.route('/api/regions/geojson', methods=['GET'])
def get_regions_geojson():
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT geojson_data, owner, code, parent_id FROM regions WHERE geojson_data IS NOT NULL')
    rows = cursor.fetchall()
    db.close()

    features = []
    for row in rows:
        geojson = json.loads(row['geojson_data'])
        # Add or override properties to carry needed info (code, owner, parent_id)
        if 'properties' not in geojson:
            geojson['properties'] = {}
        geojson['properties'].update({
            'owner': row['owner'],
            'code': row['code'],
            'parent_id': row['parent_id']
        })
        features.append(geojson)

    merged = {
        "type": "FeatureCollection",
        "features": features
    }

    return jsonify(merged)

@app.route('/api/region/<int:region_id>', methods=['GET'])
def get_region(region_id):
    """Get a specific region by ID"""
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM regions WHERE id = ?', (region_id,))
    region = cursor.fetchone()
    db.close()

    if region:
        return jsonify(dict(region))
    return jsonify({'error': 'Region not found'}), 404

@app.route('/api/region/code/<code>', methods=['GET'])
def get_region_by_code(code):
    """Get a specific region by country code"""
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM regions WHERE code = ?', (code,))
    region = cursor.fetchone()
    db.close()

    if region:
        return jsonify(dict(region))
    return jsonify({'error': 'Region not found'}), 404

@app.route('/api/region', methods=['POST'])
def create_region():
    """Create a new region"""
    data = request.get_json()

    db = get_db()
    cursor = db.cursor()
    cursor.execute('''
        INSERT INTO regions (name, code, parent_id, region_type, geojson_data, custom_data, owner)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        data.get('name'),
        data.get('code'),
        data.get('parent_id'),
        data.get('region_type', 'country'),
        data.get('geojson_data'),
        data.get('custom_data'),
        data.get('owner')
    ))
    db.commit()
    region_id = cursor.lastrowid
    db.close()

    return jsonify({'id': region_id, 'message': 'Region created successfully'}), 201

@app.route('/api/region/<int:region_id>', methods=['PUT'])
def update_region(region_id):
    """Update an existing region"""
    data = request.get_json()

    db = get_db()
    cursor = db.cursor()
    cursor.execute('''
        UPDATE regions
        SET name = ?, code = ?, parent_id = ?, region_type = ?,
            geojson_data = ?, custom_data = ?, owner = ?
        WHERE id = ?
    ''', (
        data.get('name'),
        data.get('code'),
        data.get('parent_id'),
        data.get('region_type'),
        data.get('geojson_data'),
        data.get('custom_data'),
        data.get('owner'),
        region_id
    ))
    db.commit()
    db.close()

    return jsonify({'message': 'Region updated successfully'})

if __name__ == '__main__':
    init_db()
    print("\n" + "="*60)
    print("Interactive Globe Server Starting...")
    print("="*60)
    print("Open in browser: http://localhost:5000")
    print("Using SQLite database: database/globe.db")
    print("="*60 + "\n")
    app.run(debug=True, host='0.0.0.0', port=5000)
