#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import flet as ft
import pymavlink
from pymavlink import DFReader

# Set MAVLink dialect explicitly
os.environ['MAVLINK_DIALECT'] = 'ardupilotmega'

def extract_bin_info(filepath):
    try:
        if not os.path.exists(filepath):
            return {'error': f"File not found: {filepath}"}

        reader = DFReader.DFReader_binary(filepath)

        message_types = set()
        total_messages = 0
        timestamps = []

        while True:
            msg = reader.recv_msg()
            if msg is None:
                break
            try:
                msg_type = msg.get_type()
                message_types.add(msg_type)
                total_messages += 1

                if hasattr(msg, '_timestamp') and msg._timestamp is not None:
                    timestamps.append(msg._timestamp)

            except Exception:
                message_types.add('UNKNOWN')

        if timestamps:
            duration_sec = max(timestamps) - min(timestamps)
            duration_min = round(duration_sec / 60, 2)
            duration_str = f"{duration_min} minutes"
        else:
            duration_str = "Unknown (no valid timestamps)"

        return {
            'filename': os.path.basename(filepath),
            'message_types': sorted(message_types),
            'total_messages': total_messages,
            'log_duration': duration_str,
        }

    except Exception as e:
        return {'error': str(e)}

# --- Flet UI wrapper ---
def main(page: ft.Page):
    page.title = "ArduPilot Log Summary"
    page.scroll = "auto"

    output_area = ft.Text(value="", selectable=True)
    progress_ring = ft.ProgressRing(visible=False)

    # Button starts hidden
    another_button = ft.ElevatedButton(
        "Select Another .bin File",
        visible=False,
        on_click=lambda _: file_picker.pick_files(
            allowed_extensions=["bin"],
            allow_multiple=False
        )
    )

    def pick_file_result(e: ft.FilePickerResultEvent):
        if e.files:
            # Show progress indicator
            progress_ring.visible = True
            output_area.value = "Processing log file..."
            page.update()

            filepath = e.files[0].path
            result = extract_bin_info(filepath)

            # Hide progress indicator
            progress_ring.visible = False

            if "error" in result:
                output_area.value = f"Error: {result['error']}"
            else:
                summary = []
                summary.append(f"Log Summary for {result['filename']}")
                summary.append(f"Total Messages: {result['total_messages']}")
                summary.append(f"Log Duration: {result['log_duration']}")
                summary.append("Message Types:")
                for msg_type in result['message_types']:
                    summary.append(f"  - {msg_type}")
                output_area.value = "\n".join(summary)

                # Reveal the "Select Another" button only after first report
                another_button.visible = True

            page.update()

    file_picker = ft.FilePicker(on_result=pick_file_result)
    page.overlay.append(file_picker)

    pick_button = ft.ElevatedButton(
        "Select .bin Log File",
        on_click=lambda _: file_picker.pick_files(
            allowed_extensions=["bin"],
            allow_multiple=False
        )
    )

    page.add(
        ft.Column([
            ft.Text("ArduPilot Log Summary", size=20, weight="bold"),
            pick_button,
            progress_ring,
            output_area,
            another_button
        ])
    )

if __name__ == "__main__":
    ft.app(target=main)
