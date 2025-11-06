#!/usr/bin/env python3

import os
import sys
import math
import argparse
import base64
import subprocess
from io import BytesIO
import matplotlib.pyplot as plt
from pymavlink import mavutil

def compute_range(pn, pe, pd):
    return math.sqrt(pn**2 + pe**2 + pd**2)

def extract_signal_data(filepath):
    mlog = mavutil.mavlink_connection(filepath)
    range_rxrssi, range_rxlq, range_rad_rssi = [], [], []
    latest_rssi, latest_rad = {}, {}

    while True:
        msg = mlog.recv_match(type=['XKF1', 'RSSI', 'RAD'], blocking=False)
        if msg is None:
            break

        msg_type = msg.get_type()
        data = msg.to_dict()

        if msg_type == 'RSSI':
            latest_rssi['RXRSSI'] = data.get('RXRSSI')
            latest_rssi['RXLQ'] = data.get('RXLQ')
        elif msg_type == 'RAD':
            latest_rad['RSSI'] = data.get('RSSI')
        elif msg_type == 'XKF1':
            pn, pe, pd = getattr(msg, 'PN', None), getattr(msg, 'PE', None), getattr(msg, 'PD', None)
            if None in (pn, pe, pd): continue
            range_val = compute_range(pn, pe, pd)

            if latest_rssi.get('RXRSSI') is not None:
                range_rxrssi.append((range_val, latest_rssi['RXRSSI']))
            if latest_rssi.get('RXLQ') is not None:
                range_rxlq.append((range_val, latest_rssi['RXLQ']))
            if latest_rad.get('RSSI') is not None:
                range_rad_rssi.append((range_val, latest_rad['RSSI']))

            latest_rssi.clear()
            latest_rad.clear()

    return range_rxrssi, range_rxlq, range_rad_rssi

def generate_range_signal_chart(rxrssi, rxlq, rad_rssi):
    fig, ax1 = plt.subplots(figsize=(14, 6))
    ax2 = ax1.twinx()
    ax3 = None

    ax1.set_ylabel('Control Radio Link Quality (RXLQ)', color='green')
    ax2.set_ylabel('Control Radio RSSI (RXRSSI)', color='blue')
    ax1.tick_params(axis='y', labelcolor='green')
    ax2.tick_params(axis='y', labelcolor='blue')

    if rxrssi:
        x, y = zip(*rxrssi)
        ax2.scatter(x, y, color='blue', marker='^', s=40, alpha=0.7)
    if rxlq:
        x, y = zip(*rxlq)
        ax1.scatter(x, y, color='green', marker='v', s=60, alpha=0.7)
    if rad_rssi:
        ax3 = ax1.twinx()
        ax3.spines.right.set_position(("axes", 1.12))
        ax3.set_ylabel('Telemetry Radio RSSI (RAD.RSSI)', color='orange', fontsize=12)
        ax3.tick_params(axis='y', labelcolor='orange')
        x, y = zip(*rad_rssi)
        ax3.scatter(x, y, color='orange', marker='D', s=50, alpha=0.7)

    ax1.set_xlabel('3D Distance from Home (meters)')
    ax1.grid(True)
    plt.title('ArduPilot Range vs Signal Strength', fontsize=14)
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

    rxrssi, rxlq, rad_rssi = extract_signal_data(path)
    if not (rxrssi or rxlq or rad_rssi):
        return {'error': 'No valid signal data found in log file.'}

    fig = generate_range_signal_chart(rxrssi, rxlq, rad_rssi)
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
    plt.close()  # ✅ Clean up figure after saving
    return {'figure': f'<img src="data:image/png;base64,{image_base64}"/>'}

if __name__ == "__main__":
    import matplotlib
    matplotlib.use("Agg")  # ✅ Use non-GUI backend for CLI mode

    parser = argparse.ArgumentParser(description="Plot signal strength vs range from ArduPilot .bin log")
    parser.add_argument("input_file", help="Path to .bin log file")
    parser.add_argument("--output", help="Path to save PNG chart")
    parser.add_argument("--nogui", action="store_true", help="Suppress GUI display")
    parser.add_argument("--view", action="store_true", help="Open chart after saving")
    args = parser.parse_args()

    path, error = validate_input_file(args.input_file)
    if error:
        print(error)
        exit(1)

    rxrssi, rxlq, rad_rssi = extract_signal_data(path)
    if not (rxrssi or rxlq or rad_rssi):
        print("❌ No valid signal data found in log.")
        exit(0)

    fig = generate_range_signal_chart(rxrssi, rxlq, rad_rssi)

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
