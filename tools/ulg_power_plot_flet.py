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
from pyulog import ULog

# --- Core logic ---
def build_power_plot(filepath):
    try:
        ulog = ULog(filepath)
        battery_data = ulog.get_dataset("battery_status")

        voltage = np.array(battery_data.data["voltage_v"])
        current = np.array(battery_data.data["current_a"])
        timestamps = np.array(battery_data.data["timestamp"])

        if len(timestamps) == 0:
            return None, "No battery telemetry found in log file."

        timestamps = (timestamps - timestamps[0]) / 1e6  # seconds
        power = voltage * current
        dt_hours = np.diff(timestamps) / 3600.0
        watt_hours = np.cumsum(power[:-1] * dt_hours)

        # 🔎 Enlarged figure size (25% bigger)
        fig, ax1 = plt.subplots(figsize=(17.5, 7.5))

        ax1.plot(timestamps, voltage, color="blue", label="Voltage (V)")
        ax1.set_xlabel("Time (s)")
        ax1.set_ylabel("Voltage (V)", color="blue")
        ax1.tick_params(axis="y", labelcolor="blue")
        ax1.grid(True)

        ax2 = ax1.twinx()
        ax2.plot(timestamps, current, color="red", label="Current (A)")
        ax2.set_ylabel("Current (A)", color="red")
        ax2.tick_params(axis="y", labelcolor="red")

        ax3 = ax1.twinx()
        ax3.spines.right.set_position(("axes", 1.1))
        ax3.plot(timestamps[1:], watt_hours, color="green", label="Watt-Hours (Wh)")
        ax3.set_ylabel("Watt-Hours (Wh)", color="green", fontsize=12)
        ax3.tick_params(axis="y", labelcolor="green")

        plt.title("PX4 Power Metrics", fontsize=14)
        fig.tight_layout()

        return fig, None

    except Exception as e:
        return None, f"❌ Failed to parse .ulg file: {e}"

def chart_to_base64(fig):
    buffer = BytesIO()
    fig.savefig(buffer, format="png")
    buffer.seek(0)
    img_b64 = base64.b64encode(buffer.read()).decode("utf-8")
    plt.close(fig)
    return img_b64

# --- Flet UI wrapper ---
def main(page: ft.Page):
    page.title = "PX4 Power Plot"
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
            fig, error = build_power_plot(filepath)

            progress_ring.visible = False

            if error:
                output_text.value = f"Error: {error}"
                output_text.visible = True
                chart_image.visible = False
            else:
                img_b64 = chart_to_base64(fig)
                chart_image.src_base64 = img_b64
                chart_image.visible = True
                output_text.visible = False

            page.update()

    file_picker = ft.FilePicker(on_result=pick_file_result)
    page.overlay.append(file_picker)

    pick_button = ft.ElevatedButton(
        "Select .ulg Log File",
        on_click=lambda _: file_picker.pick_files(
            allowed_extensions=["ulg"], allow_multiple=False
        )
    )

    page.add(
        ft.Column([
            ft.Text("PX4 Power Plot", size=20, weight="bold"),
            pick_button,
            progress_ring,
            output_text,
            chart_image
        ], expand=True)
    )

if __name__ == "__main__":
    ft.app(target=main)
