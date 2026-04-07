import os
import sys
import subprocess
from pathlib import Path

from art import LOGO

HERE = Path(__file__).parent


def main():
    clear = True
    while True:
        if clear:
            os.system("cls" if os.name == "nt" else "clear")
            print(LOGO)
            print("  1. Original build  (course version)")
            print("  2. Advanced build  (OOP, config, multi-channel)")
            print("  q. Quit")
            print()
        clear = True

        choice = input("Select an option: ").strip().lower()

        if choice == "1":
            path = HERE / "original" / "main.py"
            subprocess.run([sys.executable, str(path)], cwd=str(path.parent))
        elif choice == "2":
            path = HERE / "advanced" / "main.py"
            subprocess.run([sys.executable, str(path)], cwd=str(path.parent))
        elif choice == "q":
            break
        else:
            print("Invalid choice. Try again.")
            clear = False


if __name__ == "__main__":
    main()
