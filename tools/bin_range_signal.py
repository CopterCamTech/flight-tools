#!/usr/bin/env python3

import math
import os
import base64
from io import BytesIO
from pathlib import Path
import matplotlib.pyplot as plt
from pymavlink import mavutil
import argparse

def compute_range(pn, pe, pd):
    return math.sqrt(pn**2 + pe**2 + pd**2)

def parse_bin_log(filepath):
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

def plot_scatter(range_rxrssi, range_rxlq, range_rad_rssi, filepath):
    fig, ax1 = plt.subplots(figsize=(12, 6))
    ax2 = ax1.twinx()
    ax3 = None

    ax1.set_ylabel('Control Radio Link Quality (RSSI.RXLQ)', color='green')
    ax2.set_ylabel('Control Radio RSSI (RSSI.RXRSSI)', color='blue')
    ax1.tick_params(axis='y', labelcolor='green')
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
        ax3.set_ylabel('Telemetry Radio RSSI (RAD.RSSI)', color='orange')
        ax3.tick_params(axis='y', labelcolor='orange')

        x, y = zip(*range_rad_rssi)
        ax3.scatter(x, y, color='orange', marker='D', s=50, alpha=0.7)

    ax1.set_xlabel('3D Distance from Home (meters)')
    ax1.grid(True)

    plt.title('ArduPilot Range vs Signal Strength', fontsize=14)

    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
    plt.close()

    return f'<img src="data:image/png;base64,{image_base64}"/>'

def validate_input_file(path_str):
    path = Path(path_str)
    if not path.exists():
        return None, f"❌ Error: File '{path}' does not exist."
    if path.suffix.lower() != ".bin":
        return None, f"❌ Error: Expected a .bin file, but got '{path.suffix}'"
    return path, None

def flask_entry(input_path):
    path, error = validate_input_file(input_path)
    if error:
        return {'error': error}

    rxrssi, rxlq, rad_rssi = parse_bin_log(str(path))

    if not (rxrssi or rxlq or rad_rssi):
        return {'error': 'No valid signal data found in log file.'}

    figure_html = plot_scatter(rxrssi, rxlq, rad_rssi, str(path))
    return {'figure': figure_html}

def main():
    parser = argparse.ArgumentParser(description="Plot signal strength vs. range from ArduPilot .bin logs")
    parser.add_argument("input_file", help="Path to ArduPilot .bin log file")
    parser.add_argument("--output", help="Path to save PNG plot (default: show in window)", default=None)
    parser.add_argument("--nogui", action="store_true", help="Suppress GUI display (useful for headless environments)")

    args = parser.parse_args()
    path, error = validate_input_file(args.input_file)
    if error:
        print(error)
        exit(1)

    rxrssi, rxlq, rad_rssi = parse_bin_log(str(path))

    if not (rxrssi or rxlq or rad_rssi):
        print("No valid signal data found.")
        exit(0)

    if args.output:
        import matplotlib
        matplotlib.use("Agg")
        plot_scatter(rxrssi, rxlq, rad_rssi, str(path))
        plt.savefig(args.output)
        print(f"✅ Plot saved to {args.output}")
    else:
        plot_scatter(rxrssi, rxlq, rad_rssi, str(path))
        if args.nogui:
            print("✅ Plot generated (GUI suppressed)")
        else:
            plt.show()

if __name__ == "__main__":
    main()
