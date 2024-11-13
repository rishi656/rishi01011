from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)

# Helper function to connect to the database
def get_db():
    conn = sqlite3.connect('items.db')
    conn.row_factory = sqlite3.Row
    return conn

# Initialize the database (create table if it doesn't exist)
def init_db():
    conn = get_db()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/items', methods=['POST'])
def create_item():
    data = request.get_json()

    # Input validation
    if not data or not 'name' in data:
        return jsonify({"error": "Missing 'name' in request data"}), 400

    name = data['name']
    description = data.get('description', '')

    conn = get_db()
    conn.execute('INSERT INTO items (name, description) VALUES (?, ?)', (name, description))
    conn.commit()
    conn.close()

    return jsonify({"message": "Item created successfully"}), 201

@app.route('/items', methods=['GET'])
def get_items():
    conn = get_db()
    cursor = conn.execute('SELECT * FROM items')
    items = [dict(row) for row in cursor.fetchall()]
    conn.close()

    return jsonify(items)

@app.route('/items/<int:id>', methods=['GET'])
def get_item(id):
    conn = get_db()
    cursor = conn.execute('SELECT * FROM items WHERE id = ?', (id,))
    item = cursor.fetchone()
    conn.close()

    if item is None:
        return jsonify({"error": "Item not found"}), 404

    return jsonify(dict(item))

@app.route('/items/<int:id>', methods=['PUT'])
def update_item(id):
    data = request.get_json()

    if not data:
        return jsonify({"error": "No data provided"}), 400

    name = data.get('name')
    description = data.get('description')

    conn = get_db()

    # Only update fields that are provided
    if name:
        conn.execute('UPDATE items SET name = ? WHERE id = ?', (name, id))
    if description:
        conn.execute('UPDATE items SET description = ? WHERE id = ?', (description, id))

    conn.commit()
    conn.close()

    return jsonify({"message": "Item updated successfully"}), 200

@app.route('/items/<int:id>', methods=['DELETE'])
def delete_item(id):
    conn = get_db()
    cursor = conn.execute('SELECT * FROM items WHERE id = ?', (id,))
    item = cursor.fetchone()

    if item is None:
        return jsonify({"error": "Item not found"}), 404

    conn.execute('DELETE FROM items WHERE id = ?', (id,))
    conn.commit()
    conn.close()

    return jsonify({"message": "Item deleted successfully"}), 200

if __name__ == '__main__':
    init_db()  # Create the database and table on startup
    app.run(debug=True)
