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

import matplotlib.pyplot as plt
import numpy as np
from pyulog import ULog
from webapp.utils.plot_utils import render_plot_to_base64  # ✅ Flask image rendering

def build_power_plot(filepath):
    if not os.path.exists(filepath):
        return None, f"File not found: {filepath}"

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
        ax3.yaxis.label.set_color('green')
        ax3.tick_params(axis='y', labelcolor='green')

        plt.title('PX4 Power Metrics', fontsize=14)
        fig.tight_layout()

        return fig, None

    except Exception as e:
        return None, str(e)

def generate_power_plot(filepath, mode="cli", output_path=None):
    fig, error = build_power_plot(filepath)
    if error:
        return {'error': error}

    if mode == "cli":
        plt.figure(fig.number)
        plt.show()
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
    parser = argparse.ArgumentParser(description="Generate power chart from PX4 .ulg log")
    parser.add_argument("input_file", help="Path to .ulg log file")
    parser.add_argument("--mode", choices=["cli", "file", "flask"], default="cli")
    parser.add_argument("--output", help="Path to save PNG chart (used in file mode)", default=None)
    args = parser.parse_args()

    result = generate_power_plot(args.input_file, mode=args.mode, output_path=args.output)
    print(result.get('error') or f"✅ {result['output']}")
