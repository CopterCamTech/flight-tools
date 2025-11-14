#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import flet as ft
from pyulog import ULog

def extract_ulg_info(filepath):
    try:
        if not os.path.exists(filepath):
            return {'error': f"File not found: {filepath}"}

        ulog = ULog(filepath)
        message_types = sorted(set(entry.name for entry in ulog.data_list))
        total_messages = sum(len(entry.data['timestamp']) for entry in ulog.data_list)
        duration = (ulog.last_timestamp - ulog.start_timestamp) / 1e6

        return {
            'filename': os.path.basename(filepath),
            'message_types': message_types,
            'total_messages': total_messages,
            'log_duration': f"{duration:.2f} seconds",
        }

    except Exception as e:
        return {'error': str(e)}

# --- Flet UI wrapper ---
def main(page: ft.Page):
    page.title = "PX4 ULG Log Summary"
    page.scroll = "auto"

    output_area = ft.Text(value="", selectable=True)
    progress_ring = ft.ProgressRing(visible=False)

    another_button = ft.ElevatedButton(
        "Select Another .ulg File",
        visible=False,
        on_click=lambda _: file_picker.pick_files(
            allowed_extensions=["ulg"],
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
            result = extract_ulg_info(filepath)

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
        "Select .ulg Log File",
        on_click=lambda _: file_picker.pick_files(
            allowed_extensions=["ulg"],
            allow_multiple=False
        )
    )

    page.add(
        ft.Column([
            ft.Text("PX4 ULG Log Summary", size=20, weight="bold"),
            pick_button,
            progress_ring,
            output_area,
            another_button
        ])
    )

if __name__ == "__main__":
    ft.app(target=main)
