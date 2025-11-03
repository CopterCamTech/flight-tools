from flask import Blueprint, request, render_template, current_app
import os
from werkzeug.utils import secure_filename
from tools.ulg_power_plot import generate_power_plot
from tools.ulg_info import generate_ulg_info
from tools.ulg_parameter_list import generate_parameter_list
from tools.ulg_range_signal import flask_entry as generate_range_signal

ulg_bp = Blueprint('ulg_bp', __name__)

@ulg_bp.route('/ulg-power', methods=['GET', 'POST'])
def ulg_power():
    chart_data = None
    filename = None
    if request.method == 'POST':
        file = request.files.get('file')
        if file and file.filename.lower().endswith('.ulg'):
            filename = secure_filename(file.filename)
            upload_dir = current_app.config['UPLOAD_FOLDER']
            filepath = os.path.join(upload_dir, filename)
            file.save(filepath)
            result = generate_power_plot(filepath)
            chart_data = result.get("image_data")
    return render_template('ulg_power.html', chart_data=chart_data, filename=filename)

@ulg_bp.route('/ulg-info', methods=['GET', 'POST'])
def ulg_info():
    summary = None
    filename = None
    if request.method == 'POST':
        file = request.files.get('file')
        if file:
            filename = secure_filename(file.filename)
            if filename.lower().endswith('.ulg'):
                upload_dir = current_app.config['UPLOAD_FOLDER']
                filepath = os.path.join(upload_dir, filename)
                file.save(filepath)
                result = generate_ulg_info(filepath)
                summary = result
            else:
                summary = {'error': 'Invalid file type. Please upload a .ULG file.'}
        else:
            summary = {'error': 'No file uploaded.'}
    return render_template('ulg_info.html', summary=summary, filename=filename)

@ulg_bp.route('/ulg-parameter-list', methods=['GET', 'POST'])
def ulg_parameter_list():
    if request.method == 'POST':
        file = request.files.get('logfile')
        if not file:
            return render_template('ulg_parameter_list.html', summary={'error': 'No file uploaded'})
        
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)

        summary = generate_parameter_list(filepath)
        return render_template('ulg_parameter_list.html', summary=summary)

    return render_template('ulg_parameter_list.html')

@ulg_bp.route('/ulg-range-signal', methods=['GET', 'POST'])
def ulg_range_signal():
    chart_data = None
    filename = None
    if request.method == 'POST':
        file = request.files.get('file')
        if file and file.filename.lower().endswith('.ulg'):
            filename = secure_filename(file.filename)
            upload_dir = current_app.config['UPLOAD_FOLDER']
            filepath = os.path.join(upload_dir, filename)
            file.save(filepath)
            try:
                result = generate_range_signal(filepath)
                chart_data = result.get("image_data")
            except Exception as e:
                print(f"❌ Error in ulg_range_signal: {e}")
    return render_template('ulg_range_signal.html', chart_data=chart_data, filename=filename)
