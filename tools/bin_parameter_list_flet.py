#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import flet as ft
from pymavlink import mavutil

def extract_parameters(filepath):
    try:
        if not os.path.exists(filepath):
            return {'error': f"File not found: {filepath}"}

        mlog = mavutil.mavlink_connection(filepath)
        param_dict = {}

        while True:
            msg = mlog.recv_match(blocking=False)
            if msg is None:
                break

            msg_type = msg.get_type()

            if msg_type == 'PARAM_VALUE':
                param_dict[msg.param_id] = msg.param_value
            elif msg_type == 'PARM':
                param_dict[msg.Name] = msg.Value

        if not param_dict:
            return {'error': "No parameters found in .bin file"}

        return {
            'filename': os.path.basename(filepath),
            'parameters': dict(sorted(param_dict.items()))
        }

    except Exception as e:
        return {'error': str(e)}

# --- Flet UI wrapper ---
def main(page: ft.Page):
    page.title = "ArduPilot Parameter List"
    page.scroll = "auto"

    output_area = ft.Text(value="", selectable=True, visible=False)
    progress_ring = ft.ProgressRing(visible=False)

    table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Parameter Name")),
            ft.DataColumn(ft.Text("Value"))
        ],
        rows=[],
        visible=False
    )

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
            progress_ring.visible = True
            output_area.visible = False
            table.visible = False
            page.update()

            filepath = e.files[0].path
            result = extract_parameters(filepath)

            progress_ring.visible = False

            if "error" in result:
                output_area.value = f"Error: {result['error']}"
                output_area.visible = True
                table.visible = False
            else:
                table.rows = [
                    ft.DataRow(cells=[
                        ft.DataCell(ft.Text(str(key))),
                        ft.DataCell(ft.Text(str(value)))
                    ])
                    for key, value in result['parameters'].items()
                ]
                table.visible = True
                output_area.visible = False
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
            ft.Text("ArduPilot Parameter List", size=20, weight="bold"),
            pick_button,
            progress_ring,
            output_area,
            table,
            another_button
        ])
    )

if __name__ == "__main__":
    ft.app(target=main)
