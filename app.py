import os
import json
import logging
import stat
from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Initialize global variables
DATA_DIR = '/data'
STORAGE_FILE = os.path.join(DATA_DIR, 'wordle_data.json')

def update_storage_paths(new_dir):
    """Update storage paths globally"""
    global DATA_DIR, STORAGE_FILE
    DATA_DIR = new_dir
    STORAGE_FILE = os.path.join(DATA_DIR, 'wordle_data.json')
    logger.info(f"Updated storage paths - DIR: {DATA_DIR}, FILE: {STORAGE_FILE}")

def ensure_data_dir():
    """Ensure the data directory exists with proper permissions"""
    try:
        if not os.path.exists(DATA_DIR):
            os.makedirs(DATA_DIR, mode=0o777)
            logger.info(f"Created data directory at {DATA_DIR}")
        
        # Ensure proper permissions
        os.chmod(DATA_DIR, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
        logger.info(f"Set permissions for {DATA_DIR}")
        
        # If file exists, ensure it has proper permissions
        if os.path.exists(STORAGE_FILE):
            os.chmod(STORAGE_FILE, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
            logger.info(f"Set permissions for {STORAGE_FILE}")
    except Exception as e:
        logger.error(f"Error setting up data directory: {e}")
        # Try fallback to current directory
        update_storage_paths(os.getcwd())
        logger.info(f"Using fallback directory: {DATA_DIR}")

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
        # Ensure proper permissions on the new file
        os.chmod(STORAGE_FILE, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
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
            'states': result.get('states', []),
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
        dir_info = {
            "exists": os.path.exists(DATA_DIR),
            "permissions": oct(os.stat(DATA_DIR).st_mode)[-3:] if os.path.exists(DATA_DIR) else None,
            "owner": os.stat(DATA_DIR).st_uid if os.path.exists(DATA_DIR) else None
        } if DATA_DIR else {}
        
        file_info = {
            "exists": os.path.exists(STORAGE_FILE),
            "permissions": oct(os.stat(STORAGE_FILE).st_mode)[-3:] if os.path.exists(STORAGE_FILE) else None,
            "owner": os.stat(STORAGE_FILE).st_uid if os.path.exists(STORAGE_FILE) else None
        } if STORAGE_FILE else {}
        
        return jsonify({
            "status": "running",
            "current_directory": os.getcwd(),
            "data_directory": DATA_DIR,
            "data_dir_info": dir_info,
            "storage_file_path": STORAGE_FILE,
            "storage_file_info": file_info,
            "files_in_data_dir": os.listdir(DATA_DIR) if os.path.exists(DATA_DIR) else [],
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