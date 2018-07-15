import yaml
import json
import paho.mqtt.client as mqtt

mapping = {}
config = yaml.load(open('config.yml'))

client = mqtt.Client("Yalt")
client.connect('localhost')
client.loop_start()

devices = config['devices']
for room_name, room in devices.items():
    for component_name, component in room.items():
        for device_name, device in component.items():
            name = '_'.join((room_name, device_name))
            config_topic = '/'.join(('config', component_name, device['platform'], name))
            state_topic = '/'.join(('rooms', room_name, component_name, device_name))
            config_payload = {
                'name': name,
                'state_topic': state_topic,
                'command_topic': state_topic+'/set'
            }
            if device['platform'] == 'bticino':
                config_payload['payload_on'] = '1'
                config_payload['payload_off'] = '0'
                if component_name == 'light':
                    tech_topic = '/'.join(('bticino', '1', device['id']))
            mapping[tech_topic] = state_topic
            mapping[state_topic+'/set'] = tech_topic+'/set'
            client.publish(config_topic, json.dumps(config_payload), 0, True).wait_for_publish()

client.publish('mapping', json.dumps(mapping), 0, True).wait_for_publish()
client.disconnect()