from flask import Blueprint, request, render_template, current_app, redirect, url_for, flash
import os
from werkzeug.utils import secure_filename
from tools.bin_info import generate_bin_info
from tools.bin_parameter_list import generate_parameter_list
from tools.bin_range_signal import flask_entry as generate_range_chart
from tools.bin_power_plot import flask_entry as generate_power_plot
from tools.bin_log_explorer import (
    parse_bin_file,
    get_fields_from_bin,
    extract_field_data_bin
)
from tools.bin_parameter_compare import compare_parameters, extract_parameters

bin_bp = Blueprint('bin_bp', __name__)

# ✅ Local helper functions for this route
def get_message_types(messages):
    return sorted(set(msg.get_type() for msg in messages if hasattr(msg, 'get_type')))



def get_firmware_version(messages_by_type):
    msg_list = messages_by_type.get('MSG', [])
    for msg in msg_list:
        try:
            message = getattr(msg, 'Message', None) or getattr(msg, 'message', None)
            if message and message.startswith('Ardu'):
                return message
        except Exception:
            continue
    return "Unknown version"





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

        elif filename and msg_type and not field_name:
            filepath = os.path.join(upload_dir, filename)
            _, messages_by_type = parse_bin_file(filepath)
            fields = get_fields_from_bin(messages_by_type, msg_type)
            return render_template('bin_log_explorer.html',
                                   filename=filename,
                                   selected_type=msg_type,
                                   fields=fields)

        elif filename and msg_type and field_name:
            filepath = os.path.join(upload_dir, filename)
            _, messages_by_type = parse_bin_file(filepath)
            report_data = extract_field_data_bin(messages_by_type, msg_type, field_name)
            return render_template('bin_log_explorer.html',
                                   filename=filename,
                                   selected_type=msg_type,
                                   selected_field=field_name,
                                   report_data=report_data)

    return render_template('bin_log_explorer.html')

@bin_bp.route('/bin-parameter-compare', methods=['GET', 'POST'])
def bin_parameter_compare():
    if request.method == 'POST':
        file1 = request.files.get('logfile1')
        file2 = request.files.get('logfile2')

        if not file1 or not file2:
            flash("Please upload two log files.")
            return redirect(url_for('bin_bp.bin_parameter_compare'))

        upload_dir = current_app.config['UPLOAD_FOLDER']
        filename1 = secure_filename(file1.filename)
        filename2 = secure_filename(file2.filename)
        path1 = os.path.join(upload_dir, filename1)
        path2 = os.path.join(upload_dir, filename2)
        file1.save(path1)
        file2.save(path2)

        # Parse logs
        _, messages_by_type1 = parse_bin_file(path1)
        _, messages_by_type2 = parse_bin_file(path2)

 #       print("Sample MSG from log 1:", messages_by_type1.get('MSG', [])[0])
 #       print("Sample MSG from log 2:", messages_by_type2.get('MSG', [])[0])

        types1 = get_message_types(messages_by_type1.get('MSG', []))
        types2 = get_message_types(messages_by_type2.get('MSG', []))

        version1 = get_firmware_version(messages_by_type1)
        version2 = get_firmware_version(messages_by_type2)

        if types1 != types2:
            return render_template(
                'bin_parameter_compare.html',
                log1=filename1,
                log2=filename2,
                version1=version1,
                version2=version2,
                error="Message types differ—comparison skipped due to format mismatch."
            )

        # Proceed with parameter extraction and comparison
        params1 = extract_parameters(path1)
        params2 = extract_parameters(path2)
        
#        print("Params1 count:", len(params1))
#        print("Params2 count:", len(params2))
        
        
        diffs = compare_parameters(params1, params2)

        return render_template(
            'bin_parameter_compare.html',
            log1=filename1,
            log2=filename2,
            version1=version1,
            version2=version2,
            diffs=diffs
        )

    return render_template('bin_parameter_compare.html')
