import threading
import socket
import time

def deadlock_simulation(target_ip, port1=8000, port2=8001):
    """
    Simulate a deadlock condition between two threads competing for network resources
    on the target device.
    """
    print(f"Starting deadlock simulation targeting {target_ip}...")
    
    # Shared resources (locks)
    lock1 = threading.Lock()
    lock2 = threading.Lock()
    
    def thread1_task():
        """First thread that acquires lock1 then tries to get lock2"""
        print("Thread 1: Acquiring lock1...")
        with lock1:
            print("Thread 1: Acquired lock1, trying to connect to port", port1)
            try:
                # Simulate resource usage by connecting to the target
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.settimeout(2)
                    s.connect((target_ip, port1))
                    print(f"Thread 1: Connected to {target_ip}:{port1}")
                    
                    # Hold the lock while trying to get the second resource
                    time.sleep(1)
                    print("Thread 1: Trying to acquire lock2...")
                    with lock2:
                        print("Thread 1: Acquired both locks (shouldn't happen in deadlock)")
            except Exception as e:
                print(f"Thread 1: Connection error - {str(e)}")
    
    def thread2_task():
        """Second thread that acquires lock2 then tries to get lock1"""
        print("Thread 2: Acquiring lock2...")
        with lock2:
            print("Thread 2: Acquired lock2, trying to connect to port", port2)
            try:
                # Simulate resource usage by connecting to the target
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.settimeout(2)
                    s.connect((target_ip, port2))
                    print(f"Thread 2: Connected to {target_ip}:{port2}")
                    
                    # Hold the lock while trying to get the first resource
                    time.sleep(1)
                    print("Thread 2: Trying to acquire lock1...")
                    with lock1:
                        print("Thread 2: Acquired both locks (shouldn't happen in deadlock)")
            except Exception as e:
                print(f"Thread 2: Connection error - {str(e)}")
    
    # Create and start threads
    t1 = threading.Thread(target=thread1_task)
    t2 = threading.Thread(target=thread2_task)
    
    t1.start()
    t2.start()
    
    # Let the simulation run for a while
    time.sleep(10)
    
    print("\nDeadlock simulation completed.")
    print("If the threads didn't complete their tasks, a deadlock likely occurred.")
    print("Note: This simulation creates a deadlock locally while attempting network connections.")
    print("A real network device deadlock would require specific conditions on the target system.")

if __name__ == "__main__":
    target_ip = input("Enter the target device IP address: ")
    deadlock_simulation(target_ip)