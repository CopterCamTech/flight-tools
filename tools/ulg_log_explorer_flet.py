#!/usr/bin/env python3

import os
import csv
import pandas as pd
import flet as ft
from pyulog import ULog

# --- Core parsing functions ---

def parse_ulg_file(filepath):
    ulog = ULog(filepath)
    message_types = sorted(set(msg.name for msg in ulog.data_list))
    return ulog, message_types

def get_fields_from_log(ulog, msg_type):
    try:
        dataset = ulog.get_dataset(msg_type).data
        return list(dataset.keys())
    except KeyError:
        return []

def extract_field_data(ulog, msg_type, field_name):
    try:
        dataset = ulog.get_dataset(msg_type).data
        timestamps = dataset["timestamp"]
        values = dataset[field_name]
        return list(zip(timestamps, values))
    except KeyError:
        return []

# --- Flet GUI ---

def main(page: ft.Page):
    page.title = "PX4 ULG Log Explorer"
    page.scroll = "auto"

    ulog = None
    selected_msg_type = None
    all_data = []

    output_text = ft.Text(value="", selectable=True, visible=False, color="red")
    progress_ring = ft.ProgressRing(visible=False)

    msg_label = ft.Text("Select Message Type:", visible=False, weight="bold")
    msg_dropdown = ft.Dropdown(visible=False, hint_text="Choose a message type")

    field_label = ft.Text("Select Field:", visible=False, weight="bold")
    field_dropdown = ft.Dropdown(visible=False, hint_text="Choose a field")

    # Initialize DataTable with placeholder columns
    data_table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Timestamp")),
            ft.DataColumn(ft.Text("Value"))
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

    # FilePicker used for both open and save
    file_picker = ft.FilePicker(on_result=lambda e: pick_file_result(e))
    save_picker = ft.FilePicker(on_result=lambda e: save_result(e))
    page.overlay.append(file_picker)
    page.overlay.append(save_picker)

    export_button = ft.ElevatedButton("Export to CSV", visible=False)

    def save_result(e: ft.FilePickerResultEvent):
        if e.path and all_data:
            try:
                with open(e.path, "w", newline="") as f:
                    writer = csv.writer(f)
                    writer.writerow(["Timestamp", "Value"])
                    for ts, val in all_data:
                        writer.writerow([ts, val])
                output_text.value = f"Exported {len(all_data)} rows to {e.path}"
                output_text.color = "green"
                output_text.visible = True
            except Exception as ex:
                output_text.value = f"Error saving file: {ex}"
                output_text.color = "red"
                output_text.visible = True
            page.update()

    def export_clicked(e):
        if all_data:
            save_picker.save_file(
                file_name="ulg_log_export.csv",  # suggested default
                allowed_extensions=["csv"]
            )

    export_button.on_click = export_clicked

    def pick_file_result(e: ft.FilePickerResultEvent):
        nonlocal ulog
        if e.files:
            progress_ring.visible = True
            output_text.visible = False
            msg_dropdown.visible = False
            msg_label.visible = False
            field_dropdown.visible = False
            field_label.visible = False
            results_panel.visible = False
            export_button.visible = False
            page.update()

            filepath = e.files[0].path
            try:
                ulog, message_types = parse_ulg_file(filepath)
                msg_dropdown.options = [ft.dropdown.Option(mt) for mt in message_types]
                msg_dropdown.visible = True
                msg_label.visible = True
                output_text.value = f"Loaded {len(message_types)} message types."
                output_text.color = "black"
                output_text.visible = True
            except Exception as ex:
                output_text.value = f"Error: {ex}"
                output_text.color = "red"
                output_text.visible = True

            progress_ring.visible = False
            page.update()

    def msg_selected(e):
        nonlocal selected_msg_type
        selected_msg_type = msg_dropdown.value
        fields = get_fields_from_log(ulog, selected_msg_type)
        field_dropdown.options = [ft.dropdown.Option(f) for f in fields]
        field_dropdown.visible = True
        field_label.visible = True
        results_panel.visible = False
        export_button.visible = False
        page.update()

    def field_selected(e):
        nonlocal all_data
        field_name = field_dropdown.value
        progress_ring.visible = True
        results_panel.visible = False
        export_button.visible = False
        page.update()

        all_data = extract_field_data(ulog, selected_msg_type, field_name)

        progress_ring.visible = False

        if not all_data:
            output_text.value = "No data found for this field."
            output_text.color = "red"
            output_text.visible = True
            results_panel.visible = False
            export_button.visible = False
        else:
            # Render directly from memory
            def format_val(val):
                if isinstance(val, float):
                    return f"{val:.12g}"
                return str(val)

            data_table.rows = [
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text(str(ts))),
                    ft.DataCell(ft.Text(format_val(val)))
                ]) for ts, val in all_data
            ]

            data_table.visible = True
            table_scroll_panel.visible = True
            results_panel.visible = True
            export_button.visible = True

            output_text.value = f"Loaded {len(all_data)} rows into viewer."
            output_text.color = "green"
            output_text.visible = True

        page.update()

    msg_dropdown.on_change = msg_selected
    field_dropdown.on_change = field_selected

    pick_button = ft.ElevatedButton(
        "Select .ulg Log File",
        on_click=lambda _: file_picker.pick_files(
            allowed_extensions=["ulg"], allow_multiple=False
        )
    )

    page.add(
        ft.Column([
            ft.Text("PX4 ULG Log Explorer", size=20, weight="bold"),
            pick_button,
            export_button,   # export button near the top
            progress_ring,
            output_text,
            msg_label,
            msg_dropdown,
            field_label,
            field_dropdown,
            results_panel,
        ], spacing=10, expand=True)
    )

if __name__ == "__main__":
    ft.app(target=main)
