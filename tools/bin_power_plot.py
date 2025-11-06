#!/usr/bin/env python3

import os
import sys
import argparse
import base64
import subprocess
from io import BytesIO
import matplotlib.pyplot as plt
import numpy as np
from pymavlink import mavutil

def extract_power_data(filepath):
    reader = mavutil.mavlink_connection(filepath)
    timestamps = []
    current_data = []
    voltage_data = []

    while True:
        msg = reader.recv_match(type='BAT', blocking=False)
        if msg is None:
            break

        curr = getattr(msg, 'Curr', None)
        volt = getattr(msg, 'Volt', None)
        time = getattr(msg, 'TimeUS', None)

        if curr is not None and volt is not None and time is not None:
            t_sec = time / 1e6
            timestamps.append(t_sec)
            current_data.append(curr)
            voltage_data.append(volt)

    if not timestamps:
        return None, None, None, 'No battery telemetry found in log file.'

    return timestamps, current_data, voltage_data, None

def generate_power_chart(timestamps, current_data, voltage_data):
    power = np.array(current_data) * np.array(voltage_data)
    time_deltas = np.diff(timestamps, prepend=timestamps[0])
    watt_sec = np.cumsum(power * time_deltas)
    watt_hours = watt_sec / 3600

    fig, ax1 = plt.subplots(figsize=(14, 6))

    ax1.plot(timestamps, voltage_data, color='blue', label='Voltage (V)')
    ax1.set_xlabel('Time (s)')
    ax1.set_ylabel('Voltage (V)', color='blue')
    ax1.tick_params(axis='y', labelcolor='blue')
    ax1.grid(True)

    ax2 = ax1.twinx()
    ax2.plot(timestamps, current_data, color='red', label='Current (A)')
    ax2.set_ylabel('Current (A)', color='red')
    ax2.tick_params(axis='y', labelcolor='red')

    ax3 = ax1.twinx()
    ax3.spines.right.set_position(("axes", 1.1))
    ax3.plot(timestamps, watt_hours, color='green', label='Watt-Hours (Wh)')
    ax3.set_ylabel('Watt-Hours (Wh)', color='green', fontsize=12)
    ax3.yaxis.label.set_color('green')
    ax3.tick_params(axis='y', labelcolor='green')

    plt.title('ArduPilot Power Metrics', fontsize=14)
    fig.tight_layout()
    return fig

def open_image(path):
    try:
        abs_path = os.path.abspath(path)
        if sys.platform.startswith("darwin"):
            subprocess.run(["open", abs_path])
        elif os.name == "nt":
            os.startfile(abs_path)
        elif os.name == "posix":
            subprocess.run(["xdg-open", abs_path])
        print(f"[INFO] Opened image: {abs_path}")
    except Exception as e:
        print(f"[WARNING] Could not open image: {e}")

def get_temp_chart_path(logfile_path, script_name):
    log_stem = os.path.splitext(os.path.basename(logfile_path))[0]
    script_stem = os.path.splitext(os.path.basename(script_name))[0]
    filename = f"{log_stem}-{script_stem}.png"
    return os.path.abspath(os.path.join("webapp", "uploads", filename))

def validate_input_file(path_str):
    if not os.path.exists(path_str):
        return None, f"❌ Error: File '{path_str}' does not exist."
    if not path_str.lower().endswith(".bin"):
        return None, f"❌ Error: Expected a .bin file, but got '{os.path.splitext(path_str)[1]}'"
    return path_str, None

def flask_entry(input_path):
    import matplotlib
    matplotlib.use("Agg")  # ✅ Use non-GUI backend for Flask

    path, error = validate_input_file(input_path)
    if error:
        return {'error': error}

    timestamps, current_data, voltage_data, parse_error = extract_power_data(path)
    if parse_error:
        return {'error': parse_error}
    if not (timestamps and current_data and voltage_data):
        return {'error': 'No valid power data found in log file.'}

    fig = generate_power_chart(timestamps, current_data, voltage_data)
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
    plt.close()  # ✅ Clean up figure after saving
    print("[DEBUG] Power chart image generated and encoded successfully.")
    return {'image_data': image_base64}

if __name__ == "__main__":
    import matplotlib
    matplotlib.use("Agg")  # ✅ Use non-GUI backend for CLI mode

    parser = argparse.ArgumentParser(description="Plot power metrics from ArduPilot .bin log")
    parser.add_argument("input_file", help="Path to .bin log file")
    parser.add_argument("--output", help="Path to save PNG chart")
    parser.add_argument("--nogui", action="store_true", help="Suppress GUI display")
    parser.add_argument("--view", action="store_true", help="Open chart after saving")
    args = parser.parse_args()

    path, error = validate_input_file(args.input_file)
    if error:
        print(error)
        exit(1)

    timestamps, current_data, voltage_data, parse_error = extract_power_data(path)
    if parse_error:
        print(parse_error)
        exit(1)
    if not (timestamps and current_data and voltage_data):
        print("❌ No valid power data found in log.")
        exit(0)

    fig = generate_power_chart(timestamps, current_data, voltage_data)

    if args.output:
        output_path = args.output
        if not output_path.lower().endswith(".png"):
            output_path += ".png"
        output_path = os.path.abspath(output_path)
    elif args.nogui:
        print("❌ Headless mode requires --output to save chart.")
        exit(1)
    else:
        output_path = get_temp_chart_path(args.input_file, __file__)

    fig.savefig(output_path)
    print(f"✅ Chart saved to: {output_path}")
    plt.close()  # ✅ Clean up figure after saving

    if not args.nogui and (not args.output or args.view):
        open_image(output_path)
