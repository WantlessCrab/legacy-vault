import argparse
import time
import platform
import subprocess
import threading
import re
from queue import Queue
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from collections import defaultdict
import os
from matplotlib.animation import FuncAnimation

# --- Configuration ---
LOG_DIRECTORY = "ping_logs"
if not os.path.exists(LOG_DIRECTORY):
    os.makedirs(LOG_DIRECTORY)
SESSION_TIMESTAMP = time.strftime("%Y-%m-%d_%H-%M-%S")
LOG_FILE_NAME = os.path.join(LOG_DIRECTORY, f"ping_session_{SESSION_TIMESTAMP}.csv")


def ping_worker(target_ip, result_queue):
    """
    Worker function that runs in a thread.
    Continuously pings a target and puts the result in a queue.
    """
    param = '-n' if platform.system().lower() == 'windows' else '-c'
    timeout_param = '-w' if platform.system().lower() == 'windows' else '-W'
    command = ['ping', param, '1', timeout_param, '2', target_ip]

    while True:
        timestamp = pd.to_datetime('now').tz_localize(None)
        try:
            output = subprocess.check_output(command, text=True, stderr=subprocess.DEVNULL)
            match = re.search(r"time=(\d+\.?\d*)\s*ms", output)
            if match:
                latency = float(match.group(1))
                result = (target_ip, timestamp, latency)
            else:
                result = (target_ip, timestamp, -1)  # Represents a failed parse
        except subprocess.CalledProcessError:
            result = (target_ip, timestamp, -1)  # Represents a timeout or unreachable host

        result_queue.put(result)
        time.sleep(0.5)  # The polling interval (0.5 seconds)


def live_plotter(target_ips):
    """Creates a live-updating plot and logs data for multiple targets."""
    results_queue = Queue()
    data_store = defaultdict(lambda: {'timestamps': [], 'latencies': []})

    # Open the log file for writing
    log_file = open(LOG_FILE_NAME, 'w', newline='')
    log_file.write("Timestamp,TargetIP,Latency(ms)\n")  # Write header

    # --- Start the Pinging Engine ---
    for ip in target_ips:
        thread = threading.Thread(target=ping_worker, args=(ip, results_queue), daemon=True)
        thread.start()
        print(f"--> Pinging worker started for {ip}")

    # --- Setup the Visual Layer ---
    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(15, 7))
    lines = {ip: ax.plot([], [], marker='o', linestyle='-', markersize=3, label=ip)[0] for ip in target_ips}

    def update(frame):
        # Process all new results from the queue
        while not results_queue.empty():
            ip, timestamp, latency = results_queue.get()

            # Log the raw data to the CSV file
            log_file.write(f"{timestamp},{ip},{latency if latency >= 0 else 'TIMEOUT'}\n")

            plot_latency = latency if latency >= 0 else None

            data_store[ip]['timestamps'].append(timestamp)
            data_store[ip]['latencies'].append(plot_latency)

        # Update the plot data for each line
        for ip, line in lines.items():
            line.set_data(data_store[ip]['timestamps'], data_store[ip]['latencies'])

        # Auto-rescale the axes
        ax.relim()
        ax.autoscale_view()

        # Re-apply formatting
        ax.legend()
        ax.grid(True, which='both', linestyle='--', linewidth=0.3)
        return lines.values()

    # --- Start the Animation ---
    ani = FuncAnimation(fig, update, interval=1000, blit=True, cache_frame_data=False)

    def on_close(event):
        print("--> Plot window closed. Finalizing logs...")
        log_file.close()
        # Save the final graph as a PNG image
        image_filename = os.path.join(LOG_DIRECTORY, f"ping_session_{SESSION_TIMESTAMP}.png")
        fig.savefig(image_filename)
        print(f"--> Final graph saved to {image_filename}")

        # Open the log directory in the default file explorer
        print(f"--> Opening log directory: {LOG_DIRECTORY}")
        if platform.system().lower() == 'windows':
            os.startfile(LOG_DIRECTORY)
        else:
            # This part handles opening the folder on Linux/macOS
            subprocess.run(['xdg-open', LOG_DIRECTORY])

    fig.canvas.mpl_connect('close_event', on_close)

    # --- Final Formatting ---
    ax.set_title('Live Ping Latency Monitor')
    ax.set_xlabel('Time')
    ax.set_ylabel('Latency (ms)')
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%I:%M:%S %p'))
    plt.xticks(rotation=15)
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Live ping plotter and logger.")
    parser.add_argument("target_ips", nargs='+', help="One or more IP addresses to monitor.")
    args = parser.parse_args()
    live_plotter(args.target_ips)