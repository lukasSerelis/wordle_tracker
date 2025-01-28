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
        # Create file if it doesn't exist
        with open('wordle_data.json', 'w') as f:
            json.dump([], f)
        return jsonify([])
    except Exception as e:
        print(f"Error reading data: {str(e)}")  # Added logging
        return jsonify({"error": str(e)}), 500

@app.route('/submit', methods=['POST'])
def submit_result():
    try:
        result = request.json
        print(f"Received data: {result}")  # Added logging
        
        # Initialize data list
        try:
            with open('wordle_data.json', 'r') as f:
                data = json.load(f)
        except FileNotFoundError:
            data = []
        except json.JSONDecodeError:
            data = []
            
        data.append(result)
        
        # Write updated data
        with open('wordle_data.json', 'w') as f:
            json.dump(data, f, indent=4)
        
        print(f"Data saved successfully. Total entries: {len(data)}")  # Added logging
        return jsonify({"message": "Result saved successfully", "data": result}), 201
    
    except Exception as e:
        print(f"Error saving data: {str(e)}")  # Added logging
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)