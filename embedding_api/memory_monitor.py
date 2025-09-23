# embedding_api/memory_monitor.py
import psutil
import os
import time
from datetime import datetime
# Import tracemalloc
import tracemalloc # <-- Make sure this is imported
from typing import Dict, List

class MemoryMonitor:
    def __init__(self):
        self.process = psutil.Process()
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.memory_snapshots: List[Dict] = []
        # --- Fix: Start tracing when the monitor is initialized ---
        # Check if tracing is already started to avoid errors if called multiple times
        if not tracemalloc.is_tracing():
            tracemalloc.start()
            print("Tracemalloc started for memory monitoring.")
        # --- End Fix ---

    # Keep start_tracing method, maybe it's called manually elsewhere
    def start_tracing(self):
        if not tracemalloc.is_tracing():
            tracemalloc.start()
            print("Tracemalloc started via start_tracing method.")
        # Store the initial snapshot
        self.memory_snapshots.append({
            'timestamp': datetime.now(),
            'snapshot': tracemalloc.take_snapshot()
        })

    def get_leak_suspects(self) -> List[tuple]:
        if len(self.memory_snapshots) < 2:
            return []

        current = self.memory_snapshots[-1]['snapshot']
        previous = self.memory_snapshots[-2]['snapshot']

        # Ensure comparison is done correctly
        try:
            return current.compare_to(previous, 'lineno')[:10]
        except Exception as e:
            print(f"Error comparing snapshots: {e}")
            return []

    def get_memory_stats(self) -> Dict:
        mem_info = self.process.memory_info()
        return {
            'rss': mem_info.rss / (1024 * 1024),      # MB
            'vms': mem_info.vms / (1024 * 1024),      # MB
            'percent': self.process.memory_percent(),
            'cpu_percent': self.process.cpu_percent(),
            'open_files': len(self.process.open_files()),
            'connections': len(self.process.connections())
        }

    def monitor(self, interval: int = 60):
        print("Starting memory monitoring...")
        # Take the first snapshot immediately after starting tracing (handled in __init__ or start_tracing)
        # Let's take the first snapshot here after ensuring tracing is on
        try:
            self.memory_snapshots.append({
                'timestamp': datetime.now(),
                'snapshot': tracemalloc.take_snapshot() # This should now work
            })
            print("Initial memory snapshot taken.")
        except Exception as e:
             print(f"Could not take initial snapshot: {e}")

        while True:
            stats = self.get_memory_stats()
            # Only try to get leak suspects if snapshots were taken successfully
            leaks = []
            if len(self.memory_snapshots) >= 2:
                 try:
                     leaks = self.get_leak_suspects()
                 except Exception as leak_err:
                     print(f"Error getting leak suspects: {leak_err}")

            print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]")
            print("=== Memory Monitoring ===")
            print(f"\nMemory Usage:")
            print(f"- RSS (Physical): {stats['rss']:.2f} MB")
            print(f"- VMS (Total): {stats['vms']:.2f} MB")
            print(f"- System Memory Usage: {stats['percent']:.1f}%")
            print(f"- CPU Usage: {stats['cpu_percent']:.1f}%")

            if leaks:
                print("\nPotential Memory Leaks:")
                for leak in leaks:
                    # Access traceback details safely
                    if leak.traceback:
                        filename = leak.traceback[0].filename if leak.traceback else "Unknown"
                    else:
                        filename = "Unknown"
                    print(f"- {leak.count} blocks, {leak.size / 1024:.2f} KB: {filename}")

            print("\nSystem Resources:")
            print(f"- Open Files: {stats['open_files']}")
            print(f"- Network Connections: {stats['connections']}")

            # Take the next snapshot
            try:
                self.memory_snapshots.append({
                    'timestamp': datetime.now(),
                    'snapshot': tracemalloc.take_snapshot()
                })
            except Exception as snap_err:
                print(f"Error taking snapshot: {snap_err}")

            # Manage snapshot history
            if len(self.memory_snapshots) > 5:
                self.memory_snapshots.pop(0)

            time.sleep(interval)
