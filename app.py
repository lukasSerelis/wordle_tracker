import os
import json
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/submit', methods=['POST'])
def submit_result():
    try:
        # Log the raw request data
        print("Raw request data:", request.get_data())
        
        result = request.json
        print("Parsed JSON data:", result)
        
        # Get current working directory and file path
        current_dir = os.getcwd()
        file_path = os.path.join(current_dir, 'wordle_data.json')
        print(f"Attempting to write to: {file_path}")
        
        # Read existing data
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
                print("Existing data:", data)
        except FileNotFoundError:
            print("File not found, creating new data array")
            data = []
        except json.JSONDecodeError:
            print("JSON decode error, creating new data array")
            data = []
            
        # Append new data
        data.append(result)
        print("Data after append:", data)
        
        # Write updated data
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=4)
        print("Data successfully written to file")
        
        return jsonify({"message": "Result saved successfully", "data": result}), 201
    
    except Exception as e:
        print(f"Error in submit_result: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/results', methods=['GET'])
def get_results():
    try:
        with open('wordle_data.json', 'r') as f:
            data = json.load(f)
        return jsonify(data)
    except FileNotFoundError:
        return jsonify([])
    except Exception as e:
        print(f"Error in get_results: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)