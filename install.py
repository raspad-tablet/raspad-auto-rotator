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

avaiable_options = ['-h', '--help', '--no-dep', '--no-reboot']

if USER == None:
    print("You must run this with sudo")
    quit()
isreboot = False
usage = '''
Usage:
    sudo python3 install.py [option]

Options:
               --no-dep     Do not download dependencies
               --no-reboot  Do not ask for reboot
    -h         --help       Show this help text and exit
'''
def install():
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
    print("Installing RasPad auto rotator")
    print("Install dependency")
    if "--no-dep" not in options:
        do(msg="update apt",
            cmd='run_command("apt update")')
        do(msg="install i2c-tools",
            cmd='run_command("apt install i2c-tools -y")')
        do(msg="install pip",
            cmd='run_command("apt install python3-pip -y")')
        do(msg="install xinput",
            cmd='run_command("apt install xinput -y")')
        do(msg="install setuptools",
            cmd='run_command("pip3 install setuptools")')

    status, result = run_command("ls /dev/i2c*")
    if result == "":
        print("Setup interfaces")
        do(msg="turn on I2C",
            cmd='Config(file=%s).set("dtparam=i2c_arm", "on")' % CONFIG_TXT)
        do(msg="Add I2C module",
            cmd='Modules().set("i2c-dev")')
        need_reboot = True
    status, result = run_command("ls /dev/i2c*")
    if "i2c" not in result:
        do(msg="Add i2c previlege to user",
            cmd='run_command("usermod -aG i2c %s")' % USER)
        need_reboot = True

    print("Setup raspad-auto-rotator service")
    do(msg="copy raspad-auto-rotator file",
        cmd='run_command("cp ./raspad-auto-rotator /usr/local/bin/")')
    do(msg="add excutable mode for raspad-auto-rotator",
        cmd='run_command("chmod +x /usr/local/bin/raspad-auto-rotator")')
    do(msg="copy rotate-helper file",
        cmd='run_command("cp ./rotate-helper /usr/local/bin/")')
    do(msg="add excutable mode for rotate-helper",
        cmd='run_command("chmod +x /usr/local/bin/rotate-helper")')
    if not os.path.isdir("/etc/raspad-auto-rotator"):
        do(msg="create config folder",
            cmd='run_command("mkdir %s")' % CONFIG_FOLDER)
        do(msg="change user",
            cmd='run_command("chown %s:%s %s")' % (USER, USER, CONFIG_FOLDER))

    do(msg="copy autostart",
        cmd='run_command("cp ./raspad-auto-rotator.desktop %s")' % AUTOSTART_DIR)
    # do(msg="copy service file",
    #     cmd='run_command("cp ./raspad-auto-rotator.service %s")' % AUTOSTART_DIR)
    # do(msg="enable service",
    #     cmd='run_command("systemctl enable raspad-auto-rotator.service")')
    # do(msg="reload systemctl",
    #     cmd='run_command("systemctl daemon-reload")')
    # do(msg="start service",
    #     cmd='run_command("systemctl start raspad-auto-rotator.service")')

    do(msg="Get SH3001 library",
        cmd='run_command("git clone https://github.com/sunfounder/python-sh3001.git")')
    os.chdir("./python-sh3001")
    print("Install sh3001 python package")
    do(msg="run setup file",
        cmd='run_command("python3 setup.py install")')
    os.chdir("../")

    if len(errors) == 0:
        print("\n\n========================================\nInstallation finished!")
        if "--no-reboot" not in options and need_reboot:
            select = input("\nInstallation needs to reboot. Do you want to reboot right now? (y/N): ")
            if select.lower() == "y":
                print("Reboot!")
                isreboot = True
            else:
                print("Canceled")
    else:
        print("\n\nError happened in install process:")
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
        install()
    except KeyboardInterrupt:
        print("Canceled.")
    finally:
        cleanup()
        if isreboot:
            time.sleep(1)
            run_command("reboot")

# if __name__ == "__main__":
#     test()
