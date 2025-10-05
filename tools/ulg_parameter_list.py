from pyulog import ULog

def extract_parameters(filepath):
    try:
        ulog = ULog(filepath)
        parameters = ulog.initial_parameters
        return {'parameters': dict(sorted(parameters.items()))}
    except Exception as e:
        return {'error': str(e)}

