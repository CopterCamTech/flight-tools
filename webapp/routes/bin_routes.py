from flask import Blueprint, request, render_template, current_app
import os
from werkzeug.utils import secure_filename
from tools.bin_info import generate_bin_info
from tools.bin_parameter_list import generate_parameter_list
from tools.bin_range_signal import flask_entry as generate_range_chart
from tools.bin_power_plot import flask_entry as generate_power_plot
from tools.bin_log_explorer import (parse_bin_file, get_fields_from_bin, extract_field_data_bin)

bin_bp = Blueprint('bin_bp', __name__)

@bin_bp.route('/bin-info', methods=['GET', 'POST'])
def bin_info():
    summary = None
    filename = None
    if request.method == 'POST':
        file = request.files.get('file')
        if file and file.filename.lower().endswith('.bin'):
            filename = secure_filename(file.filename)
            upload_dir = current_app.config['UPLOAD_FOLDER']
            filepath = os.path.join(upload_dir, filename)
            file.save(filepath)
            result = generate_bin_info(filepath, mode="flask")
            if 'error' in result:
                print("❌ Error returned:", result['error'])
            else:
                summary = result
    return render_template('bin_info.html', summary=summary, filename=filename)

@bin_bp.route('/bin-parameter-list', methods=['GET', 'POST'])
def bin_parameter_list():
    if request.method == 'POST':
        file = request.files.get('logfile')
        if not file:
            return render_template('bin_parameter_list.html', summary={'error': 'No file uploaded'})
        
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)

        summary = generate_parameter_list(filepath, mode="flask")
        return render_template('bin_parameter_list.html', summary=summary)

    return render_template('bin_parameter_list.html')

@bin_bp.route('/bin-range-signal', methods=['GET', 'POST'])
def bin_range_signal():
    chart_data = None
    filename = None
    if request.method == 'POST':
        file = request.files.get('logfile')
        if not file:
            return render_template('bin_range_signal.html', summary={'error': 'No file uploaded'})

        filename = secure_filename(file.filename)
        upload_dir = current_app.config['UPLOAD_FOLDER']
        filepath = os.path.join(upload_dir, filename)
        file.save(filepath)

        result = generate_range_chart(filepath)
        if 'error' in result:
            return render_template('bin_range_signal.html', summary={'error': result['error']})
        else:
            chart_data = result['figure']

    return render_template('bin_range_signal.html', chart_data=chart_data, filename=filename)

@bin_bp.route('/bin-power-plot', methods=['GET', 'POST'])
def bin_power_plot():
    chart_data = None
    filename = None
    if request.method == 'POST':
        file = request.files.get('logfile')
        if not file:
            return render_template('bin_power_plot.html', summary={'error': 'No file uploaded'})

        filename = secure_filename(file.filename)
        upload_dir = current_app.config['UPLOAD_FOLDER']
        filepath = os.path.join(upload_dir, filename)
        file.save(filepath)

        result = generate_power_plot(filepath)
        if 'error' in result:
            return render_template('bin_power_plot.html', summary={'error': result['error']})
        else:
            chart_data = result['image_data']

    # ✅ Always return the template, even for GET
    return render_template('bin_power_plot.html', chart_data=chart_data, filename=filename)

@bin_bp.route('/bin-log-explorer', methods=['GET', 'POST'])
def bin_log_explorer():
    upload_dir = current_app.config['UPLOAD_FOLDER']
    filename = None
    selected_type = None
    selected_field = None
    message_types = []
    fields = []
    report_data = []

    if request.method == 'POST':
        filename = request.form.get('filename')
        msg_type = request.form.get('msg_type')
        field_name = request.form.get('field_name')

        # Step 1: File upload
        if not filename:
            file = request.files.get('file')
            if file and file.filename.lower().endswith('.bin'):
                filename = secure_filename(file.filename)
                filepath = os.path.join(upload_dir, filename)
                file.save(filepath)
                message_types, _ = parse_bin_file(filepath)
                return render_template('bin_log_explorer.html',
                                       filename=filename,
                                       message_types=message_types)

        # Step 2: Message type selected
        elif filename and msg_type and not field_name:
            filepath = os.path.join(upload_dir, filename)
            _, messages_by_type = parse_bin_file(filepath)
            fields = get_fields_from_bin(messages_by_type, msg_type)
            return render_template('bin_log_explorer.html',
                                   filename=filename,
                                   selected_type=msg_type,
                                   fields=fields)

        # Step 3: Field selected
        elif filename and msg_type and field_name:
            filepath = os.path.join(upload_dir, filename)
            _, messages_by_type = parse_bin_file(filepath)
            report_data = extract_field_data_bin(messages_by_type, msg_type, field_name)
            return render_template('bin_log_explorer.html',
                                   filename=filename,
                                   selected_type=msg_type,
                                   selected_field=field_name,
                                   report_data=report_data)

    # Initial GET
    return render_template('bin_log_explorer.html')
