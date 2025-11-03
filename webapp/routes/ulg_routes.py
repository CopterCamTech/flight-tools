from flask import Blueprint, request, render_template, current_app
import os
from werkzeug.utils import secure_filename

from tools.ulg_power_plot import generate_power_plot
from tools.ulg_info import generate_ulg_info
from tools.ulg_parameter_list import generate_parameter_list
from tools.ulg_range_signal import flask_entry as generate_range_signal
from tools.ulg_log_explorer import (
    parse_ulg_file,
    get_fields_from_log,
    extract_field_data
)

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

@ulg_bp.route('/ulg-log-explorer', methods=['GET', 'POST'])
def ulg_log_explorer():
    filename = None
    message_types = []
    fields = []
    selected_type = None
    selected_field = None
    report_data = None
    error = None

    upload_dir = current_app.config['UPLOAD_FOLDER']

    if request.method == 'POST':
        file = request.files.get('file')
        filename = request.form.get('filename')
        selected_type = request.form.get('msg_type')
        selected_field = request.form.get('field_name')

        # Step 1: File upload
        if file and file.filename.lower().endswith('.ulg'):
            filename = secure_filename(file.filename)
            filepath = os.path.join(upload_dir, filename)
            file.save(filepath)
            try:
                ulog, message_types = parse_ulg_file(filepath)
            except Exception as e:
                error = f"❌ Failed to parse .ulg file: {e}"
                return render_template('ulg_log_explorer.html', error=error)
            return render_template('ulg_log_explorer.html', filename=filename, message_types=message_types)

        # Step 2: Message type selected
        elif filename and selected_type and not selected_field:
            filepath = os.path.join(upload_dir, filename)
            try:
                ulog, _ = parse_ulg_file(filepath)
                fields = get_fields_from_log(ulog, selected_type)
            except Exception as e:
                error = f"❌ Failed to extract fields: {e}"
            return render_template('ulg_log_explorer.html', filename=filename, selected_type=selected_type, fields=fields, error=error)

        # Step 3: Field selected
        elif filename and selected_type and selected_field:
            filepath = os.path.join(upload_dir, filename)
            try:
                ulog, _ = parse_ulg_file(filepath)
                report_data = extract_field_data(ulog, selected_type, selected_field)
                if not report_data:
                    error = "No data found for selected field."
            except Exception as e:
                error = f"❌ Failed to extract data: {e}"
            return render_template('ulg_log_explorer.html', filename=filename, selected_type=selected_type, selected_field=selected_field, report_data=report_data, error=error)

    return render_template('ulg_log_explorer.html')
