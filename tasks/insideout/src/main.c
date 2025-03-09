#include <windows.h>

long _tls_index;

void __cdecl wWinMainCRTStartup() {
    WCHAR *pFlag = NULL;
    int szFlag = LoadStringW(NULL, (WORD)0x100, (LPWSTR)&pFlag, 0);
    HANDLE hOut = GetStdHandle(STD_OUTPUT_HANDLE);
    WriteFile(hOut, L"The flag is ", 24, NULL, NULL);
    WriteFile(hOut, pFlag, szFlag * 2, NULL, NULL);
    WriteFile(hOut, L"\r\n", 4, NULL, NULL);
    ExitProcess(0);
}
