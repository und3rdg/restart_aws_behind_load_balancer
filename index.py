#!/usr/bin/python3
import sys
sys.path.append('lib')
import subprocess
import json
import pprint
pp = pprint.PrettyPrinter(depth=6).pprint

set = {
        'aws': 'aws',
        'service': 'ec2',
        'only_tag': 'production',
        'profile': 'wk',
        }

def run_command(command):
    print('\nRunning: ' + command[0] + "\n" + '...')
    res = subprocess.run(command, env=dict(AWS_PROFILE='wk'), stdout=subprocess.PIPE)
    print('Done!')
    return res.stdout

instances = json.loads(run_command(
    [
    set['aws'],
    set['service'],
    'describe-instances',
    ]
    ))['Reservations']


def filter_tag_name(tag):
    return tag['Key'] == "Name"


def filtered():
    out = []
    for instance in instances:
        tag = list(filter(filter_tag_name, instance['Instances'][0]['Tags']))
        o = {
                "InstanceId": instance['Instances'][0]['InstanceId'],
                "Tag": tag[0]['Value'],
                "PublicIpAddress": instance['Instances'][0]['PublicIpAddress'],
        }
        if(tag[0]['Value'] == set['only_tag']):
            out.append(o)
    return out




def reboot(InstanceId):
    run_command([
        set['aws'],
        set['service'],
        'reboot-instances',
        '--instance-ids=' + InstanceId,
        # '--dry-run',
    ])

def user_interaction(filtered) :
    pp(filtered)
    print()
    for el in filtered:
        answer = input("restart http://" + el['PublicIpAddress'] + " ? (y/N): ").lower()
        if answer[:1] == 'y':
            reboot(el['InstanceId'])
            print('done: ' + el['PublicIpAddress'])

user_interaction(filtered())

