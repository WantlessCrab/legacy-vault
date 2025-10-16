# ===================================================================
# Project Rebuild: Master Diagnostic Launcher v3.2 (diagnostics.ps1)
# ===================================================================

# --- Configuration ---
# IP of the Palworld server (found via nmap/ipconfig)
$serverIp = "192.168.0.12"

# IP of your router (found via ipconfig)
$myRouterIp = "192.168.0.1"

# Public IP for general internet test
$internetTestIp = "8.8.8.8"

# Absolute path to the compiled AHK logger script in its Windows folder
$amdLoggerExePath = "C:\Users\admin\diagnostic_tools\amd_logger.exe"

# Directory where AMD saves performance logs
$amdLogDirectory = "C:\Users\admin\AppData\Local\AMD\CN"

# ===================================================================
# --- SESSION START ---
# ===================================================================

Write-Host "--- LAUNCHING DIAGNOSTIC MONITORS ---" -ForegroundColor Green

# 1. Launch IP Watcher (gping)
Write-Host "Starting gping..."
# CORRECTED COMMAND: Uses -ArgumentList to correctly pass parameters
start powershell -ArgumentList "-NoExit", "-Command", "gping $myRouterIp $serverIp $internetTestIp"

# 2. Launch System Resource Monitor (btop)
Write-Host "Starting btop..."
start btop

# 3. Launch Windows Event Viewer (Filtered View)
Write-Host "Starting Event Viewer..."
# CORRECTED COMMAND: Uses an absolute path to the view file
start eventvwr.exe /v:"$PSScriptRoot\diagnostic_view.xml"

# 4. Start AMD Performance Logging
Write-Host "Sending START signal to AMD logger..."
# CORRECTED LOGIC: Checks if the file exists before trying to run it
if (Test-Path $amdLoggerExePath) {
    & $amdLoggerExePath "toggle"
} else {
    Write-Host "ERROR: amd_logger.exe not found at $amdLoggerExePath. Skipping." -ForegroundColor Red
}

# ===================================================================
# --- SESSION ACTIVE (Script Pauses Here) ---
# ===================================================================

Write-Host "`n--- DIAGNOSTIC SESSION IS ACTIVE ---" -ForegroundColor Cyan
Write-Host "All monitors are running. Perform your tests now." -ForegroundColor Cyan
Read-Host "Press ENTER in this terminal to stop AMD logging and end the session"

# ===================================================================
# --- SESSION END ---
# ===================================================================

Write-Host "`n--- ENDING DIAGNOSTIC SESSION ---" -ForegroundColor Yellow

# 5. Stop AMD Performance Logging
Write-Host "Sending STOP signal to AMD logger..."
if (Test-Path $amdLoggerExePath) {
    & $amdLoggerExePath "toggle"
}

# 6. Open the AMD Log Directory for review
Write-Host "Opening AMD log directory for review."
Invoke-Item $amdLogDirectory

Write-Host "Script finished."