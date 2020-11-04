#!/usr/bin/env python3
import sys
import argparse
import datetime
import json
import os
from pandas_datareader import data
from enum import Enum


class AlarmState(Enum):
    Inactive = 0
    Active = 1


alarmsConfigFile = 'config/alarms.json'
alarmsIsChanged = False
alarms = []
hysteresis = 10  # percent value


def alarmsRead():
    global alarmsConfigFile
    global alarms
    if os.path.isfile(alarmsConfigFile):
        with open(alarmsConfigFile, 'r') as f:
            alarms = json.load(f)


def alarmsWrite():
    global alarmsConfigFile
    global alarms
    with open(alarmsConfigFile, 'w') as f:
        json.dump(alarms, f, indent=4, sort_keys=True)


def alarmsShow():
    global alarmsConfigFile
    global alarms
    for alarm in alarms:
        print(alarm)


def alarmsAdd(name, reference, alarmType, value, state):
    global alarms
    alarms.append({'name': name, 'reference': float(reference),
                   'type': str(alarmType), 'value': float(value), 'state': int(state.value)})


def alarmsRemove(name, reference, alarmType, value):
    global alarms
    try:
        alarms.remove({'name': name, 'reference': float(reference),
                       'type': str(alarmType), 'value': float(value), 'state': AlarmState.Active})
    except ValueError:
        pass
    try:
        alarms.remove({'name': name, 'reference': float(reference),
                       'type': str(alarmType), 'value': float(value), 'state': AlarmState.Inactive})
    except ValueError:
        pass


def alarmPrint(alarm):
    print(alarm)


def alarmCheck(value, alarm):
    diffrence = abs(close[-1] - alarm['reference'])
    if alarm['type'] == 'percent':
        valueChange = float(alarm['reference'] * alarm['value']) / 100
    else:
        valueChange = alarm['value']
    valueChangeReset = valueChange - float(valueChange * hysteresis) / 100

    # Check if alarm happend!
    if ((alarm['state'] == AlarmState.Active) and (diffrence > valueChange)):
        print('!Alarm! ' + str(alarm['name']) + ' price ' + str(price) + ' '
              '(ref. ' + str(alarm['reference']) + ' +/-' + str(valueChange) + ')!')
        alarms[i]['state'] = AlarmState.Inactive
        return True
    # Check if alarm should be reseted!
    if ((alarm['state'] == AlarmState.Inactive) and (diffrence <= valueChangeReset)):
        print('Alarm reseted!')
        alarms[i]['state'] = AlarmState.Active
        return True
    return False


parser = argparse.ArgumentParser()
parser.add_argument('-a', '--addAlarm', action='store_true',
                    required=False, help='Adds given alarm')
parser.add_argument('-d', '--deleteAlarm', action='store_true',
                    required=False, help='Removes alarm')
parser.add_argument('-c', '--checkAlarms', action='store_true',
                    required=False, help='Check all alarms')
parser.add_argument('-p', '--printAlarms', action='store_true',
                    required=False, help='Print all alarms')
parser.add_argument('-n', '--stockCode', type=str, required=False, help='')
parser.add_argument('-r', '--referencePrice',
                    type=float, required=False, help='')
parser.add_argument('-t', '--type', type=str, required=False, help='')
parser.add_argument('-v', '--value', type=float, required=False, help='')
parser.add_argument('-W', '--lastWeek', action='store_true',
                    required=False, help='Last Week')
args = parser.parse_args()

# Assert
if (not args.addAlarm and not args.checkAlarms and not args.deleteAlarm and not args.printAlarms):
    print('Missing event')
    sys.exit(1)

if (args.addAlarm):
    if (not args.stockCode or not args.referencePrice or not args.type or not args.value):
        print('Missing arguments for adding.')
        sys.exit(1)

if (args.deleteAlarm):
    if (not args.stockCode or not args.referencePrice or not args.type or not args.value):
        print('Missing arguments for removal.')
        sys.exit(1)

# End date
currentDateTime = datetime.datetime.now()
end_date = currentDateTime.strftime('%Y-%m-%d')
# Check last month
tmpDate = datetime.datetime.now() - datetime.timedelta(days=30)
start_date = tmpDate.strftime('%Y-%m-%d')

alarmsRead()

# 0. Adding alarms
# #####################################################33
if (args.addAlarm):
    alarmsRemove(args.stockCode, args.referencePrice, args.type, args.value)
    alarmsAdd(args.stockCode, args.referencePrice,
              args.type, args.value, AlarmState.Active)
    alarmsIsChanged = True

# 1. Removing alarms
# #####################################################33
if (args.deleteAlarm):
    alarmsRemove(args.stockCode, args.referencePrice, args.type, args.value)
    alarmsIsChanged = True

# 2. Checking alarms
# #####################################################33
for i in range(len(alarms)):
    alarm = alarms[i]
    if (args.printAlarms):
        alarmPrint(alarm)

    if (args.checkAlarms):
        # User pandas_reader.data.DataReader to load the desired data. As simple as that.
        panel_data = data.DataReader(
            alarm['name'], 'stooq', start_date, end_date)

        if len(panel_data) != 0:
            close = panel_data['Close']
            price = close[-1]

            if (alarmCheck(price, alarm) is True):
                alarmsIsChanged = True
        else:
            print('No Stooq data for entry!')


# 4. Write alarms if were changed
# #####################################################33
if (alarmsIsChanged is True):
    alarmsWrite()
