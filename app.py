import os
import json
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Initialize data storage
STORAGE_FILE = 'wordle_data.json'

def load_data():
    """Load data from storage file, creating it if it doesn't exist"""
    try:
        if os.path.exists(STORAGE_FILE):
            with open(STORAGE_FILE, 'r') as f:
                return json.load(f)
        else:
            # Initialize with empty structure
            return {}
    except Exception as e:
        logger.error(f"Error loading data: {e}")
        return {}

def save_data(data):
    """Save data to storage file"""
    try:
        with open(STORAGE_FILE, 'w') as f:
            json.dump(data, f, indent=2)
        return True
    except Exception as e:
        logger.error(f"Error saving data: {e}")
        return False

@app.route('/submit', methods=['POST'])
def submit_result():
    try:
        logger.info(f"Received submission request: {request.get_data()}")
        result = request.json
        
        if not result:
            return jsonify({"error": "No data received"}), 400

        # Load existing data
        data = load_data()
        
        # Get today's date
        today = datetime.now().strftime('%Y-%m-%d')
        
        # Initialize the date entry if it doesn't exist
        if today not in data:
            data[today] = {}
            
        # Store the new result
        data[today][result['player']] = {
            'guesses': result['guesses'],
            'success': result['success'],
            'attempts': len(result['guesses'])
        }
        
        logger.info(f"Storing data for {today}: {data[today]}")
        
        # Save the updated data
        if save_data(data):
            logger.info("Data saved successfully")
            return jsonify({"message": "Result saved successfully", "data": data[today]}), 201
        else:
            return jsonify({"error": "Failed to save data"}), 500
            
    except Exception as e:
        logger.error(f"Error in submit_result: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500

@app.route('/results', methods=['GET'])
def get_results():
    try:
        data = load_data()
        logger.info(f"Returning results: {data}")
        return jsonify(data)
    except Exception as e:
        logger.error(f"Error in get_results: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500

@app.route('/debug', methods=['GET'])
def debug():
    """Debug endpoint to check server status and data"""
    try:
        data = load_data()
        return jsonify({
            "status": "running",
            "current_directory": os.getcwd(),
            "files_in_directory": os.listdir(),
            "current_data": data
        })
    except Exception as e:
        logger.error(f"Error in debug: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500

@app.route('/clear', methods=['POST'])
def clear_data():
    """Debug endpoint to clear all data"""
    try:
        if save_data({}):
            return jsonify({"message": "Data cleared successfully"}), 200
        return jsonify({"error": "Failed to clear data"}), 500
    except Exception as e:
        logger.error(f"Error in clear_data: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)