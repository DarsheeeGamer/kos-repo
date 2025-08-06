#!/usr/bin/env python3
"""
KOS System Monitor
==================
Real-time system resource monitoring for KOS
"""

import os
import time
import psutil
import shutil
from datetime import datetime

class SystemMonitor:
    """System resource monitor for KOS"""
    
    def __init__(self):
        self.running = False
        
    def get_cpu_info(self):
        """Get CPU usage information"""
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_count = psutil.cpu_count()
        cpu_freq = psutil.cpu_freq()
        
        return {
            'usage': cpu_percent,
            'cores': cpu_count,
            'frequency': f"{cpu_freq.current:.2f} MHz" if cpu_freq else "N/A"
        }
    
    def get_memory_info(self):
        """Get memory usage information"""
        mem = psutil.virtual_memory()
        swap = psutil.swap_memory()
        
        return {
            'total': self.format_bytes(mem.total),
            'used': self.format_bytes(mem.used),
            'free': self.format_bytes(mem.free),
            'percent': mem.percent,
            'swap_total': self.format_bytes(swap.total),
            'swap_used': self.format_bytes(swap.used),
            'swap_percent': swap.percent
        }
    
    def get_disk_info(self):
        """Get disk usage information"""
        disk = psutil.disk_usage('/')
        
        return {
            'total': self.format_bytes(disk.total),
            'used': self.format_bytes(disk.used),
            'free': self.format_bytes(disk.free),
            'percent': disk.percent
        }
    
    def get_network_info(self):
        """Get network statistics"""
        net = psutil.net_io_counters()
        
        return {
            'bytes_sent': self.format_bytes(net.bytes_sent),
            'bytes_recv': self.format_bytes(net.bytes_recv),
            'packets_sent': net.packets_sent,
            'packets_recv': net.packets_recv
        }
    
    def get_process_info(self, limit=5):
        """Get top processes by CPU and memory usage"""
        processes = []
        
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                processes.append(proc.info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        # Sort by CPU usage
        top_cpu = sorted(processes, key=lambda x: x.get('cpu_percent', 0), reverse=True)[:limit]
        
        # Sort by memory usage
        top_mem = sorted(processes, key=lambda x: x.get('memory_percent', 0), reverse=True)[:limit]
        
        return {'top_cpu': top_cpu, 'top_memory': top_mem}
    
    def format_bytes(self, bytes):
        """Format bytes to human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes < 1024.0:
                return f"{bytes:.2f} {unit}"
            bytes /= 1024.0
        return f"{bytes:.2f} PB"
    
    def clear_screen(self):
        """Clear the terminal screen"""
        os.system('clear' if os.name == 'posix' else 'cls')
    
    def display_header(self):
        """Display header with timestamp"""
        width = shutil.get_terminal_size().columns
        print("=" * width)
        print(f"KOS System Monitor - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}".center(width))
        print("=" * width)
    
    def display_info(self):
        """Display all system information"""
        self.clear_screen()
        self.display_header()
        
        # CPU Information
        cpu = self.get_cpu_info()
        print("\n📊 CPU Information:")
        print(f"  Usage: {cpu['usage']}%")
        print(f"  Cores: {cpu['cores']}")
        print(f"  Frequency: {cpu['frequency']}")
        
        # Memory Information
        mem = self.get_memory_info()
        print("\n💾 Memory Information:")
        print(f"  Total: {mem['total']}")
        print(f"  Used: {mem['used']} ({mem['percent']:.1f}%)")
        print(f"  Free: {mem['free']}")
        print(f"  Swap: {mem['swap_used']} / {mem['swap_total']} ({mem['swap_percent']:.1f}%)")
        
        # Disk Information
        disk = self.get_disk_info()
        print("\n💿 Disk Information:")
        print(f"  Total: {disk['total']}")
        print(f"  Used: {disk['used']} ({disk['percent']:.1f}%)")
        print(f"  Free: {disk['free']}")
        
        # Network Information
        net = self.get_network_info()
        print("\n🌐 Network Statistics:")
        print(f"  Bytes sent: {net['bytes_sent']}")
        print(f"  Bytes received: {net['bytes_recv']}")
        print(f"  Packets sent: {net['packets_sent']}")
        print(f"  Packets received: {net['packets_recv']}")
        
        # Top Processes
        procs = self.get_process_info()
        print("\n🔝 Top Processes by CPU:")
        for proc in procs['top_cpu']:
            if proc['cpu_percent'] > 0:
                print(f"  [{proc['pid']:5}] {proc['name'][:20]:20} {proc['cpu_percent']:5.1f}%")
        
        print("\n🔝 Top Processes by Memory:")
        for proc in procs['top_memory']:
            if proc['memory_percent'] > 0:
                print(f"  [{proc['pid']:5}] {proc['name'][:20]:20} {proc['memory_percent']:5.1f}%")
    
    def run_continuous(self, interval=2):
        """Run continuous monitoring"""
        self.running = True
        print("Starting continuous monitoring... Press Ctrl+C to stop")
        time.sleep(1)
        
        try:
            while self.running:
                self.display_info()
                print(f"\n🔄 Refreshing in {interval} seconds... (Press Ctrl+C to stop)")
                time.sleep(interval)
        except KeyboardInterrupt:
            self.running = False
            print("\n\n✅ Monitoring stopped.")
    
    def run_once(self):
        """Display system information once"""
        self.display_info()
        print("\n✅ System snapshot complete.")

def cli_app():
    """Main CLI application entry point"""
    monitor = SystemMonitor()
    
    print("KOS System Monitor")
    print("==================")
    print("1. Show system info once")
    print("2. Continuous monitoring (2 sec refresh)")
    print("3. Continuous monitoring (custom interval)")
    print("4. Exit")
    print()
    
    while True:
        try:
            choice = input("Select option [1-4]: ").strip()
            
            if choice == '1':
                monitor.run_once()
                print()
            elif choice == '2':
                monitor.run_continuous(2)
                print()
            elif choice == '3':
                interval = input("Enter refresh interval in seconds: ").strip()
                try:
                    interval = float(interval)
                    if interval < 0.5:
                        print("Minimum interval is 0.5 seconds")
                        continue
                    monitor.run_continuous(interval)
                except ValueError:
                    print("Invalid interval. Please enter a number.")
                print()
            elif choice == '4' or choice.lower() == 'exit':
                print("Exiting System Monitor...")
                break
            else:
                print("Invalid option. Please select 1-4.")
        except KeyboardInterrupt:
            print("\n\nExiting System Monitor...")
            break
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    cli_app()