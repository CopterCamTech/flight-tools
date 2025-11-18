#!/usr/bin/env python3
"""
bin_parameter_compare.py
Compare parameters between two ArduPilot .bin log files.
Reports parameter values in CSV format, with options to use initial or final values.
"""

import os
import sys
import argparse
from pymavlink import DFReader

def parse_bin_file(filepath):
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")

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

def extract_parameters(filepath, mode="final"):
    """
    Extract parameters from a .bin file.
    mode = "initial" -> first occurrence of each parameter
    mode = "final"   -> last occurrence of each parameter
    """
    _, messages_by_type = parse_bin_file(filepath)
    param_messages = messages_by_type.get("PARM", []) + messages_by_type.get("PARAM", [])
    parameters = {}

    for msg in param_messages:
        try:
            name = getattr(msg, "Name", None) or getattr(msg, "name", None)
            value = getattr(msg, "Value", None) or getattr(msg, "value", None)
            if name is not None and value is not None:
                if mode == "initial":
                    if name not in parameters:  # keep first occurrence
                        parameters[name] = value
                else:  # "final"
                    parameters[name] = value  # overwrite, last occurrence wins
        except Exception:
            continue

    return parameters

def compare_parameters(file1, file2, mode1="final", mode2="final"):
    """Compare parameters between two .bin files with mode options."""
    params1 = extract_parameters(file1, mode=mode1)
    params2 = extract_parameters(file2, mode=mode2)

    diffs = {}
    all_keys = set(params1.keys()) | set(params2.keys())
    for key in all_keys:
        val1 = params1.get(key)
        val2 = params2.get(key)
        if val1 != val2:
            diffs[key] = (val1, val2)

    return {
        'file1': os.path.basename(file1),
        'file2': os.path.basename(file2),
        'differences': diffs,
        'total': len(all_keys)
    }

def main():
    parser = argparse.ArgumentParser(description="Compare ArduPilot parameters in two .bin files")
    parser.add_argument("log1", help="First .bin file")
    parser.add_argument("log2", help="Second .bin file")
    parser.add_argument("--file1_mode", choices=["initial", "final"], default="final",
                        help="Use 'initial' or 'final' values for file1 (default: final)")
    parser.add_argument("--file2_mode", choices=["initial", "final"], default="final",
                        help="Use 'initial' or 'final' values for file2 (default: final)")
    parser.add_argument("-o", "--output", help="Optional output file path")
    args = parser.parse_args()

    try:
        result = compare_parameters(args.log1, args.log2,
                                    mode1=args.file1_mode,
                                    mode2=args.file2_mode)

        if result['differences']:
            header = "Parameter,File1,File2"
            lines = [header]
            for key, (val1, val2) in sorted(result['differences'].items()):
                def fmt(val):
                    if val is None:
                        return "N/A"
                    if isinstance(val, float):
                        return f"{val:.6f}"
                    return str(val)
                lines.append(f"{key},{fmt(val1)},{fmt(val2)}")

            if args.output:
                with open(args.output, "w") as f:
                    f.write("\n".join(lines))
                print(f"Comparison written to {args.output}")
            else:
                print("\n".join(lines))
            print(f"\n🔎 {len(result['differences'])} parameters differ out of {result['total']} compared.")
        else:
            print("✅ No parameter differences found.")

    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(2)

if __name__ == "__main__":
    main()
