import sys
import platform
import socket
from datetime import datetime
import psutil

def get_system_telemetry() -> dict:
    """
    Returns safe, read-only system telemetry metrics.
    """
    cpu = psutil.cpu_percent(interval=None)
    ram = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    return {
        "cpu_percent": cpu,
        "ram_percent": ram.percent,
        "ram_used_gb": round(ram.used / (1024**3), 2),
        "ram_total_gb": round(ram.total / (1024**3), 2),
        "disk_percent": disk.percent,
        "disk_free_gb": round(disk.free / (1024**3), 2),
        "os": f"{platform.system()} {platform.release()}",
        "python_version": sys.version.split()[0],
        "hostname": socket.gethostname(),
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

def get_formatted_status() -> str:
    """Returns formatted human-readable system status report."""
    t = get_system_telemetry()
    return (f"System Telemetry Report:\n"
            f"• OS: {t['os']} (Host: {t['hostname']})\n"
            f"• Python: v{t['python_version']}\n"
            f"• CPU Load: {t['cpu_percent']}%\n"
            f"• RAM Load: {t['ram_percent']}% ({t['ram_used_gb']}GB / {t['ram_total_gb']}GB)\n"
            f"• Disk Load: {t['disk_percent']}% ({t['disk_free_gb']}GB free)")
