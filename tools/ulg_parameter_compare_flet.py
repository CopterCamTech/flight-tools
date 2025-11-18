#!/usr/bin/env python3

import os
import csv
import flet as ft
from pyulog import ULog

def extract_parameters(filepath, mode="final"):
    ulog = ULog(filepath)
    parameters = {}
    for name, value in ulog.initial_parameters.items():
        parameters[name] = value
    return parameters

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
    page.title = "PX4 ULG Parameter Compare"
    page.scroll = "auto"

    log1_path = None
    log2_path = None
    mode1 = "final"
    mode2 = "final"
    params1 = {}
    params2 = {}
    diffs = []

    output_text = ft.Text(value="", selectable=True, visible=False, color="red")
    progress_ring = ft.ProgressRing(visible=False)

    log1_label = ft.Text(value="", visible=False)
    log2_label = ft.Text(value="", visible=False)

    # Checkboxes for file 1
    initial_checkbox1 = ft.Checkbox(label="Initial values", value=False)
    final_checkbox1 = ft.Checkbox(label="Final values", value=True)

    def update_mode1(e):
        nonlocal mode1
        if e.control == initial_checkbox1 and initial_checkbox1.value:
            final_checkbox1.value = False
            mode1 = "initial"
        elif e.control == final_checkbox1 and final_checkbox1.value:
            initial_checkbox1.value = False
            mode1 = "final"
        page.update()

    initial_checkbox1.on_change = update_mode1
    final_checkbox1.on_change = update_mode1

    # Checkboxes for file 2
    initial_checkbox2 = ft.Checkbox(label="Initial values", value=False)
    final_checkbox2 = ft.Checkbox(label="Final values", value=True)

    def update_mode2(e):
        nonlocal mode2
        if e.control == initial_checkbox2 and initial_checkbox2.value:
            final_checkbox2.value = False
            mode2 = "initial"
        elif e.control == final_checkbox2 and final_checkbox2.value:
            initial_checkbox2.value = False
            mode2 = "final"
        page.update()

    initial_checkbox2.on_change = update_mode2
    final_checkbox2.on_change = update_mode2

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
                    writer.writerow([
                        "Parameter Name",
                        f"{os.path.basename(log1_path)} ({mode1} values)",
                        f"{os.path.basename(log2_path)} ({mode2} values)"
                    ])
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
                file_name="ulg_parameter_diff.csv",
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
            params1.update(extract_parameters(log1_path, mode1))
            params2.update(extract_parameters(log2_path, mode2))
            nonlocal diffs
            diffs = compare_parameters(params1, params2)

            def format_val(val):
                if isinstance(val, float):
                    return f"{val:.12g}"
                return str(val)

            data_table.columns = [
                ft.DataColumn(ft.Text("Parameter Name")),
                ft.DataColumn(ft.Text(f"{os.path.basename(log1_path)} ({mode1} values)")),
                ft.DataColumn(ft.Text(f"{os.path.basename(log2_path)} ({mode2} values)"))
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
        "Select First .ulg Log File",
        on_click=lambda _: file_picker1.pick_files(
            allowed_extensions=["ulg"], allow_multiple=False
        )
    )

    pick_button2 = ft.ElevatedButton(
        "Select Second .ulg Log File",
        on_click=lambda _: file_picker2.pick_files(
            allowed_extensions=["ulg"], allow_multiple=False
        )
    )

    page.add(
        ft.Column([
            ft.Text("PX4 ULG Parameter Compare", size=20, weight="bold"),
            pick_button1,
            log1_label,
            ft.Row([initial_checkbox1, final_checkbox1]),
            pick_button2,
            log2_label,
            ft.Row([initial_checkbox2, final_checkbox2]),
            compare_button,
            export_button,
            progress_ring,
            output_text,
            results_panel,
        ], spacing=10, expand=True)
    )

if __name__ == "__main__":
    ft.app(target=main)
