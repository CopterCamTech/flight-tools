#!/usr/bin/env python3

import os
import sys
from io import BytesIO
import base64
import matplotlib
matplotlib.use("Agg")  # ✅ Non-GUI backend
import matplotlib.pyplot as plt
import numpy as np
import flet as ft
from pymavlink import mavutil

# --- Core logic ---
def extract_power_data(filepath):
    reader = mavutil.mavlink_connection(filepath)
    timestamps, current_data, voltage_data = [], [], []

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
        return None, None, None, "No battery telemetry found in log file."

    return timestamps, current_data, voltage_data, None

def generate_power_chart(timestamps, current_data, voltage_data):
    power = np.array(current_data) * np.array(voltage_data)
    time_deltas = np.diff(timestamps, prepend=timestamps[0])
    watt_sec = np.cumsum(power * time_deltas)
    watt_hours = watt_sec / 3600

    # 🔎 Enlarged figure size (25% bigger)
    fig, ax1 = plt.subplots(figsize=(15, 7.5))

    ax1.plot(timestamps, voltage_data, color="blue", label="Voltage (V)")
    ax1.set_xlabel("Time (s)")
    ax1.set_ylabel("Voltage (V)", color="blue")
    ax1.tick_params(axis="y", labelcolor="blue")
    ax1.grid(True)

    ax2 = ax1.twinx()
    ax2.plot(timestamps, current_data, color="red", label="Current (A)")
    ax2.set_ylabel("Current (A)", color="red")
    ax2.tick_params(axis="y", labelcolor="red")

    ax3 = ax1.twinx()
    ax3.spines.right.set_position(("axes", 1.1))
    ax3.plot(timestamps, watt_hours, color="green", label="Watt-Hours (Wh)")
    ax3.set_ylabel("Watt-Hours (Wh)", color="green")
    ax3.tick_params(axis="y", labelcolor="green")

    plt.title("ArduPilot Power Metrics", fontsize=14)
    fig.tight_layout()
    return fig

def chart_to_base64(fig):
    buffer = BytesIO()
    fig.savefig(buffer, format="png")
    buffer.seek(0)
    img_b64 = base64.b64encode(buffer.read()).decode("utf-8")
    plt.close(fig)
    return img_b64

# --- Flet UI wrapper ---
def main(page: ft.Page):
    page.title = "ArduPilot Power Plot"
    page.scroll = "auto"

    output_text = ft.Text(value="", selectable=True, visible=False)
    progress_ring = ft.ProgressRing(visible=False)
    # 🔎 Responsive chart: expands with window size
    chart_image = ft.Image(src="", visible=False, expand=True)

    def pick_file_result(e: ft.FilePickerResultEvent):
        if e.files:
            progress_ring.visible = True
            output_text.visible = False
            chart_image.visible = False
            page.update()

            filepath = e.files[0].path
            timestamps, current_data, voltage_data, parse_error = extract_power_data(filepath)

            progress_ring.visible = False

            if parse_error:
                output_text.value = f"Error: {parse_error}"
                output_text.visible = True
                chart_image.visible = False
            else:
                fig = generate_power_chart(timestamps, current_data, voltage_data)
                img_b64 = chart_to_base64(fig)
                chart_image.src_base64 = img_b64
                chart_image.visible = True
                output_text.visible = False

            page.update()

    file_picker = ft.FilePicker(on_result=pick_file_result)
    page.overlay.append(file_picker)

    pick_button = ft.ElevatedButton(
        "Select .bin Log File",
        on_click=lambda _: file_picker.pick_files(
            allowed_extensions=["bin"], allow_multiple=False
        )
    )

    page.add(
        ft.Column([
            ft.Text("ArduPilot Power Plot", size=20, weight="bold"),
            pick_button,
            progress_ring,
            output_text,
            chart_image
        ], expand=True)
    )

if __name__ == "__main__":
    ft.app(target=main)
