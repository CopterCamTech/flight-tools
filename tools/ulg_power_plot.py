import matplotlib.pyplot as plt
import numpy as np
import io
import base64
from pyulog import ULog

def generate_power_plot(filepath):
    try:
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
        fig, ax1 = plt.subplots(figsize=(10, 6))

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

        # === Convert to base64 PNG ===
        buf = io.BytesIO()
        fig.savefig(buf, format='png')
        buf.seek(0)
        encoded = base64.b64encode(buf.read()).decode('utf-8')
        html_img = f'<img src="data:image/png;base64,{encoded}"/>'

        return {'figure': html_img}

    except Exception as e:
        return {'error': str(e)}

