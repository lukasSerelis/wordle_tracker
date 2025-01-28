import os
import json
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return jsonify({"message": "Wordle Tracker API is running"})

@app.route('/results', methods=['GET'])
def get_results():
    try:
        with open('wordle_data.json', 'r') as f:
            data = json.load(f)
        return jsonify(data)
    except FileNotFoundError:
        return jsonify({"error": "No data found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/submit', methods=['POST'])
def submit_result():
    try:
        result = request.json
        with open('wordle_data.json', 'r') as f:
            data = json.load(f)
        
        data.append(result)
        
        with open('wordle_data.json', 'w') as f:
            json.dump(data, f, indent=4)
            
        return jsonify({"message": "Result saved successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)