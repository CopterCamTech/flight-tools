#!/usr/bin/env python3

import math
import base64
from io import BytesIO
from pathlib import Path
import matplotlib
matplotlib.use("Agg")  # ✅ Non-GUI backend
import matplotlib.pyplot as plt
import flet as ft
from pyulog import ULog

# --- Core logic ---
def compute_range(x, y, z):
    return math.sqrt(x**2 + y**2 + z**2)

def parse_ulg_log(filepath):
    try:
        ulog = ULog(filepath)
    except Exception as e:
        return None, None, None, f"❌ Failed to parse .ulg file: {e}"

    def extract(msg_name, field):
        msg = next((m for m in ulog.data_list if m.name == msg_name), None)
        return msg.data[field] if msg and field in msg.data else []

    x_vals = extract("vehicle_local_position_setpoint", "x")
    y_vals = extract("vehicle_local_position_setpoint", "y")
    z_vals = extract("vehicle_local_position_setpoint", "z")
    ctrl_rssi = extract("input_rc", "rssi")
    ctrl_lq = extract("input_rc", "link_quality")
    telem_rssi = extract("radio_status", "rssi")

    min_len = min(len(x_vals), len(y_vals), len(z_vals))
    ranges = [compute_range(x_vals[i], y_vals[i], z_vals[i]) for i in range(min_len)]

    range_ctrl_rssi = [(r, v) for r, v in zip(ranges, ctrl_rssi) if v not in [-1, None]]
    range_ctrl_lq = [(r, v) for r, v in zip(ranges, ctrl_lq) if v not in [-1, None]]
    range_telem_rssi = [(r, v) for r, v in zip(ranges, telem_rssi) if v not in [-1, 0, None]]

    return range_ctrl_rssi, range_ctrl_lq, range_telem_rssi, None

def generate_range_signal_chart(ctrl_rssi, ctrl_lq, telem_rssi):
    # 🔎 Enlarged figure size (25% bigger)
    fig, ax1 = plt.subplots(figsize=(17.5, 7.5))
    ax2 = ax1.twinx()
    ax3 = None

    ax1.set_ylabel("Control Radio Link Quality (input_rc.link_quality)", color="green")
    ax2.set_ylabel("Control Radio RSSI (input_rc.rssi)", color="blue")
    ax1.tick_params(axis="y", labelcolor="green")
    ax2.tick_params(axis="y", labelcolor="blue")

    if ctrl_rssi:
        x, y = zip(*ctrl_rssi)
        ax2.scatter(x, y, color="blue", marker="^", s=40, alpha=0.7)
    if ctrl_lq:
        x, y = zip(*ctrl_lq)
        ax1.scatter(x, y, color="green", marker="v", s=60, alpha=0.7)
    if telem_rssi:
        ax3 = ax1.twinx()
        ax3.spines.right.set_position(("axes", 1.12))
        ax3.set_ylabel("Telemetry Radio RSSI (radio_status.rssi)", color="orange", fontsize=12)
        ax3.tick_params(axis="y", labelcolor="orange")
        x, y = zip(*telem_rssi)
        ax3.scatter(x, y, color="orange", marker="D", s=50, alpha=0.7)

    ax1.set_xlabel("3D Distance from Home (meters)")
    ax1.grid(True)
    plt.title("PX4 Range vs Signal Strength", fontsize=14)
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
    page.title = "PX4 Range vs Signal Strength"
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
            ctrl_rssi, ctrl_lq, telem_rssi, parse_error = parse_ulg_log(filepath)

            progress_ring.visible = False

            if parse_error:
                output_text.value = f"Error: {parse_error}"
                output_text.visible = True
                chart_image.visible = False
            elif not (ctrl_rssi or ctrl_lq or telem_rssi):
                output_text.value = "Error: No valid signal data found in log file."
                output_text.visible = True
                chart_image.visible = False
            else:
                fig = generate_range_signal_chart(ctrl_rssi, ctrl_lq, telem_rssi)
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
            ft.Text("PX4 Range vs Signal Strength", size=20, weight="bold"),
            pick_button,
            progress_ring,
            output_text,
            chart_image
        ], expand=True)
    )

if __name__ == "__main__":
    ft.app(target=main)
