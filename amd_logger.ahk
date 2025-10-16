#SingleInstance

; Check if the first command-line argument is exactly "toggle"
if A_Args[1] == "toggle" {
    ; Send the Ctrl+Shift+L keystroke
    Send "^+L"
}
ExitApp()