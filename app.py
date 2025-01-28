from flask import Flask, request, jsonify
from flask_cors import CORS
import json
from datetime import datetime
import os

app = Flask(__name__)
CORS(app)

DATA_FILE = 'wordle_data.json'

def initialize_data_file():
    if not os.path.exists(DATA_FILE) or os.path.getsize(DATA_FILE) == 0:
        with open(DATA_FILE, 'w') as f:
            json.dump({}, f, indent=2)

def load_data():
    initialize_data_file()
    with open(DATA_FILE, 'r') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            empty_data = {}
            save_data(empty_data)
            return empty_data

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

@app.route('/submit', methods=['POST'])
def submit_game():
    data = request.json
    all_data = load_data()
    
    date = datetime.now().strftime('%Y-%m-%d')
    if date not in all_data:
        all_data[date] = {}
    
    all_data[date][data['player']] = {
        'guesses': data['guesses'],
        'states': data['states'],
        'success': data['success'],
        'attempts': data['attempts'],
        'duration': data['duration']
    }
    
    save_data(all_data)
    return jsonify({'status': 'success'})

@app.route('/results', methods=['GET'])
def get_results():
    date = request.args.get('date', datetime.now().strftime('%Y-%m-%d'))
    data = load_data()
    return jsonify(data.get(date, {}))

initialize_data_file()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)