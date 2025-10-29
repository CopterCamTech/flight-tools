#!/usr/bin/env python3

import matplotlib.pyplot as plt
import base64
from io import BytesIO
from pymavlink import mavutil
import numpy as np
import os

def generate_power_plot(filepath, output_path=None):
    if not os.path.exists(filepath):
        return {'error': f"File not found: {filepath}"}

    reader = mavutil.mavlink_connection(filepath)
    timestamps = []
    current_data = []
    voltage_data = []

    # Stream BAT messages
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
        return {'error': 'No battery telemetry found in log file.'}

    # Compute Watt-Hours
    power = np.array(current_data) * np.array(voltage_data)  # Watts
    time_deltas = np.diff(timestamps, prepend=timestamps[0])  # Seconds
    watt_sec = np.cumsum(power * time_deltas)
    watt_hours = watt_sec / 3600

    # Plotting
    fig, ax1 = plt.subplots(figsize=(14, 6))  # Wider canvas

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
    fig.tight_layout()  # Prevent clipping

    if output_path:
        plt.savefig(output_path)
        plt.close()
        return {'output': output_path}
    else:
        plt.show()
        return {'output': 'Chart displayed interactively'}

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Generate power chart from ArduPilot .bin log")
    parser.add_argument("input_file", help="Path to .bin log file")
    parser.add_argument("--output", help="Path to save PNG chart", default=None)
    args = parser.parse_args()

    result = generate_power_plot(args.input_file, args.output)

    if 'error' in result:
        print(f"❌ {result['error']}")
    else:
        print(f"✅ {result['output']}")
