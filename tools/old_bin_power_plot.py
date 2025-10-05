import matplotlib.pyplot as plt
import base64
from io import BytesIO
from pymavlink import mavutil
import numpy as np

def generate_power_plot(filepath):
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

    # Plotting with split legends
    fig, ax1 = plt.subplots(figsize=(12, 6))

    # Left axis: Current and Voltage
    ax1.plot(timestamps, current_data, label='Current (A)', color='blue')
    ax1.plot(timestamps, voltage_data, label='Voltage (V)', color='green')
    ax1.set_xlabel('Time (s)')
    ax1.set_ylabel('Current / Voltage')
    ax1.grid(True)
    ax1.legend(loc='upper left')

    # Right axis: Watt-Hours
    ax2 = ax1.twinx()
    ax2.plot(timestamps, watt_hours, label='Watt-Hours (Wh)', color='red')
    ax2.set_ylabel('Watt-Hours')
    ax2.legend(loc='upper right')

    # Title
    plt.title('ArduPilot Power Metrics Over Time')

    # Encode plot
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
    plt.close()

    return {'plot': image_base64}

