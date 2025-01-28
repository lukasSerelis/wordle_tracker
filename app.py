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

# Use the mounted disk path from render.yaml
DATA_DIR = '/data'
STORAGE_FILE = os.path.join(DATA_DIR, 'wordle_data.json')

def ensure_data_dir():
    """Ensure the data directory exists"""
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
        logger.info(f"Created data directory at {DATA_DIR}")

def load_data():
    """Load data from storage file, creating it if it doesn't exist"""
    try:
        ensure_data_dir()
        if os.path.exists(STORAGE_FILE):
            with open(STORAGE_FILE, 'r') as f:
                logger.info(f"Loading data from {STORAGE_FILE}")
                return json.load(f)
        else:
            # Initialize with empty structure
            logger.info(f"No existing data file at {STORAGE_FILE}, creating new")
            return {}
    except Exception as e:
        logger.error(f"Error loading data: {e}")
        return {}

def save_data(data):
    """Save data to storage file"""
    try:
        ensure_data_dir()
        logger.info(f"Attempting to save data to {STORAGE_FILE}")
        with open(STORAGE_FILE, 'w') as f:
            json.dump(data, f, indent=2)
        logger.info("Data saved successfully")
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
        logger.info(f"Loaded existing data: {data}")
        
        # Get today's date
        today = datetime.now().strftime('%Y-%m-%d')
        
        # Initialize the date entry if it doesn't exist
        if today not in data:
            data[today] = {}
            
        # Store the new result
        data[today][result['player']] = {
            'guesses': result['guesses'],
            'states': result.get('states', []),  # Add support for letter states
            'success': result['success'],
            'attempts': len(result['guesses'])
        }
        
        logger.info(f"Storing data for {today}: {data[today]}")
        
        # Save the updated data
        if save_data(data):
            return jsonify({"message": "Result saved successfully", "data": data[today]}), 201
        else:
            return jsonify({"error": "Failed to save data"}), 500
            
    except Exception as e:
        logger.error(f"Error in submit_result: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500

# ... rest of your routes remain the same ...

@app.route('/debug', methods=['GET'])
def debug():
    """Debug endpoint to check server status and data"""
    try:
        data = load_data()
        return jsonify({
            "status": "running",
            "current_directory": os.getcwd(),
            "data_directory": DATA_DIR,
            "storage_file_path": STORAGE_FILE,
            "files_in_data_dir": os.listdir(DATA_DIR) if os.path.exists(DATA_DIR) else [],
            "current_data": data
        })
    except Exception as e:
        logger.error(f"Error in debug: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500