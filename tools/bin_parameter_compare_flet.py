#!/usr/bin/env python3

import os
import csv
import flet as ft
from pymavlink import DFReader

os.environ["MAVLINK_DIALECT"] = "ardupilotmega"

def parse_bin_file(filepath):
    reader = DFReader.DFReader_binary(filepath)
    message_types = set()
    messages_by_type = {}
    while True:
        msg = reader.recv_msg()
        if msg is None:
            break
        msg_type = msg.get_type()
        message_types.add(msg_type)
        messages_by_type.setdefault(msg_type, []).append(msg)
    return sorted(message_types), messages_by_type

def extract_parameters(filepath):
    _, messages_by_type = parse_bin_file(filepath)
    param_messages = messages_by_type.get("PARM", []) + messages_by_type.get("PARAM", [])
    parameters = {}
    for msg in param_messages:
        try:
            name = getattr(msg, "Name", None) or getattr(msg, "name", None)
            value = getattr(msg, "Value", None) or getattr(msg, "value", None)
            if name is not None and value is not None:
                parameters[name] = value
        except Exception:
            continue
    return parameters

def get_firmware_version(messages_by_type):
    msg_list = messages_by_type.get("MSG", [])
    for msg in msg_list:
        try:
            message = getattr(msg, "Message", None) or getattr(msg, "message", None)
            if message and message.startswith("Ardu"):
                return message
        except Exception:
            continue
    return "Unknown version"

def compare_parameters(params1, params2):
    all_keys = sorted(set(params1.keys()) | set(params2.keys()))
    diffs = []
    for key in all_keys:
        val1 = params1.get(key, "N/A")
        val2 = params2.get(key, "N/A")
        if val1 != val2:
            diffs.append((key, val1, val2))
    return diffs

def main(page: ft.Page):
    page.title = "ArduPilot BIN Parameter Compare"
    page.scroll = "auto"

    log1_path = None
    log2_path = None
    params1 = {}
    params2 = {}
    version1 = "Unknown"
    version2 = "Unknown"
    diffs = []

    output_text = ft.Text(value="", selectable=True, visible=False, color="red")
    progress_ring = ft.ProgressRing(visible=False)

    log1_label = ft.Text(value="", visible=False)
    log2_label = ft.Text(value="", visible=False)

    compare_button = ft.ElevatedButton("Compare Parameters", visible=False)

    data_table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Parameter Name")),
            ft.DataColumn(ft.Text("Value 1")),
            ft.DataColumn(ft.Text("Value 2"))
        ],
        rows=[],
        visible=False
    )

    table_scroll_panel = ft.Column(
        controls=[data_table],
        scroll="auto",
        expand=True,
        visible=False
    )

    results_panel = ft.Container(
        content=table_scroll_panel,
        expand=True,
        border=ft.border.all(1, "gray"),
        padding=10,
        visible=False
    )

    file_picker1 = ft.FilePicker(on_result=lambda e: pick_file1(e))
    file_picker2 = ft.FilePicker(on_result=lambda e: pick_file2(e))
    save_picker = ft.FilePicker(on_result=lambda e: save_result(e))
    page.overlay.extend([file_picker1, file_picker2, save_picker])

    export_button = ft.ElevatedButton("Export to CSV", visible=False)

    def update_compare_button_visibility():
        compare_button.visible = bool(log1_path and log2_path)
        page.update()

    def save_result(e: ft.FilePickerResultEvent):
        if e.path and diffs:
            try:
                with open(e.path, "w", newline="") as f:
                    writer = csv.writer(f)
                    writer.writerow(["Parameter Name", f"{os.path.basename(log1_path)} ({version1})", f"{os.path.basename(log2_path)} ({version2})"])
                    for name, val1, val2 in diffs:
                        writer.writerow([name, val1, val2])
                output_text.value = f"Exported {len(diffs)} differences to {e.path}"
                output_text.color = "green"
                output_text.visible = True
            except Exception as ex:
                output_text.value = f"Error saving file: {ex}"
                output_text.color = "red"
                output_text.visible = True
            page.update()

    def export_clicked(e):
        if diffs:
            save_picker.save_file(
                file_name="bin_parameter_diff.csv",
                allowed_extensions=["csv"]
            )

    export_button.on_click = export_clicked

    def pick_file1(e: ft.FilePickerResultEvent):
        nonlocal log1_path
        if e.files:
            log1_path = e.files[0].path
            log1_label.value = f"Selected: {os.path.basename(log1_path)}"
            log1_label.visible = True
            update_compare_button_visibility()

    def pick_file2(e: ft.FilePickerResultEvent):
        nonlocal log2_path
        if e.files:
            log2_path = e.files[0].path
            log2_label.value = f"Selected: {os.path.basename(log2_path)}"
            log2_label.visible = True
            update_compare_button_visibility()

    def run_comparison(e):
        progress_ring.visible = True
        output_text.visible = False
        results_panel.visible = False
        export_button.visible = False
        page.update()

        try:
            params1.clear()
            params2.clear()
            params1.update(extract_parameters(log1_path))
            params2.update(extract_parameters(log2_path))
            _, messages1 = parse_bin_file(log1_path)
            _, messages2 = parse_bin_file(log2_path)
            nonlocal version1, version2, diffs
            version1 = get_firmware_version(messages1)
            version2 = get_firmware_version(messages2)
            diffs = compare_parameters(params1, params2)

            def format_val(val):
                if isinstance(val, float):
                    return f"{val:.12g}"
                return str(val)

            data_table.columns = [
                ft.DataColumn(ft.Text("Parameter Name")),
                ft.DataColumn(ft.Text(f"{os.path.basename(log1_path)} ({version1})")),
                ft.DataColumn(ft.Text(f"{os.path.basename(log2_path)} ({version2})"))
            ]

            data_table.rows = [
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text(name)),
                    ft.DataCell(ft.Text(format_val(val1))),
                    ft.DataCell(ft.Text(format_val(val2)))
                ]) for name, val1, val2 in diffs
            ]

            output_text.value = f"Found {len(diffs)} differing parameters."
            output_text.color = "green"
            output_text.visible = True
            data_table.visible = True
            table_scroll_panel.visible = True
            results_panel.visible = True
            export_button.visible = True

        except Exception as ex:
            output_text.value = f"Error comparing logs: {ex}"
            output_text.color = "red"
            output_text.visible = True

        progress_ring.visible = False
        page.update()

    compare_button.on_click = run_comparison

    pick_button1 = ft.ElevatedButton(
        "Select First .bin Log File",
        on_click=lambda _: file_picker1.pick_files(
            allowed_extensions=["bin"], allow_multiple=False
        )
    )

    pick_button2 = ft.ElevatedButton(
        "Select Second .bin Log File",
        on_click=lambda _: file_picker2.pick_files(
            allowed_extensions=["bin"], allow_multiple=False
        )
    )

    page.add(
        ft.Column([
            ft.Text("ArduPilot BIN Parameter Compare", size=20, weight="bold"),
            pick_button1,
            log1_label,
            pick_button2,
            log2_label,
            compare_button,
            export_button,
            progress_ring,
            output_text,
            results_panel,
        ], spacing=10, expand=True)
    )

if __name__ == "__main__":
    ft.app(target=main)
