#!/usr/bin/env python3

import matplotlib.pyplot as plt
import numpy as np
import io
import base64
import os
from pyulog import ULog

def generate_power_plot(filepath, output_path=None):
    try:
        if not os.path.exists(filepath):
            return {'error': f"File not found: {filepath}"}

        # === Extract battery data from .ulg ===
        ulog = ULog(filepath)
        battery_data = ulog.get_dataset('battery_status')

        voltage = np.array(battery_data.data['voltage_v'])  # volts
        current = np.array(battery_data.data['current_a'])  # amps
        timestamps = np.array(battery_data.data['timestamp'])  # microseconds

        # Normalize timestamps to seconds
        timestamps = (timestamps - timestamps[0]) / 1e6

        # === Compute watt-hours ===
        power = voltage * current
        dt_hours = np.diff(timestamps) / 3600.0
        watt_hours = np.cumsum(power[:-1] * dt_hours)

        # === Plot all metrics on one chart ===
        fig, ax1 = plt.subplots(figsize=(14, 6))

        ax1.set_xlabel('Time (s)')
        ax1.set_ylabel('Voltage (V)', color='blue')
        ax1.plot(timestamps, voltage, label='Voltage (V)', color='blue')
        ax1.tick_params(axis='y', labelcolor='blue')

        ax2 = ax1.twinx()
        ax2.set_ylabel('Current (A)', color='red')
        ax2.plot(timestamps, current, label='Current (A)', color='red')
        ax2.tick_params(axis='y', labelcolor='red')

        ax3 = ax1.twinx()
        ax3.spines['right'].set_position(('outward', 60))
        ax3.set_ylabel('Watt-hours (Wh)', color='green')
        ax3.plot(timestamps[1:], watt_hours, label='Watt-hours (Wh)', color='green')
        ax3.tick_params(axis='y', labelcolor='green')

        fig.suptitle("PX4 Power Metrics")
        fig.tight_layout()
        ax1.grid(True)

        if output_path:
            fig.savefig(output_path)
            plt.close()
            return {'output': output_path}
        else:
            plt.show()
            return {'output': 'Chart displayed interactively'}

    except Exception as e:
        return {'error': str(e)}

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Generate power chart from PX4 .ulg log")
    parser.add_argument("input_file", help="Path to .ulg log file")
    parser.add_argument("--output", help="Path to save PNG chart", default=None)
    args = parser.parse_args()

    result = generate_power_plot(args.input_file, args.output)

    if 'error' in result:
        print(f"❌ {result['error']}")
    else:
        print(f"✅ {result['output']}")
