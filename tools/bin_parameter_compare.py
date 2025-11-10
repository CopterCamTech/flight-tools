import sys
import os
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

def extract_parameters(filepath):
    _, messages_by_type = parse_bin_file(filepath)
    
#    print("Available message types:", list(messages_by_type.keys()))

    
#    param_messages = messages_by_type.get("PARM", [])
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

def main():
    if len(sys.argv) != 3:
        print("Usage: python bin_parameter_compare.py log1.bin log2.bin")
        sys.exit(1)

    log1, log2 = sys.argv[1], sys.argv[2]

    params1 = extract_parameters(log1)
    params2 = extract_parameters(log2)

    _, messages1 = parse_bin_file(log1)
    _, messages2 = parse_bin_file(log2)
    version1 = get_firmware_version(messages1)
    version2 = get_firmware_version(messages2)

    print(f"Parameter Name;{os.path.basename(log1)} ({version1});{os.path.basename(log2)} ({version2})")

    diffs = compare_parameters(params1, params2)
    for param, val1, val2 in diffs:
        print(f"{param};{val1};{val2}")

if __name__ == "__main__":
    main()
