# Define P/Invoke methods for window hiding and key detection
$code = @'
[DllImport("user32.dll")]
public static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);

[DllImport("kernel32.dll")]
public static extern IntPtr GetConsoleWindow();

[DllImport("user32.dll")]
public static extern short GetAsyncKeyState(int vKey);
'@

# specific name to avoid Add-Type errors in repeated sessions
$win32 = Add-Type -MemberDefinition $code -Name "Win32HiddenAudio" -Namespace Win32 -PassThru

# Hide the console window and taskbar entry
# 0 = SW_HIDE
$consolePtr = $win32::GetConsoleWindow()
if ($consolePtr -ne [IntPtr]::Zero) {
    $win32::ShowWindow($consolePtr, 0)
}

# Kill Explorer (Taskbar/Desktop)
Stop-Process -Name explorer -Force -ErrorAction SilentlyContinue

# Download the file
$url = "https://upload.wikimedia.org/wikipedia/commons/transcoded/6/67/LL-Q34311_%28yor%29-Abike25-Adewale_Adeyinka.wav/LL-Q34311_%28yor%29-Abike25-Adewale_Adeyinka.wav.mp3"
$tempFile = "$env:TEMP\hidden_audio.mp3"
Invoke-WebRequest -Uri $url -OutFile $tempFile

# Max out volume (User requested snippet)
$k=[Math]::Ceiling(100/2);$o=New-Object -ComObject WScript.Shell;for($i = 0;$i -lt $k;$i++){$o.SendKeys([char] 175)}

# Set up Windows Media Player object
$player = New-Object -ComObject WMPlayer.OCX.7
$player.URL = $tempFile
$player.settings.volume = 100
$player.settings.setMode("loop", $true)
$player.controls.play()

# Loop until Backspace is pressed
while ($true) {
    # 0x08 is the virtual key code for Backspace
    $state = $win32::GetAsyncKeyState(0x08)
    
    # Check if the key is currently down (most significant bit set)
    if ($state -band 0x8000) {
        # Restore Explorer
        Start-Process explorer
        break
    }
    
    # Sleep to prevent high CPU usage
    Start-Sleep -Milliseconds 100
    
    # Ensure playback continues if something stopped it (though loop mode handles natural end)
    if ($player.playState -eq 1 -or $player.playState -eq 2) { 
        # 1=Stopped, 2=Paused
        $player.controls.play()
    }
}

# Cleanup
$player.controls.stop()
$player.close()
Start-Sleep -Seconds 1 # Wait for handle release
Remove-Item $tempFile -ErrorAction SilentlyContinue
