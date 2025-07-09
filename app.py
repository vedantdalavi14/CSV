"""
Smart CSV Cleaner - Web Application
Professional responsive frontend for CSV cleaning tool
"""

import os
import io
import json
import traceback
from flask import Flask, request, jsonify, render_template, send_file
import pandas as pd
from werkzeug.utils import secure_filename
from main import CSVCleaner
from parser.nlp_parser import NLPParser
import logging

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['OUTPUT_FOLDER'] = 'outputs'

# Create directories if they don't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Allowed file extensions
ALLOWED_EXTENSIONS = {'csv'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Handle file upload and initial analysis"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type. Please upload a CSV file.'}), 400
        
        # Save the uploaded file
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Load and analyze the CSV
        df = pd.read_csv(filepath)
        
        # Get basic info about the dataset
        missing_data_per_column = df.isnull().sum()
        total_missing = int(missing_data_per_column.sum())

        info = {
            'filename': filename,
            'rows': len(df),
            'columns': len(df.columns),
            'missing_values': total_missing,
            'column_names': df.columns.tolist(),
            'missing_data': missing_data_per_column.to_dict(),
            'data_types': df.dtypes.astype(str).to_dict(),
            'preview': df.head(5).to_dict('records')
        }
        
        return jsonify({
            'success': True,
            'data': info,
            'message': f'Successfully loaded {info["rows"]} rows and {info["columns"]} columns'
        })
        
    except Exception as e:
        logger.error(f"Upload error: {str(e)}")
        return jsonify({'error': f'Error processing file: {str(e)}'}), 500

@app.route('/api/parse-command', methods=['POST'])
def parse_nlp_command():
    """Parse natural language command"""
    try:
        data = request.get_json()
        command = data.get('command', '')
        
        if not command:
            return jsonify({'error': 'No command provided'}), 400
        
        parser = NLPParser()
        result = parser.parse_command(command)
        
        return jsonify({
            'success': True,
            'parsed_flags': result,
            'message': f'Parsed command: {command}'
        })
        
    except Exception as e:
        logger.error(f"Parse error: {str(e)}")
        return jsonify({'error': f'Error parsing command: {str(e)}'}), 500

@app.route('/api/clean', methods=['POST'])
def clean_file():
    data = request.json
    filename = data.get('filename')
    
    if not filename:
        return jsonify({'error': 'Filename is required'}), 400

    input_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    
    # Extract cleaning flags from request
    fix_names = data.get('fix_names', False)
    fix_missing = data.get('fix_missing')
    drop_outliers = data.get('drop_outliers')
    standardize_types = data.get('standardize_types', False)
    excel = data.get('excel', False)
    natural_command = data.get('natural_command', '')

    # New options
    remove_duplicates = data.get('remove_duplicates', False)
    trim_whitespace = data.get('trim_whitespace', False)
    change_case = data.get('change_case')
    find_replace = data.get('find_replace') # Expects {'find': 'value', 'replace': 'new_value'}
    drop_columns_str = data.get('drop_columns', '')
    drop_columns = [col.strip() for col in drop_columns_str.split(',') if col.strip()] if drop_columns_str else None

    # Instantiate the cleaner and process
    try:
        # Note: logger is now handled inside CSVCleaner
        cleaner = CSVCleaner(zscore_threshold=3.0, logger=app.logger) 
        result = cleaner.process_csv(
            input_file=input_path,
            natural_command=natural_command,
            fix_names=fix_names,
            fix_missing=fix_missing,
            drop_outliers=drop_outliers,
            standardize_types=standardize_types,
            remove_duplicates=remove_duplicates,
            trim_whitespace=trim_whitespace,
            change_case=change_case,
            find_replace=find_replace,
            drop_columns=drop_columns,
            excel=excel,
            preview=True # Always get a preview for the web UI
        )
        return jsonify(result)
    except Exception as e:
        app.logger.error(f"An error occurred during cleaning: {str(e)}\n{traceback.format_exc()}")
        return jsonify({'error': f'An internal error occurred: {str(e)}'}), 500

@app.route('/api/download/<filename>')
def download_file(filename):
    """Download cleaned file"""
    try:
        filepath = os.path.join(app.config['OUTPUT_FOLDER'], filename)
        if not os.path.exists(filepath):
            return jsonify({'error': 'File not found'}), 404
        
        return send_file(filepath, as_attachment=True, download_name=filename)
        
    except Exception as e:
        logger.error(f"Download error: {str(e)}")
        return jsonify({'error': f'Error downloading file: {str(e)}'}), 500

@app.route('/api/supported-commands')
def get_supported_commands():
    """Get list of supported natural language commands"""
    try:
        parser = NLPParser()
        commands = parser.get_supported_commands()
        return jsonify({
            'success': True,
            'commands': commands
        })
    except Exception as e:
        logger.error(f"Commands error: {str(e)}")
        return jsonify({'error': f'Error getting commands: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)