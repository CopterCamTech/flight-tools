#!/usr/bin/env python3

# ✅ Enables CLI execution from tools/ by patching sys.path
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# ✅ Use interactive backend for CLI, headless for Flask
import matplotlib
if __name__ == "__main__":
    matplotlib.use('TkAgg')  # GUI backend for CLI
else:
    matplotlib.use('Agg')    # Headless backend for Flask

import matplotlib.pyplot as plt  # ✅ Now available in all modes
import numpy as np
from pymavlink import mavutil
from webapp.utils.plot_utils import render_plot_to_base64

def build_power_plot(filepath):
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
        return None, 'No battery telemetry found in log file.'

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

    return fig, None

def generate_power_plot(filepath, mode="cli", output_path=None):
    if not os.path.exists(filepath):
        return {'error': f"File not found: {filepath}"}

    fig, error = build_power_plot(filepath)
    if error:
        return {'error': error}

    if mode == "cli":
        plt.figure(fig.number)  # 👈 Precise figure selection
        plt.show()              # 👈 Blocks until chart is closed
        return {'output': 'Chart displayed interactively'}

    elif mode == "file":
        if not output_path:
            output_path = filepath + "_power.png"
        fig.savefig(output_path)
        plt.close(fig)
        return {'output': output_path}

    elif mode == "flask":
        image_data = render_plot_to_base64(fig)
        plt.close(fig)
        return {
            'image_data': image_data,
            'summary': 'Chart rendered in memory'
        }

    else:
        plt.close(fig)
        return {'error': f"Unknown mode: {mode}"}

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Generate power chart from ArduPilot .bin log")
    parser.add_argument("input_file", help="Path to .bin log file")
    parser.add_argument("--mode", choices=["cli", "file", "flask"], default="cli")
    parser.add_argument("--output", help="Path to save PNG chart (used in file mode)", default=None)
    args = parser.parse_args()

    result = generate_power_plot(args.input_file, mode=args.mode, output_path=args.output)
    print(result.get('error') or f"✅ {result['output']}")
