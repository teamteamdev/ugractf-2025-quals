#include <windows.h>

void __cdecl _start() {
    WriteFile(GetStdHandle(STD_OUTPUT_HANDLE), L"The flag is hidden somewhere\r\n", 60, NULL, NULL);
    ExitProcess(0);
}
