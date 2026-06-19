"""
CyberKey Windows Locker

Purpose:
- Provide a small Windows lock helper.
- Keep default behavior safe.
- Never unlock Windows.
- Never authenticate users.

Security rule:
BLE proximity may only trigger restrictive actions such as locking.
It must never be used for unlock or authentication.
"""

import argparse
import ctypes
import platform


def is_windows() -> bool:
    return platform.system().lower() == "windows"


def lock_windows() -> bool:
    """
    Lock the current Windows workstation.

    Returns:
        True if the Windows API call was executed successfully.
        False if the current platform is not Windows.
    """
    if not is_windows():
        print("LockWorkStation is only available on Windows.")
        return False

    result = ctypes.windll.user32.LockWorkStation()
    return bool(result)


def would_lock_now(reason: str = "manual-test") -> None:
    """
    Safe test-mode output.
    This does not lock the machine.
    """
    print(f"WOULD_LOCK_NOW reason={reason}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="CyberKey Windows lock helper"
    )

    parser.add_argument(
        "--lock-now",
        action="store_true",
        help="Actually lock Windows. Use only for manual testing."
    )

    parser.add_argument(
        "--confirm",
        action="store_true",
        help="Required together with --lock-now to prevent accidental locking."
    )

    args = parser.parse_args()

    if args.lock_now and args.confirm:
        print("Locking Windows now...")
        lock_windows()
        return

    would_lock_now("test-mode")


if __name__ == "__main__":
    main()
