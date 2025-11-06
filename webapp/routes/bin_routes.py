from flask import Blueprint, request, render_template, current_app
import os
from werkzeug.utils import secure_filename
from tools.bin_info import generate_bin_info
from tools.bin_parameter_list import generate_parameter_list
from tools.bin_range_signal import flask_entry as generate_range_chart
from tools.bin_power_plot import flask_entry as generate_power_plot

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

