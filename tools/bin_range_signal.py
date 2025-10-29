#!/usr/bin/env python3

import os
import math
import argparse
import base64
from io import BytesIO
import matplotlib.pyplot as plt
from pymavlink import mavutil

def compute_range(pn, pe, pd):
    return math.sqrt(pn**2 + pe**2 + pd**2)

def extract_signal_data(filepath):
    mlog = mavutil.mavlink_connection(filepath)
    range_rxrssi = []
    range_rxlq = []
    range_rad_rssi = []

    latest_rssi = {}
    latest_rad = {}

    while True:
        msg = mlog.recv_match(type=['XKF1', 'RSSI', 'RAD'], blocking=False)
        if msg is None:
            break

        msg_type = msg.get_type()

        if msg_type == 'RSSI':
            data = msg.to_dict()
            latest_rssi['RXRSSI'] = data.get('RXRSSI')
            latest_rssi['RXLQ'] = data.get('RXLQ')

        elif msg_type == 'RAD':
            data = msg.to_dict()
            latest_rad['RSSI'] = data.get('RSSI')

        elif msg_type == 'XKF1':
            pn = getattr(msg, 'PN', None)
            pe = getattr(msg, 'PE', None)
            pd = getattr(msg, 'PD', None)

            if None in (pn, pe, pd):
                continue

            range_val = compute_range(pn, pe, pd)

            if 'RXRSSI' in latest_rssi and latest_rssi['RXRSSI'] is not None:
                range_rxrssi.append((range_val, latest_rssi['RXRSSI']))

            if 'RXLQ' in latest_rssi and latest_rssi['RXLQ'] is not None:
                range_rxlq.append((range_val, latest_rssi['RXLQ']))

            if 'RSSI' in latest_rad and latest_rad['RSSI'] is not None:
                range_rad_rssi.append((range_val, latest_rad['RSSI']))

            latest_rssi.clear()
            latest_rad.clear()

    return range_rxrssi, range_rxlq, range_rad_rssi

def plot_range_signal(range_rxrssi, range_rxlq, range_rad_rssi, output_path=None, suppress_gui=False):
    fig, ax1 = plt.subplots(figsize=(14, 6))
    ax2 = ax1.twinx()
    ax3 = None

    ax1.set_ylabel('Control Radio Link Quality (RXLQ)', color='green')
    ax1.tick_params(axis='y', labelcolor='green')

    ax2.set_ylabel('Control Radio RSSI (RXRSSI)', color='blue')
    ax2.tick_params(axis='y', labelcolor='blue')

    if range_rxrssi:
        x, y = zip(*range_rxrssi)
        ax2.scatter(x, y, color='blue', marker='^', s=40, alpha=0.7)

    if range_rxlq:
        x, y = zip(*range_rxlq)
        ax1.scatter(x, y, color='green', marker='v', s=60, alpha=0.7)

    if range_rad_rssi:
        ax3 = ax1.twinx()
        ax3.spines.right.set_position(("axes", 1.12))
        ax3.plot([], [], color='orange')  # Dummy plot to anchor label
        ax3.set_ylabel('Telemetry Radio RSSI (RAD.RSSI)', color='orange', fontsize=12)
        ax3.yaxis.label.set_color('orange')
        ax3.tick_params(axis='y', labelcolor='orange')

        x, y = zip(*range_rad_rssi)
        ax3.scatter(x, y, color='orange', marker='D', s=50, alpha=0.7)

    ax1.set_xlabel('3D Distance from Home (meters)')
    ax1.grid(True)
    plt.title('ArduPilot Range vs Signal Strength', fontsize=14)
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
    if not os.path.exists(path_str):
        return None, f"❌ Error: File '{path_str}' does not exist."
    if not path_str.lower().endswith(".bin"):
        return None, f"❌ Error: Expected a .bin file, but got '{os.path.splitext(path_str)[1]}'"
    return path_str, None

def flask_entry(input_path):
    path, error = validate_input_file(input_path)
    if error:
        return {'error': error}

    rxrssi, rxlq, rad_rssi = extract_signal_data(path)

    if not (rxrssi or rxlq or rad_rssi):
        return {'error': 'No valid signal data found in log file.'}

    fig, ax1 = plt.subplots(figsize=(14, 6))
    ax2 = ax1.twinx()
    ax3 = None

    ax1.set_ylabel('Control Radio Link Quality (RXLQ)', color='green')
    ax1.tick_params(axis='y', labelcolor='green')

    ax2.set_ylabel('Control Radio RSSI (RXRSSI)', color='blue')
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
        ax3.plot([], [], color='orange')
        ax3.set_ylabel('Telemetry Radio RSSI (RAD.RSSI)', color='orange', fontsize=12)
        ax3.yaxis.label.set_color('orange')
        ax3.tick_params(axis='y', labelcolor='orange')

        x, y = zip(*rad_rssi)
        ax3.scatter(x, y, color='orange', marker='D', s=50, alpha=0.7)

    ax1.set_xlabel('3D Distance from Home (meters)')
    ax1.grid(True)
    plt.title('ArduPilot Range vs Signal Strength', fontsize=14)
    fig.tight_layout()

    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
    plt.close()

    return {'figure': f'<img src="data:image/png;base64,{image_base64}"/>'}

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Plot signal strength vs range from ArduPilot .bin log")
    parser.add_argument("input_file", help="Path to .bin log file")
    parser.add_argument("--output", help="Path to save PNG chart", default=None)
    parser.add_argument("--nogui", action="store_true", help="Suppress GUI display")

    args = parser.parse_args()
    path, error = validate_input_file(args.input_file)
    if error:
        print(error)
        exit(1)

    rxrssi, rxlq, rad_rssi = extract_signal_data(path)

    if not (rxrssi or rxlq or rad_rssi):
        print("❌ No valid signal data found in log.")
        exit(0)

    if args.output:
        import matplotlib
        matplotlib.use("Agg")
        plot_range_signal(rxrssi, rxlq, rad_rssi, args.output, suppress_gui=True)
    else:
        plot_range_signal(rxrssi, rxlq, rad_rssi, None, suppress_gui=args.nogui)
