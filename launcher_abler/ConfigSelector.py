"""
Launcher Update Test
"""
import os
import pathlib
import subprocess
import shutil
import argparse
import sys


class ConfigSelector:
    def __init__(self):
        # Path settings
        self.home = pathlib.Path.home()
        self.updater = os.path.join(
            self.home, "AppData\\Roaming\\Blender Foundation\\Blender\\2.96\\updater"
        )
        self.launcher = os.path.join(self.updater, "AblerLauncher.exe")
        self.config = os.path.join(self.updater, "config.ini")
        self.config_bak = os.path.join(self.updater, "config.bak")
        self.config_data = []

        # Version
        self.abler_ver = None
        self.launcher_ver = None

        return

    def read_config(self):
        """
        Read config.ini & Extract ABLER and Launcher version.
        """

        with open(self.config, "r") as f:
            for line in f.readlines():
                line = line.strip("\n")

                if "installed" in line:
                    self.abler_ver = line.split(" ")[-1]
                elif "launcher" in line:
                    self.launcher_ver = line.split(" ")[-1]

                self.config_data.append(line)

        return

    def set_config(self):
        """
        Set ABLER & Launcher version.
        """
        get_abler = self.abler_ver if args.abler is None else args.abler
        get_launcher = self.launcher_ver if args.launcher is None else args.launcher

        if args.print:
            print(f"[config.ini]")
            print(f"ABLER    ver : {get_abler}")
            print(f"Launcher ver : {get_launcher}")

        with open(self.config, "w") as f:
            for line in self.config_data:
                if "installed" in line:
                    line = line.split(" ")[:-1]
                    line.append(get_abler)
                    line = " ".join(line)

                elif "launcher" in line:
                    line = line.split(" ")[:-1]
                    line.append(get_launcher)
                    line = " ".join(line)

                f.writelines(line)
                f.writelines("\n")

        return

    def copy_config(self):
        """
        Save back-up of config.ini
        """
        shutil.copyfile(self.config, self.config_bak)

        return

    def reset_config(self):
        """
        Reset back-up to config.ini
        """
        if os.path.isfile(self.config_bak):
            shutil.copyfile(self.config_bak, self.config)
            os.remove(self.config_bak)

        return

    def remove_backup(self):
        """
        Remove config.bak
        """
        if os.path.isfile(self.config_bak):
            os.remove(self.config_bak)

        return


def main():
    config = ConfigSelector()

    if args.copy:
        config.copy_config()

    if args.reset:
        config.reset_config()

    if args.remove:
        config.remove_backup()

    if args.run:
        config.copy_config()
        config.read_config()
        config.set_config()
        subprocess.call(config.launcher)

    return


if __name__ == "__main__":
    # Define parser
    parser = argparse.ArgumentParser(
        description="Test ABLER launcher update", usage="Parser [options]"
    )

    parser.add_argument("--launcher", "-l", action="store", default=None, type=str)
    parser.add_argument("--abler", "-a", action="store", default=None, type=str)
    parser.add_argument("--copy", "-c", action="store_true")
    parser.add_argument("--reset", "-r", action="store_true")
    parser.add_argument("--remove", action="store_true")
    parser.add_argument("--print", "-p", action="store_true")
    parser.add_argument("--run", action="store_true")

    args = parser.parse_args()

    if len(sys.argv) == 1:
        print("Please set ABLER or Launcher version.")

    else:
        main()

    if args.print:
        print(args)
