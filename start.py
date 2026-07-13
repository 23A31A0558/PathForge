# start.py
import os
import sys
import time
import socket
import subprocess
import webbrowser

def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('127.0.0.1', port)) == 0

def get_python_executable(backend_dir):
    # Try using the virtual environment python first
    if sys.platform == "win32":
        venv_python = os.path.join(backend_dir, "venv", "Scripts", "python.exe")
    else:
        venv_python = os.path.join(backend_dir, "venv", "bin", "python")
        
    if os.path.exists(venv_python):
        return venv_python
    
    # Fallback to sys.executable (current running python)
    return sys.executable

def main():
    root_dir = os.path.dirname(os.path.abspath(__file__))
    backend_dir = os.path.join(root_dir, "backend")
    
    print("=" * 60)
    print("           PATHFORGE WEBSERVER STARTUP SERVICE")
    print("=" * 60)
    
    port = 8000
    if is_port_in_use(port):
        print(f"[*] Port {port} is already in use.")
        print(f"[*] It looks like PathForge is already running.")
        print(f"[*] Opening browser to http://127.0.0.1:{port} ...")
        webbrowser.open(f"http://127.0.0.1:{port}")
        return

    python_exec = get_python_executable(backend_dir)
    print(f"[*] Using Python executable: {python_exec}")
    print(f"[*] Launching FastAPI backend server...")
    
    # Start uvicorn server in a subprocess
    # We run it with cwd=backend_dir so that relative paths (like database) resolve correctly.
    cmd = [python_exec, "-m", "uvicorn", "main:app", "--host", "127.0.0.1", "--port", str(port)]
    
    try:
        process = subprocess.Popen(
            cmd,
            cwd=backend_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
    except Exception as e:
        print(f"[!] Failed to launch server process: {e}")
        sys.exit(1)
        
    # Wait for the port to become active (maximum 5 seconds)
    started = False
    for _ in range(10):
        time.sleep(0.5)
        if is_port_in_use(port):
            started = True
            break
        if process.poll() is not None:
            # Process terminated early
            break

    if started:
        print(f"[+] PathForge is now live at: http://127.0.0.1:{port}")
        print("[+] Opening your default web browser...")
        webbrowser.open(f"http://127.0.0.1:{port}")
        print("\n" + "=" * 60)
        print(" SERVER IS LIVE. PRESS CTRL+C IN THIS TERMINAL TO STOP THE SERVER.")
        print("=" * 60 + "\n")
        
        try:
            # Stream logs in real-time
            for line in iter(process.stdout.readline, ""):
                sys.stdout.write(line)
                sys.stdout.flush()
        except KeyboardInterrupt:
            print("\n[*] Stopping PathForge backend server...")
            process.terminate()
            try:
                process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                process.kill()
            print("[+] Server stopped.")
    else:
        print("[!] Backend server failed to start or bind to port 8000.")
        if process.poll() is not None:
            print("[!] Exit code:", process.returncode)
            print("[!] Output logs:")
            print(process.stdout.read())
        else:
            process.terminate()
            
if __name__ == "__main__":
    main()

