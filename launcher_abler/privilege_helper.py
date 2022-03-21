import os
import contextlib
import traceback

import win32con
import winerror
import win32api
import win32process
import win32security
import win32ts
import pywintypes

import ctypes
from ctypes import wintypes


def isUserAdmin():

    if os.name == "nt":
        import ctypes

        # WARNING: requires Windows XP SP2 or higher!
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            traceback.print_exc()
            print("Admin check failed, assuming not an admin.")
            return False
    elif os.name == "posix":
        # Check for root on Posix
        return os.getuid() == 0
    else:
        raise RuntimeError


ntdll = ctypes.WinDLL("ntdll")
kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
advapi32 = ctypes.WinDLL("advapi32", use_last_error=True)
user32 = ctypes.WinDLL("user32", use_last_error=True)

TOKEN_ADJUST_SESSIONID = 0x0100
PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
LPBYTE = ctypes.POINTER(wintypes.BYTE)


class STARTUPINFO(ctypes.Structure):
    """https://msdn.microsoft.com/en-us/library/ms686331"""

    __slots__ = ()

    _fields_ = (
        ("cb", wintypes.DWORD),
        ("lpReserved", wintypes.LPWSTR),
        ("lpDesktop", wintypes.LPWSTR),
        ("lpTitle", wintypes.LPWSTR),
        ("dwX", wintypes.DWORD),
        ("dwY", wintypes.DWORD),
        ("dwXSize", wintypes.DWORD),
        ("dwYSize", wintypes.DWORD),
        ("dwXCountChars", wintypes.DWORD),
        ("dwYCountChars", wintypes.DWORD),
        ("dwFillAttribute", wintypes.DWORD),
        ("dwFlags", wintypes.DWORD),
        ("wShowWindow", wintypes.WORD),
        ("cbReserved2", wintypes.WORD),
        ("lpReserved2", LPBYTE),
        ("hStdInput", wintypes.HANDLE),
        ("hStdOutput", wintypes.HANDLE),
        ("hStdError", wintypes.HANDLE),
    )

    def __init__(self, **kwds):
        self.cb = ctypes.sizeof(self)
        super(STARTUPINFO, self).__init__(**kwds)


LPSTARTUPINFO = ctypes.POINTER(STARTUPINFO)


class PROCESS_INFORMATION(ctypes.Structure):
    """https://msdn.microsoft.com/en-us/library/ms684873"""

    __slots__ = ()

    _fields_ = (
        ("hProcess", wintypes.HANDLE),
        ("hThread", wintypes.HANDLE),
        ("dwProcessId", wintypes.DWORD),
        ("dwThreadId", wintypes.DWORD),
    )


LPPROCESS_INFORMATION = ctypes.POINTER(PROCESS_INFORMATION)

kernel32.CloseHandle.argtypes = (wintypes.HANDLE,)

# https://msdn.microsoft.com/en-us/library/ms682434
advapi32.CreateProcessWithTokenW.argtypes = (
    wintypes.HANDLE,  # _In_        hToken
    wintypes.DWORD,  # _In_        dwLogonFlags
    wintypes.LPCWSTR,  # _In_opt_    lpApplicationName
    wintypes.LPWSTR,  # _Inout_opt_ lpCommandLine
    wintypes.DWORD,  # _In_        dwCreationFlags
    wintypes.LPCWSTR,  # _In_opt_    lpEnvironment
    wintypes.LPCWSTR,  # _In_opt_    lpCurrentDirectory
    LPSTARTUPINFO,  # _In_        lpStartupInfo
    LPPROCESS_INFORMATION,
)  # _Out_       lpProcessInformation

# https://msdn.microsoft.com/en-us/library/ms633512
user32.GetShellWindow.restype = wintypes.HWND


def adjust_token_privileges(htoken, state):
    prev_state = win32security.AdjustTokenPrivileges(htoken, False, state)
    error = win32api.GetLastError()
    if error == winerror.ERROR_NOT_ALL_ASSIGNED:
        raise pywintypes.error(
            error, "AdjustTokenPrivileges", win32api.FormatMessageW(error)
        )
    return prev_state


def enable_token_privileges(htoken, *privilege_names):
    state = []
    for name in privilege_names:
        state.append(
            (
                win32security.LookupPrivilegeValue(None, name),
                win32con.SE_PRIVILEGE_ENABLED,
            )
        )
    return adjust_token_privileges(htoken, state)


@contextlib.contextmanager
def open_effective_token(access, open_as_self=True):
    hthread = win32api.GetCurrentThread()
    impersonated_self = False
    try:
        htoken = win32security.OpenThreadToken(hthread, access, open_as_self)
    except pywintypes.error as e:
        if e.winerror != winerror.ERROR_NO_TOKEN:
            raise
        win32security.ImpersonateSelf(win32security.SecurityImpersonation)
        impersonated_self = True
        htoken = win32security.OpenThreadToken(hthread, access, open_as_self)
    try:
        yield htoken
    finally:
        if impersonated_self:
            win32security.SetThreadToken(None, None)


@contextlib.contextmanager
def enable_privileges(*privilege_names):
    """Enable a set of privileges for the current thread."""
    prev_state = ()
    with open_effective_token(
        win32con.TOKEN_QUERY | win32con.TOKEN_ADJUST_PRIVILEGES
    ) as htoken:
        prev_state = enable_token_privileges(htoken, *privilege_names)
        try:
            yield
        finally:
            if prev_state:
                adjust_token_privileges(htoken, prev_state)


def duplicate_shell_token():
    hWndShell = user32.GetShellWindow()
    if not hWndShell:
        raise pywintypes.error(
            winerror.ERROR_FILE_NOT_FOUND, "GetShellWindow", "no shell window"
        )
    tid, pid = win32process.GetWindowThreadProcessId(hWndShell)
    hProcShell = win32api.OpenProcess(win32con.PROCESS_QUERY_INFORMATION, False, pid)
    hTokenShell = win32security.OpenProcessToken(hProcShell, win32con.TOKEN_DUPLICATE)
    # Contrary to MSDN, CreateProcessWithTokenW also requires
    # TOKEN_ADJUST_DEFAULT and TOKEN_ADJUST_SESSIONID
    return win32security.DuplicateTokenEx(
        hTokenShell,
        win32security.SecurityImpersonation,
        win32con.TOKEN_ASSIGN_PRIMARY
        | win32con.TOKEN_DUPLICATE
        | win32con.TOKEN_QUERY
        | win32con.TOKEN_ADJUST_DEFAULT
        | TOKEN_ADJUST_SESSIONID,
        win32security.TokenPrimary,
        None,
    )


@contextlib.contextmanager
def impersonate_system():
    with enable_privileges(win32security.SE_DEBUG_NAME):
        pid_csr = ntdll.CsrGetProcessId()
        hprocess_csr = win32api.OpenProcess(
            PROCESS_QUERY_LIMITED_INFORMATION, False, pid_csr
        )
        htoken_csr = win32security.OpenProcessToken(
            hprocess_csr, win32con.TOKEN_DUPLICATE
        )
    htoken = win32security.DuplicateTokenEx(
        htoken_csr,
        win32security.SecurityImpersonation,
        win32con.TOKEN_QUERY
        | win32con.TOKEN_IMPERSONATE
        | win32con.TOKEN_ADJUST_PRIVILEGES,
        win32security.TokenImpersonation,
    )
    enable_token_privileges(
        htoken,
        win32security.SE_TCB_NAME,
        win32security.SE_INCREASE_QUOTA_NAME,
        win32security.SE_ASSIGNPRIMARYTOKEN_NAME,
    )
    try:
        htoken_prev = win32security.OpenThreadToken(
            win32api.GetCurrentThread(), win32con.TOKEN_IMPERSONATE, True
        )
    except pywintypes.error as e:
        if e.winerror != winerror.ERROR_NO_TOKEN:
            raise
        htoken_prev = None
    win32security.SetThreadToken(None, htoken)
    try:
        yield
    finally:
        win32security.SetThreadToken(None, htoken_prev)


def startupinfo_update(si_src, si_dst):
    for name in (
        "lpDesktop",
        "lpTitle",
        "dwX",
        "dwY",
        "dwXSize",
        "dwYSize",
        "dwXCountChars",
        "dwYCountChars",
        "dwFillAttribute",
        "dwFlags",
        "wShowWindow",
        "hStdInput",
        "hStdOutput",
        "hStdError",
    ):
        try:
            setattr(si_dst, name, getattr(si_src, name))
        except AttributeError:
            pass


def runas_session_user(
    cmd,
    executable=None,
    creationflags=0,
    cwd=None,
    startupinfo=None,
    return_handles=False,
):
    if not creationflags & win32con.DETACHED_PROCESS:
        creationflags |= win32con.CREATE_NEW_CONSOLE
    if cwd is None:
        cwd = os.getcwd()
    si = win32process.STARTUPINFO()
    if startupinfo:
        startupinfo_update(startupinfo, si)
    with impersonate_system():
        htoken_user = win32ts.WTSQueryUserToken(win32ts.WTS_CURRENT_SESSION)
        hProcess, hThread, dwProcessId, dwThreadId = win32process.CreateProcessAsUser(
            htoken_user,
            executable,
            cmd,
            None,
            None,
            False,
            creationflags,
            None,
            cwd,
            si,
        )
    if return_handles:
        return hProcess, hThread
    return dwProcessId, dwThreadId


def runas_shell_user(
    cmd,
    executable=None,
    creationflags=0,
    cwd=None,
    startupinfo=None,
    return_handles=False,
):
    if not creationflags & win32con.DETACHED_PROCESS:
        creationflags |= win32con.CREATE_NEW_CONSOLE
    if cwd is None:
        cwd = os.getcwd()
    si = STARTUPINFO()
    if startupinfo:
        startupinfo_update(startupinfo, si)
    pi = PROCESS_INFORMATION()
    try:
        htoken = duplicate_shell_token()
    except pywintypes.error as e:
        if e.winerror != winerror.ERROR_FILE_NOT_FOUND:
            raise
        return runas_session_user(
            cmd, executable, creationflags, cwd, startupinfo, return_handles
        )
    with enable_privileges(win32security.SE_IMPERSONATE_NAME):
        if not advapi32.CreateProcessWithTokenW(
            int(htoken),
            0,
            executable,
            cmd,
            creationflags,
            None,
            cwd,
            ctypes.byref(si),
            ctypes.byref(pi),
        ):
            error = ctypes.get_last_error()
            raise pywintypes.error(
                error, "CreateProcessWithTokenW", win32api.FormatMessageW(error)
            )
    hProcess = pywintypes.HANDLE(pi.hProcess)
    hThread = pywintypes.HANDLE(pi.hThread)
    if return_handles:
        return hProcess, hThread
    return pi.dwProcessId, pi.dwThreadId
