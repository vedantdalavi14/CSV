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
        info = {
            'filename': filename,
            'rows': len(df),
            'columns': len(df.columns),
            'column_names': df.columns.tolist(),
            'missing_data': df.isnull().sum().to_dict(),
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
def parse_command():
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
def clean_csv():
    """Clean the CSV file"""
    try:
        data = request.get_json()
        filename = data.get('filename')
        natural_command = data.get('natural_command', '')
        fix_names = data.get('fix_names', False)
        fix_missing = data.get('fix_missing')
        drop_outliers = data.get('drop_outliers')
        standardize_types = data.get('standardize_types', False)
        excel_export = data.get('excel_export', False)
        zscore_threshold = data.get('zscore_threshold', 3.0)
        
        if not filename:
            return jsonify({'error': 'No filename provided'}), 400
        
        input_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if not os.path.exists(input_path):
            return jsonify({'error': 'File not found'}), 404
        
        # Create output filename
        base_name = os.path.splitext(filename)[0]
        output_filename = f"{base_name}_cleaned.csv"
        output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)
        
        # Initialize cleaner
        cleaner = CSVCleaner(logger, zscore_threshold)
        
        # Process the CSV
        result = cleaner.process_csv(
            input_file=input_path,
            natural_command=natural_command,
            fix_names=fix_names,
            fix_missing=fix_missing,
            drop_outliers=drop_outliers,
            standardize_types=standardize_types,
            output=output_path,
            excel=excel_export,
            preview=False  # We'll handle preview separately
        )
        
        if not result['success']:
            return jsonify({'error': result['error']}), 500
        
        # Load the cleaned data for preview
        cleaned_df = pd.read_csv(output_path)
        
        # Prepare response
        response_data = {
            'success': True,
            'message': result['summary'],
            'output_filename': output_filename,
            'cleaned_data': {
                'rows': len(cleaned_df),
                'columns': len(cleaned_df.columns),
                'column_names': cleaned_df.columns.tolist(),
                'preview': cleaned_df.head(10).to_dict('records'),
                'data_types': cleaned_df.dtypes.astype(str).to_dict()
            }
        }
        
        # Add Excel file if requested
        if excel_export:
            excel_filename = f"{base_name}_cleaned.xlsx"
            excel_path = os.path.join(app.config['OUTPUT_FOLDER'], excel_filename)
            cleaned_df.to_excel(excel_path, index=False)
            response_data['excel_filename'] = excel_filename
        
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"Cleaning error: {str(e)}\n{traceback.format_exc()}")
        return jsonify({'error': f'Error cleaning CSV: {str(e)}'}), 500

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