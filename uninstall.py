#!/usr/bin/env python3
import os, sys
import time

USER = os.environ.get('SUDO_USER')
AUTOSTART_DIR = "/etc/xdg/autostart/"
# AUTOSTART_DIR = "/usr/lib/systemd/system/"
CONFIG_TXT = "/boot/config.txt"
CONFIG_FOLDER = '/home/%s/.raspad-auto-rotator' % USER
CONFIG_FILE = '%s/config' % CONFIG_FOLDER

need_reboot = False
errors = []

avaiable_options = ['-h', '--help', '--no-reboot']

if USER == None:
    print("You must run this with sudo")
    quit()
isreboot = False
usage = '''
Usage:
    sudo python3 uninstall.py [option]

Options:
               --no-reboot  Do not ask for reboot
    -h         --help       Show this help text and exit
'''
def uninstall():
    global isreboot, need_reboot
    options = []
    if len(sys.argv) > 1:
        options = sys.argv[1:]
        for o in options:
            if o not in avaiable_options:
                print("Option {} is not found.".format(o))
                print(usage)
                quit()
    if "-h" in options or "--help" in options:
        print(usage)
        quit()
    print("Uninstalling RasPad auto rotator")

    print("Remove raspad-auto-rotator service")
    do(msg="remove raspad-auto-rotator file",
        cmd='run_command("rm -rf /usr/local/bin/raspad-auto-rotator")')
    do(msg="remove rotate-helper file",
        cmd='run_command("rm -rf /usr/local/bin/rotate-helper")')
    do(msg="remove config folder",
        cmd='run_command("rm -rf %s")' % CONFIG_FOLDER)

    do(msg="remove autostart",
        cmd='run_command("rm -rf %s/raspad-auto-rotator.desktop")' % AUTOSTART_DIR)

    do(msg="remove SH3001 library",
        cmd='run_command("pip uninstall python-sh3001")')
    do(msg="Start auto rotator",
        cmd='run_command("sudo killall raspad-auto-rotator")')

    if len(errors) == 0:
        print("\n\n========================================\nUninstallation finished!")
        if "--no-reboot" not in options and need_reboot:
            select = input("\nInstallation needs to reboot. Do you want to reboot right now? (y/N): ")
            if select.lower() == "y":
                print("Reboot!")
                isreboot = True
            else:
                print("Canceled")
    else:
        print("\n\nError happened in uninstall process:")
        for error in errors:
            print(error)
        print("Try to fix it yourself, or contact service@sunfounder.com with this message")
        sys.exit(1)

def cleanup():
    run_command("rm -rf python-sh3001")

class Modules(object):
    ''' 
        To setup /etc/modules
    '''

    def __init__(self, file="/etc/modules"):
        self.file = file
        with open(self.file, 'r') as f:
            self.configs = f.read()
        self.configs = self.configs.split('\n')

    def remove(self, expected):
        for config in self.configs:
            if expected in config:
                self.configs.remove(config)
        return self.write_file()

    def set(self, name):
        have_excepted = False
        for i in range(len(self.configs)):
            config = self.configs[i]
            if name in config:
                have_excepted = True
                tmp = name
                self.configs[i] = tmp
                break

        if not have_excepted:
            tmp = name
            self.configs.append(tmp)
        return self.write_file()

    def write_file(self):
        try:
            config = '\n'.join(self.configs)
            # print(config)
            with open(self.file, 'w') as f:
                f.write(config)
            return 0, config
        except Exception as e:
            return -1, e

class Config(object):
    ''' 
        To setup /boot/config.txt
    '''

    def __init__(self, file="/boot/config.txt"):
        self.file = file
        with open(self.file, 'r') as f:
            self.configs = f.read()
        self.configs = self.configs.split('\n')

    def remove(self, expected):
        for config in self.configs:
            if expected in config:
                self.configs.remove(config)
        return self.write_file()

    def set(self, name, value=None):
        have_excepted = False
        for i in range(len(self.configs)):
            config = self.configs[i]
            if name in config:
                have_excepted = True
                tmp = name
                if value != None:
                    tmp += '=' + value
                self.configs[i] = tmp
                break

        if not have_excepted:
            tmp = name
            if value != None:
                tmp += '=' + value
            self.configs.append(tmp)
        return self.write_file()

    def write_file(self):
        try:
            config = '\n'.join(self.configs)
            # print(config)
            with open(self.file, 'w') as f:
                f.write(config)
            return 0, config
        except Exception as e:
            return -1, e

class Cmdline(object):
    ''' 
        To setup /boot/cmdline.txt
    '''

    def __init__(self, file="/boot/cmdline.txt"):
        self.file = file
        with open(self.file, 'r') as f:
            cmdline = f.read()
        self.cmdline = cmdline.strip()
        self.cmds = self.cmdline.split(' ')

    def remove(self, expected):
        for cmd in self.cmds:
            if expected in cmd:
                self.cmds.remove(cmd)
        return self.write_file()

    def write_file(self):
        try:
            cmdline = ' '.join(self.cmds)
            # print(cmdline)
            with open(self.file, 'w') as f:
                f.write(cmdline)
            return 0, cmdline
        except Exception as e:
            return -1, e


def run_command(cmd=""):
    import subprocess
    p = subprocess.Popen(
        cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    result = p.stdout.read().decode('utf-8')
    status = p.poll()
    return status, result

def colored(text, color):
    color = color.lower()
    colors = {
        "grey": "\033[1;30m%s\033[0m",
        "red": "\033[1;31m%s\033[0m",
        "green": "\033[1;32m%s\033[0m",
        "yellow": "\033[1;33m%s\033[0m",
        "blue": "\033[1;34m%s\033[0m",
        "purple": "\033[1;35m%s\033[0m",
        "cyan": "\033[1;36m%s\033[0m",
        "white": "\033[1;37m%s\033[0m",
    }
    return colors[color] % text

def do(msg="", cmd=""):
    print("[    ] %s..." % (msg), end='', flush=True)
    status, result = eval(cmd)
    if status == 0 or status == None or result == "":
        print('\r[ %s ]' % colored("OK", "green"))
        return True
    else:
        print('\r[%s]' % colored("Fail", "red"))
        errors.append("%s error:\n  Status:%s\n  Error:%s" %
                      (msg, status, result))
        return False

if __name__ == "__main__":
    try:
        uninstall()
    except KeyboardInterrupt:
        print("Canceled.")
    finally:
        cleanup()
        if isreboot:
            time.sleep(1)
            run_command("reboot")

# if __name__ == "__main__":
#     test()
