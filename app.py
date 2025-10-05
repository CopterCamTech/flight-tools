import os
from flask import Flask, request, render_template
from tools.plot_utils import cleanup_uploads  # ✅ Import cleanup utility

# PX4 (.ulg) modules
from tools.ulg_power_plot import generate_power_plot as generate_ulg_power_plot
from tools.ulg_info import extract_ulg_info as generate_ulg_info
from tools.ulg_parameter_list import extract_parameters as generate_ulg_parameters

# ArduPilot (.bin) modules
from tools.bin_power_plot import generate_power_plot as generate_bin_power_plot
from tools.bin_info import extract_bin_info as generate_bin_info
from tools.bin_parameter_list import extract_parameters as generate_bin_parameters

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def upload_form(route, label, extension):
    return f'''
        <h1>Upload {label}</h1>
        <form action="/{route}" method="post" enctype="multipart/form-data">
            <input type="file" name="file" accept="{extension}">
            <input type="submit" value="Upload">
        </form>
    '''

@app.route('/')
def index():
    return '''
        <h1>Flight Log Diagnostics</h1>
        <ul>
            <li><a href="/bin-power">ArduPilot Power Plot</a></li>
            <li><a href="/bin-info">ArduPilot Log Info</a></li>
            <li><a href="/bin-parameters">ArduPilot Parameters</a></li>
            <li><a href="/ulg-power">PX4 Power Plot</a></li>
            <li><a href="/ulg-info">PX4 Log Info</a></li>
            <li><a href="/ulg-parameters">PX4 Parameters</a></li>
        </ul>
    '''

@app.route('/bin-power', methods=['GET', 'POST'])
def bin_power():
    if request.method == 'POST':
        cleanup_uploads(app.config['UPLOAD_FOLDER'])  # ✅ Clean old uploads
        file = request.files['file']
        if file:
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filepath)
            result = generate_bin_power_plot(filepath)
            filename = os.path.basename(filepath)
            return render_template("bin_power.html", result=result, filename=filename)

    return upload_form("bin-power", "ArduPilot .bin file (Power Plot)", ".bin")

@app.route('/bin-info', methods=['GET', 'POST'])
def bin_info():
    if request.method == 'POST':
        cleanup_uploads(app.config['UPLOAD_FOLDER'])  # ✅ Clean old uploads
        file = request.files['file']
        if file:
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filepath)
            result = generate_bin_info(filepath)
            return render_template("bin_info.html", result=result)
    return upload_form("bin-info", "ArduPilot .bin file (Log Info)", ".bin")

@app.route('/bin-parameters', methods=['GET', 'POST'])
def bin_parameters():
    if request.method == 'POST':
        cleanup_uploads(app.config['UPLOAD_FOLDER'])  # ✅ Clean old uploads
        file = request.files['file']
        if file:
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filepath)
            result = generate_bin_parameters(filepath)
            filename = os.path.basename(filepath)
            return render_template("bin_parameters.html", result=result, filename=filename)

    return upload_form("bin-parameters", "ArduPilot .bin file (Parameters)", ".bin")

@app.route('/ulg-power', methods=['GET', 'POST'])
def ulg_power():
    if request.method == 'POST':
        cleanup_uploads(app.config['UPLOAD_FOLDER'])  # ✅ Clean old uploads
        file = request.files['file']
        if file:
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filepath)
            result = generate_ulg_power_plot(filepath)
            filename = os.path.basename(filepath)
            return render_template("ulg_power.html", result=result, filename=filename)

    return upload_form("ulg-power", "PX4 .ulg file (Power Plot)", ".ulg")

@app.route('/ulg-info', methods=['GET', 'POST'])
def ulg_info():
    if request.method == 'POST':
        cleanup_uploads(app.config['UPLOAD_FOLDER'])  # ✅ Clean old uploads
        file = request.files['file']
        if file:
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filepath)
            result = generate_ulg_info(filepath)
            return render_template("ulg_info.html", result=result)
    return upload_form("ulg-info", "PX4 .ulg file (Log Info)", ".ulg")

@app.route('/ulg-parameters', methods=['GET', 'POST'])
def ulg_parameters():
    if request.method == 'POST':
        cleanup_uploads(app.config['UPLOAD_FOLDER'])  # ✅ Clean old uploads
        file = request.files['file']
        if file:
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filepath)
            result = generate_ulg_parameters(filepath)
            filename = os.path.basename(filepath)
            return render_template("ulg_parameters.html", result=result, filename=filename)

    return upload_form("ulg-parameters", "PX4 .ulg file (Parameters)", ".ulg")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

