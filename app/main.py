from flask import Flask, request, Response
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
import time
import psutil
import threading

app = Flask(__name__)

# Renamed and adjusted metrics
REQUEST_COUNTER = Counter(
    "webapp_requests_total",
    "Total HTTP requests received",
    ["path", "status_code"]
)

REQUEST_LATENCY = Histogram(
    "webapp_request_duration_seconds",
    "Histogram of request durations",
    ["path"]
)

CPU_USAGE = Gauge(
    "webapp_cpu_usage_percent",
    "System CPU usage percentage"
)

MEMORY_USAGE = Gauge(
    "webapp_memory_usage_bytes",
    "System memory usage in bytes"
)

DISK_USAGE = Gauge(
    "webapp_disk_usage_percent",
    "System disk usage percentage"
)

@app.route("/")
def index():
    start = time.time()
    response = "Hello from a fully monitored Flask app!"
    duration = time.time() - start

    REQUEST_LATENCY.labels("/").observe(duration)
    REQUEST_COUNTER.labels("/", "200").inc()

    return response

@app.route("/about")
def about():
    start = time.time()
    response = "This is the about page."
    duration = time.time() - start

    REQUEST_LATENCY.labels("/about").observe(duration)
    REQUEST_COUNTER.labels("/about", "200").inc()

    return response

@app.route("/status")
def status():
    start = time.time()
    # Capture disk usage at request time
    DISK_USAGE.set(psutil.disk_usage('/').percent)

    response = "System status checked."
    duration = time.time() - start

    REQUEST_LATENCY.labels("/status").observe(duration)
    REQUEST_COUNTER.labels("/status", "200").inc()

    return response

@app.route("/metrics")
def metrics():
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)

def update_system_metrics():
    while True:
        CPU_USAGE.set(psutil.cpu_percent(interval=1))
        MEMORY_USAGE.set(psutil.virtual_memory().used)

if __name__ == "__main__":
    threading.Thread(target=update_system_metrics, daemon=True).start()
    app.run(host="0.0.0.0", port=8000)