#!/usr/bin/python3
import argparse
import getpass
import datetime
import os
import time

from git import Repo
from netmiko import ConnectHandler

first_commit = False

class CiscoIos(object):
    def __init__(self):
        self.collected_data = {}

    def connect_to_device(self, hostname, username, password, secret):
        device = {'device_type':'cisco_ios',
                  'host': hostname,
                  'username': username,
                  'password': password,
                  'secret': secret
                  }
        return ConnectHandler(**device)

    def collect_cisco_ios_data(self):
        device = self.connect_to_device(host, username, password, secret)
        device.enable()
        self.collected_data['show_run'] = device.send_command_expect('show run')
        self.collected_data['version'] = device.send_command('show version')
        self.collected_data['cdp'] = device.send_command('show cdp neighbors')
        self.collected_data['env'] = device.send_command('show env all')

        return self.collected_data

class CiscoIosSwitch(CiscoIos):
    def collect(self):
        print("Connecting to device...")
        device = self.connect_to_device(host, username, password, secret)
        device.enable()
        print("Collecting information...")
        self.collect_cisco_ios_data()
        self.collected_data['switch_status'] = device.send_command('show switch')
        self.collected_data['switch_stack_ports'] = device.send_command('show switch stack-ports')
        self.collected_data['mac_table'] = device.send_command('show mac address-table | in Total')

        return self.collected_data


def git_diff():
    #make "git diff HEAD~"
    git_add_commit()
    if first_commit == True:
        print("Success!!! Nothing to compare, it was your first commit")
    else:
        repo = Repo('{}'.format(host))
        # print(repo.git.diff('HEAD~'))
        print(os.system("cd {}/ && git diff HEAD~".format(host)))

def git_add_commit():
    write_data_to_files()
    time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print("Commiting changes...")
    repo = Repo('{}'.format(host))
    repo.index.add(['*'])
    repo.index.commit(time)

def write_data_to_files():
    git_init()
    data = get_data_from_switch()
    for parameter in data:
        print('Writing {}...'.format(parameter))
        with open('{}/{}'.format(host, parameter), 'w') as file:
                file.write(data.get(parameter))

def git_init():
    if not os.path.isdir("{}/{}".format(os.environ['HOME'],host)):
        repo = Repo.init('{}/{}'.format(os.environ['HOME'],host))
        global first_commit
        first_commit = True

def get_data_from_switch():
    thing = platforms.get(args.platform)

    return thing.collect()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("hostname",
                        type=str,
                        help="device hostname")
    parser.add_argument("platform",
                        type=str,
                        help="cisco_ios_switch, cisco_ios_router")
    global host, username, password, secret, platforms, args
    args = parser.parse_args()
    host = args.hostname
    username = input('Enter username: ')
    password = getpass.getpass('Enter password: ')
    secret = getpass.getpass('Enter enable: ')
    platforms = {'cisco_ios_switch' : CiscoIosSwitch()}
    git_diff()

if __name__ == "__main__":
    main()
