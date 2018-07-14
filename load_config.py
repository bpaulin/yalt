import yaml


config=yaml.load(open('config.yml'))
devices = config['devices']
for room_name, room in devices.items():
    for component_name, component in room.items():
        for device_name, device in component.items():
            name ='_'.join((room_name, device_name))
            config_topic = '/'.join(('config', component_name,device['platform'],name))
            state_topic = 'devices'+'/'+room_name+'/'+component_name+'/'+device_name
            config_payload = {
                'name': name,
                'state_topic': state_topic,
                'command_topic': state_topic+'/set'
            }
            if device['platform']=='bticino':
                config_payload['payload_on']='1'
                config_payload['payload_off']='0'
            print(config_topic)
            print(config_payload)