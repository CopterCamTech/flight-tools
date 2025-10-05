import os
import matplotlib.pyplot as plt
from datetime import datetime
import random
import string

GRAPH_DIR = "/tmp/flight_graphs"
os.makedirs(GRAPH_DIR, exist_ok=True)

def save_timestamped_plot(fig):
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M")
    suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    filename = f"graph_{timestamp}_{suffix}.png"
    filepath = os.path.join(GRAPH_DIR, filename)

    fig.savefig(filepath)
    plt.close(fig)
    return filename

def cleanup_old_plots(max_age_minutes=60):
    now = datetime.utcnow().timestamp()
    for fname in os.listdir(GRAPH_DIR):
        fpath = os.path.join(GRAPH_DIR, fname)
        if not os.path.isfile(fpath):
            continue
        age = now - os.path.getmtime(fpath)
        if age > max_age_minutes * 60:
            os.remove(fpath)

def cleanup_uploads(upload_dir, max_age_minutes=60):
    now = datetime.utcnow().timestamp()
    for fname in os.listdir(upload_dir):
        fpath = os.path.join(upload_dir, fname)
        if not os.path.isfile(fpath):
            continue
        age = now - os.path.getmtime(fpath)
        if age > max_age_minutes * 60:
            os.remove(fpath)

