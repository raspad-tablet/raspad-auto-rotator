#!/usr/bin/env python3
import os, sys
import time

# AUTOSTART_DIR = "/home/%s/.config/autostart/" % USER
AUTOSTART_DIR = "/etc/xdg/autostart/"
CONFIG_TXT = "/boot/config.txt"
CONFIG_TXT_UBUNTU = "/boot/config.txt"
if not os.isfile("/boot/config.txt"):
    CONFIG_TXT = CONFIG_TXT_UBUNTU
errors = []

avaiable_options = ['-h', '--help', '--no-dep', '--no-reboot']

USER = os.getenv("SUDO_USER")
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
    global isreboot
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
        do(msg="update apt-get",
            cmd='run_command("apt-get update")')
        do(msg="install i2c-tools",
            cmd='run_command("apt-get install i2c-tools -y")')
        do(msg="install xinput",
            cmd='run_command("apt-get install xinput -y")')

    print("Setup interfaces")
    do(msg="turn on I2C",
        cmd='Config(file=%s).set("dtparam=i2c_arm", "on")' % CONFIG_TXT)
    do(msg="Add I2C module",
        cmd='Modules().set("i2c-dev")')

    print("Setup raspad-auto-rotator service")
    do(msg="copy rotate-helper file",
        cmd='run_command("cp ./raspad-auto-rotator /usr/local/bin/")')
    do(msg="add excutable mode for rotate-helper",
        cmd='run_command("chmod +x /usr/local/bin/raspad-auto-rotator")')
    if not os.path.isdir("/home/%s/.config/raspad-auto-rotator"%USER):
        do(msg="create config folder",
            cmd='run_command("mkdir /home/%s/.config/raspad-auto-rotator/")'%USER)
    do(msg="create config",
        cmd='run_command("touch /home/%s/.config/raspad-auto-rotator/config")'%USER)
    do(msg="change owner",
        cmd='run_command("chown -R pi:pi /home/%s/.config/raspad-auto-rotator/")'%USER)
    do(msg="change mode",
        cmd='run_command("chmod -R 700 /home/%s/.config/raspad-auto-rotator/")'%USER)

    # AutoStart
    if not os.path.isdir("%s" % AUTOSTART_DIR):
        do(msg="mkdir autostart", cmd='run_command("mkdir %s/")' % AUTOSTART_DIR)
        # do(msg="change owner",
        #     cmd='run_command("chown -R pi:pi %s/")' % AUTOSTART_DIR)

    do(msg="copy autostart",
        cmd='run_command("cp ./raspad-auto-rotator.desktop %s")' % AUTOSTART_DIR)
    # do(msg="change owner",
    #     cmd='run_command("chown -R pi:pi %s/raspad-auto-rotator.desktop")' % AUTOSTART_DIR)
    # do(msg="copy autostart",
    #     cmd='run_command("cp ./raspad-auto-rotator-first-calibrate.desktop %s")' % AUTOSTART_DIR)
    # do(msg="change owner",
    #     cmd='run_command("chown -R pi:pi %s/raspad-auto-rotator-first-calibrate.desktop")' % AUTOSTART_DIR)

    do(msg="Get SH3001 library",
        cmd='run_command("git clone https://github.com/sunfounder/python-sh3001.git")')
    os.chdir("./python-sh3001")
    print("Install sh3001 python package")
    do(msg="run setup file",
        cmd='run_command("python3 setup.py install")')
    os.chdir("../")

    if len(errors) == 0:
        print("\n\n========================================\n")
        if "--no-reboot" not in options:
            select = input("Installation needs to reboot. Do you want to reboot right now? (y/N): ")
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


def do(msg="", cmd=""):
    print(" - %s..." % (msg), end='\r')
    print(" - %s... " % (msg), end='')
    status, result = eval(cmd)
    # print(status, result)
    if status == 0 or status == None or result == "":
        print('Done')
    else:
        print('Error')
        errors.append("%s error:\n  Status:%s\n  Error:%s" %
                      (msg, status, result))

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
