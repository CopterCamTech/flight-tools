#!/usr/bin/env python3

import os
import sys
import argparse
import subprocess
import numpy as np
import matplotlib.pyplot as plt
from pyulog import ULog
from io import BytesIO
import base64

def build_power_plot(filepath):
    try:
        ulog = ULog(filepath)
        battery_data = ulog.get_dataset('battery_status')

        voltage = np.array(battery_data.data['voltage_v'])
        current = np.array(battery_data.data['current_a'])
        timestamps = np.array(battery_data.data['timestamp'])

        if len(timestamps) == 0:
            return None, "No battery telemetry found in log file."

        timestamps = (timestamps - timestamps[0]) / 1e6  # seconds
        power = voltage * current
        dt_hours = np.diff(timestamps) / 3600.0
        watt_hours = np.cumsum(power[:-1] * dt_hours)

        fig, ax1 = plt.subplots(figsize=(14, 6))

        ax1.plot(timestamps, voltage, color='blue', label='Voltage (V)')
        ax1.set_xlabel('Time (s)')
        ax1.set_ylabel('Voltage (V)', color='blue')
        ax1.tick_params(axis='y', labelcolor='blue')
        ax1.grid(True)

        ax2 = ax1.twinx()
        ax2.plot(timestamps, current, color='red', label='Current (A)')
        ax2.set_ylabel('Current (A)', color='red')
        ax2.tick_params(axis='y', labelcolor='red')

        ax3 = ax1.twinx()
        ax3.spines.right.set_position(("axes", 1.1))
        ax3.plot(timestamps[1:], watt_hours, color='green', label='Watt-Hours (Wh)')
        ax3.set_ylabel('Watt-Hours (Wh)', color='green', fontsize=12)
        ax3.tick_params(axis='y', labelcolor='green')

        plt.title('PX4 Power Metrics', fontsize=14)
        fig.tight_layout()

        return fig, None

    except Exception as e:
        return None, f"❌ Failed to parse .ulg file: {e}"

def flask_entry(input_path):
    import matplotlib
    matplotlib.use("Agg")  # ✅ Use non-GUI backend for Flask

    print("🧪 flask_entry() triggered")

    if not os.path.exists(input_path):
        return {'error': f"File not found: {input_path}"}

    fig, error = build_power_plot(input_path)
    if error:
        return {'error': error}

    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
    plt.close()  # ✅ Clean up figure after saving

    result = {'image_data': image_base64}
    print("[DEBUG] Chart image generated and encoded successfully.")
    return result

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
    path = os.path.abspath(path_str)
    if not os.path.exists(path):
        return None, f"❌ Error: File '{path}' does not exist."
    if not path.lower().endswith(".ulg"):
        return None, f"❌ Error: Expected a .ulg file, but got '{os.path.splitext(path)[1]}'"
    return path, None

if __name__ == "__main__":
    import matplotlib
    matplotlib.use("Agg")  # ✅ Use non-GUI backend for CLI mode

    parser = argparse.ArgumentParser(description="Generate power chart from PX4 .ulg log")
    parser.add_argument("input_file", help="Path to PX4 .ulg log file")
    parser.add_argument("--output", help="Path to save PNG chart")
    parser.add_argument("--nogui", action="store_true", help="Suppress GUI display")
    parser.add_argument("--view", action="store_true", help="Open chart after saving")
    args = parser.parse_args()

    path, error = validate_input_file(args.input_file)
    if error:
        print(error)
        exit(1)

    fig, error = build_power_plot(path)
    if error:
        print(error)
        exit(1)

    if args.output:
        output_path = os.path.abspath(args.output)
        if not output_path.lower().endswith(".png"):
            output_path += ".png"
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
