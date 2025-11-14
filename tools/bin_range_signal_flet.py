#!/usr/bin/env python3

import os
import sys
import math
import base64
from io import BytesIO
import matplotlib
matplotlib.use("Agg")  # ✅ Non-GUI backend
import matplotlib.pyplot as plt
import flet as ft
from pymavlink import mavutil

# --- Core logic ---
def compute_range(pn, pe, pd):
    return math.sqrt(pn**2 + pe**2 + pd**2)

def extract_signal_data(filepath):
    mlog = mavutil.mavlink_connection(filepath)
    range_rxrssi, range_rxlq, range_rad_rssi = [], [], []
    latest_rssi, latest_rad = {}, {}

    while True:
        msg = mlog.recv_match(type=["XKF1", "RSSI", "RAD"], blocking=False)
        if msg is None:
            break

        msg_type = msg.get_type()
        data = msg.to_dict()

        if msg_type == "RSSI":
            latest_rssi["RXRSSI"] = data.get("RXRSSI")
            latest_rssi["RXLQ"] = data.get("RXLQ")
        elif msg_type == "RAD":
            latest_rad["RSSI"] = data.get("RSSI")
        elif msg_type == "XKF1":
            pn, pe, pd = getattr(msg, "PN", None), getattr(msg, "PE", None), getattr(msg, "PD", None)
            if None in (pn, pe, pd):
                continue
            range_val = compute_range(pn, pe, pd)

            if latest_rssi.get("RXRSSI") is not None:
                range_rxrssi.append((range_val, latest_rssi["RXRSSI"]))
            if latest_rssi.get("RXLQ") is not None:
                range_rxlq.append((range_val, latest_rssi["RXLQ"]))
            if latest_rad.get("RSSI") is not None:
                range_rad_rssi.append((range_val, latest_rad["RSSI"]))

            latest_rssi.clear()
            latest_rad.clear()

    return range_rxrssi, range_rxlq, range_rad_rssi

def generate_range_signal_chart(rxrssi, rxlq, rad_rssi):
    # 🔎 Enlarged figure size (25% bigger)
    fig, ax1 = plt.subplots(figsize=(17.5, 7.5))
    ax2 = ax1.twinx()
    ax3 = None

    ax1.set_ylabel("Control Radio Link Quality (RXLQ)", color="green")
    ax2.set_ylabel("Control Radio RSSI (RXRSSI)", color="blue")
    ax1.tick_params(axis="y", labelcolor="green")
    ax2.tick_params(axis="y", labelcolor="blue")

    if rxrssi:
        x, y = zip(*rxrssi)
        ax2.scatter(x, y, color="blue", marker="^", s=40, alpha=0.7)
    if rxlq:
        x, y = zip(*rxlq)
        ax1.scatter(x, y, color="green", marker="v", s=60, alpha=0.7)
    if rad_rssi:
        ax3 = ax1.twinx()
        ax3.spines.right.set_position(("axes", 1.12))
        ax3.set_ylabel("Telemetry Radio RSSI (RAD.RSSI)", color="orange", fontsize=12)
        ax3.tick_params(axis="y", labelcolor="orange")
        x, y = zip(*rad_rssi)
        ax3.scatter(x, y, color="orange", marker="D", s=50, alpha=0.7)

    ax1.set_xlabel("3D Distance from Home (meters)")
    ax1.grid(True)
    plt.title("ArduPilot Range vs Signal Strength", fontsize=14)
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
    page.title = "ArduPilot Range vs Signal Strength"
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
            rxrssi, rxlq, rad_rssi = extract_signal_data(filepath)

            progress_ring.visible = False

            if not (rxrssi or rxlq or rad_rssi):
                output_text.value = "Error: No valid signal data found in log file."
                output_text.visible = True
                chart_image.visible = False
            else:
                fig = generate_range_signal_chart(rxrssi, rxlq, rad_rssi)
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
            ft.Text("ArduPilot Range vs Signal Strength", size=20, weight="bold"),
            pick_button,
            progress_ring,
            output_text,
            chart_image
        ], expand=True)
    )

if __name__ == "__main__":
    ft.app(target=main)
