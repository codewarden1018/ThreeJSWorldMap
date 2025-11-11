from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import pymysql
import json
from config import DB_CONFIG, FLASK_CONFIG

app = Flask(__name__)
CORS(app)

# Add DictCursor to DB_CONFIG
DB_CONFIG['cursorclass'] = pymysql.cursors.DictCursor

def get_db():
    """Connect to the MySQL database"""
    return pymysql.connect(**DB_CONFIG)

def init_db():
    """Initialize the database with schema"""
    # First, create database if it doesn't exist
    conn = pymysql.connect(
        host=DB_CONFIG['host'],
        user=DB_CONFIG['user'],
        password=DB_CONFIG['password'],
        charset='utf8mb4'
    )
    cursor = conn.cursor()
    cursor.execute('CREATE DATABASE IF NOT EXISTS globe_db')
    conn.close()

    # Now create tables
    db = get_db()
    cursor = db.cursor()

    # Create regions table (supports countries and sub-regions)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS regions (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            code VARCHAR(10) UNIQUE,
            parent_id INT,
            region_type VARCHAR(50) DEFAULT 'country',
            geojson_data LONGTEXT,
            custom_data TEXT,
            owner VARCHAR(255),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (parent_id) REFERENCES regions(id) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    ''')

    db.commit()
    db.close()

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
        query += ' AND region_type = %s'
        params.append(region_type)

    if parent_id:
        query += ' AND parent_id = %s'
        params.append(parent_id)

    cursor.execute(query, params)
    regions = cursor.fetchall()
    db.close()

    return jsonify(regions)

@app.route('/api/region/<int:region_id>', methods=['GET'])
def get_region(region_id):
    """Get a specific region by ID"""
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM regions WHERE id = %s', (region_id,))
    region = cursor.fetchone()
    db.close()

    if region:
        return jsonify(region)
    return jsonify({'error': 'Region not found'}), 404

@app.route('/api/region/code/<code>', methods=['GET'])
def get_region_by_code(code):
    """Get a specific region by country code"""
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM regions WHERE code = %s', (code,))
    region = cursor.fetchone()
    db.close()

    if region:
        return jsonify(region)
    return jsonify({'error': 'Region not found'}), 404

@app.route('/api/region', methods=['POST'])
def create_region():
    """Create a new region"""
    data = request.get_json()

    db = get_db()
    cursor = db.cursor()
    cursor.execute('''
        INSERT INTO regions (name, code, parent_id, region_type, geojson_data, custom_data, owner)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
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
        SET name = %s, code = %s, parent_id = %s, region_type = %s,
            geojson_data = %s, custom_data = %s, owner = %s
        WHERE id = %s
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
    app.run(**FLASK_CONFIG)
