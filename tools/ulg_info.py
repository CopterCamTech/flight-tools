from pyulog import ULog
import os

def extract_ulg_info(filepath):
    print("Received file path:", filepath)
    print("File exists:", os.path.exists(filepath))
    try:
        ulog = ULog(filepath)
        message_types = sorted(set(ulog.data_list[i].name for i in range(len(ulog.data_list))))
        total_messages = sum(len(entry.data['timestamp']) for entry in ulog.data_list)
        duration = (ulog.last_timestamp - ulog.start_timestamp) / 1e6

        return {
            'message_types': message_types,
            'total_messages': total_messages,
            'log_duration': f"{duration:.2f} seconds",
        }

    except Exception as e:
        return {'error': str(e)}

