#!/usr/bin/env python3

import math
import os
import argparse
import base64
from io import BytesIO
from pathlib import Path
import matplotlib.pyplot as plt
from pyulog import ULog

def compute_range(x, y, z):
    return math.sqrt(x**2 + y**2 + z**2)

def parse_ulg_log(filepath):
    try:
        ulog = ULog(filepath)
    except Exception as e:
        return None, f"❌ Failed to parse .ulg file: {e}"

    def extract(msg_name, field):
        msg = next((m for m in ulog.data_list if m.name == msg_name), None)
        return msg.data[field] if msg and field in msg.data else []

    x_vals = extract("vehicle_local_position_setpoint", "x")
    y_vals = extract("vehicle_local_position_setpoint", "y")
    z_vals = extract("vehicle_local_position_setpoint", "z")
    ctrl_rssi = extract("input_rc", "rssi")
    ctrl_lq = extract("input_rc", "link_quality")
    telem_rssi = extract("radio_status", "rssi")

    min_len = min(len(x_vals), len(y_vals), len(z_vals))
    ranges = [compute_range(x_vals[i], y_vals[i], z_vals[i]) for i in range(min_len)]

    range_ctrl_rssi = [(r, v) for r, v in zip(ranges, ctrl_rssi) if v not in [-1, None]]
    range_ctrl_lq = [(r, v) for r, v in zip(ranges, ctrl_lq) if v not in [-1, None]]
    range_telem_rssi = [(r, v) for r, v in zip(ranges, telem_rssi) if v not in [-1, 0, None]]

    return range_ctrl_rssi, range_ctrl_lq, range_telem_rssi, None

def plot_scatter(ctrl_rssi, ctrl_lq, telem_rssi, output_path=None, suppress_gui=False):
    fig, ax1 = plt.subplots(figsize=(14, 6))
    ax2 = ax1.twinx()
    ax3 = None

    ax1.set_ylabel('Control Radio Link Quality (input_rc.link_quality)', color='green')
    ax1.tick_params(axis='y', labelcolor='green')

    ax2.set_ylabel('Control Radio RSSI (input_rc.rssi)', color='blue')
    ax2.tick_params(axis='y', labelcolor='blue')

    if ctrl_rssi:
        x, y = zip(*ctrl_rssi)
        ax2.scatter(x, y, color='blue', marker='^', s=40, alpha=0.7)

    if ctrl_lq:
        x, y = zip(*ctrl_lq)
        ax1.scatter(x, y, color='green', marker='v', s=60, alpha=0.7)

    if telem_rssi:
        ax3 = ax1.twinx()
        ax3.spines.right.set_position(("axes", 1.12))
        ax3.plot([], [], color='orange')
        ax3.set_ylabel('Telemetry Radio RSSI (radio_status.rssi)', color='orange', fontsize=12)
        ax3.yaxis.label.set_color('orange')
        ax3.tick_params(axis='y', labelcolor='orange')

        x, y = zip(*telem_rssi)
        ax3.scatter(x, y, color='orange', marker='D', s=50, alpha=0.7)

    ax1.set_xlabel('3D Distance from Home (meters)')
    ax1.grid(True)
    plt.title('PX4 Range vs Signal Strength', fontsize=14)
    fig.tight_layout()

    if output_path:
        plt.savefig(output_path)
        plt.close()
        print(f"✅ Plot saved to {output_path}")
    elif suppress_gui:
        plt.close()
        print("✅ Plot generated (GUI suppressed)")
    else:
        plt.show()

def validate_input_file(path_str):
    path = Path(path_str)
    if not path.exists():
        return None, f"❌ Error: File '{path}' does not exist."
    if path.suffix.lower() != ".ulg":
        return None, f"❌ Error: Expected a .ulg file, but got '{path.suffix}'"
    return path, None

def flask_entry(input_path):
    path, error = validate_input_file(input_path)
    if error:
        return {'error': error}

    ctrl_rssi, ctrl_lq, telem_rssi, parse_error = parse_ulg_log(str(path))
    if parse_error:
        return {'error': parse_error}

    if not (ctrl_rssi or ctrl_lq or telem_rssi):
        return {'error': 'No valid signal data found in log file.'}

    fig, ax1 = plt.subplots(figsize=(14, 6))
    ax2 = ax1.twinx()
    ax3 = None

    ax1.set_ylabel('Control Radio Link Quality (input_rc.link_quality)', color='green')
    ax1.tick_params(axis='y', labelcolor='green')

    ax2.set_ylabel('Control Radio RSSI (input_rc.rssi)', color='blue')
    ax2.tick_params(axis='y', labelcolor='blue')

    if ctrl_rssi:
        x, y = zip(*ctrl_rssi)
        ax2.scatter(x, y, color='blue', marker='^', s=40, alpha=0.7)

    if ctrl_lq:
        x, y = zip(*ctrl_lq)
        ax1.scatter(x, y, color='green', marker='v', s=60, alpha=0.7)

    if telem_rssi:
        ax3 = ax1.twinx()
        ax3.spines.right.set_position(("axes", 1.12))
        ax3.plot([], [], color='orange')
        ax3.set_ylabel('Telemetry Radio RSSI (radio_status.rssi)', color='orange', fontsize=12)
        ax3.yaxis.label.set_color('orange')
        ax3.tick_params(axis='y', labelcolor='orange')

        x, y = zip(*telem_rssi)
        ax3.scatter(x, y, color='orange', marker='D', s=50, alpha=0.7)

    ax1.set_xlabel('3D Distance from Home (meters)')
    ax1.grid(True)
    plt.title('PX4 Range vs Signal Strength', fontsize=14)
    fig.tight_layout()

    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
    plt.close()

    return {'image_data': f'<img src="data:image/png;base64,{image_base64}"/>'}

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Plot signal strength vs. range from PX4 .ulg logs")
    parser.add_argument("input_file", help="Path to PX4 .ulg log file")
    parser.add_argument("--output", help="Path to save PNG plot", default=None)
    parser.add_argument("--nogui", action="store_true", help="Suppress GUI display (useful for headless environments)")

    args = parser.parse_args()
    path, error = validate_input_file(args.input_file)
    if error:
        print(error)
        exit(1)

    ctrl_rssi, ctrl_lq, telem_rssi, parse_error = parse_ulg_log(str(path))
    if parse_error:
        print(parse_error)
        exit(1)

    if not (ctrl_rssi or ctrl_lq or telem_rssi):
        print("❌ No valid signal data found in log.")
        exit(0)

    if args.output:
        import matplotlib
        matplotlib.use("Agg")
        plot_scatter(ctrl_rssi, ctrl_lq, telem_rssi, args.output, suppress_gui=True)
    else:
        plot_scatter(ctrl_rssi, ctrl_lq, telem_rssi, None, suppress_gui=args.nogui)
