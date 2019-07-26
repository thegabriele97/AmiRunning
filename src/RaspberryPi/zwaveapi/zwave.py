import requests
import time
import cfg

base_url = cfg.global_configs.zwave_base_url
username = cfg.global_configs.zwave_username
password = cfg.global_configs.zwave_password
device_url = base_url + '/ZWaveAPI/Run/devices[{}].instances[{}].commandClasses[{}]'
switch_binary = cfg.global_configs.zwave_switch_binary
sensor_binary = cfg.global_configs.zwave_sensor_binary
sensor_multi = cfg.global_configs.zwave_sensor_multi

# gets all the devices escluding the Z-Way controller
def get_all_devices():
    all_devices = requests.get(base_url + '/ZWaveAPI/Data/0', auth=(username, password)).json()
    all_devices = all_devices['devices']
    all_devices.pop('1')
    return all_devices

def get_values(device, instance, command_class):
    # get data from the multilevel class
    url_to_call = device_url.format(device, instance, command_class)
    # info from devices is in the response
    return requests.get(url_to_call, auth=(username, password)).json()

def set_value(device, instance, value):
    # turn it on (255) or off (0)
    url_to_call = (device_url + '.Set(' + str(value) + ')').format(device, instance, switch_binary)
    requests.get(url_to_call, auth=(username, password))

def wait_binary(device_key):
    all_devices=get_all_devices()
    for instance in all_devices[device_key]['instances']:
        if switch_binary in all_devices[device_key]['instances'][instance]['commandClasses']:
            set_value(device_key, instance, 255)
        if sensor_binary in all_devices[device_key]['instances'][instance]['commandClasses']:
            while 1:
                response = get_values(device_key,instance,sensor_binary)
                if str(response['data']['1']['level']['value']) == 'True':
                    break

                time.sleep(0.01)

def get_temp(device_key):
    all_devices=get_all_devices()
    for instance in all_devices[device_key]['instances']:
        if switch_binary in all_devices[device_key]['instances'][instance]['commandClasses']:
            set_value(device_key, instance, 255)
        if sensor_binary in all_devices[device_key]['instances'][instance]['commandClasses']:
            valori = get_values(device_key, instance, sensor_multi)
            return valori['data']['1']['val']['value']

def get_lum(device_key):
    all_devices=get_all_devices()
    for instance in all_devices[device_key]['instances']:
        if switch_binary in all_devices[device_key]['instances'][instance]['commandClasses']:
            set_value(device_key, instance, 255)
        if sensor_binary in all_devices[device_key]['instances'][instance]['commandClasses']:
            valori = get_values(device_key, instance, sensor_multi)
            return valori['data']['3']['val']['value']


def get_umi(device_key):
    all_devices=get_all_devices()
    for instance in all_devices[device_key]['instances']:
        if switch_binary in all_devices[device_key]['instances'][instance]['commandClasses']:
            set_value(device_key, instance, 255)
        if sensor_binary in all_devices[device_key]['instances'][instance]['commandClasses']:
            valori = get_values(device_key, instance, sensor_multi)
            return valori['data']['5']['val']['value']

if __name__ == '__main__':
    wait_binary('2')