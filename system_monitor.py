# file: system_monitor.py
import psutil


def system_status() -> str:
    try:
        cpu = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory().percent
        processes = [
            f"{p.info['pid']} - {p.info['name']}"
            for p in psutil.process_iter(['pid', 'name'])
        ][:5]
        processes_str = "\n".join(processes) or "[no processes]"
        return f"CPU: {cpu}%\nMemory: {memory}%\nProcesses:\n{processes_str}"
    except Exception as e:
        return f"Error: {e}"
