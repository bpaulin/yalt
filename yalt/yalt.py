"""mqtt translator between technical and waf-full topics."""
import logging
import paho.mqtt.client as mqtt
import json

import load_config
topics_config = {
    # state
    "bticino/1/02": "home/living/light/ceiling",
    "bticino/1/01": "home/living/light/wall",
    # set
    "home/living/light/ceiling/set": "bticino/1/02/set",
    "home/living/light/wall/set": "bticino/1/01/set"
}


class Yalt:
    def __init__(self, broker_ip):
        self._client = mqtt.Client("Yalt")
        self._client.connect(broker_ip)
        self._topics = {}
        self._logger = None

    def run(self):
        self._client.on_log = self.log_callback
        self._client.on_connect = self.on_connect
        self._client.on_message = self.on_message
        self._client.loop_forever()

    def enable_logger(self, logger=None):
        if not logger:
            if self._logger:
                return
            logger = logging.getLogger(__name__)
        self._logger = logger

    def on_connect(self, client, userdata, flags, rc):
        """Subscribe to right topic."""
        client.subscribe('mapping')

    def on_message(self, client, userdata, msg):
        """Translate topic when a message is received."""
        if msg.topic == 'mapping':
            for topic in self._topics.keys():
                client.unsubscribe(topic)
            self._topics = json.loads(msg.payload.decode())
            self._logger.info('updating topics mapping')
            client.subscribe(
                [(topic, 0) for topic in self._topics.keys()]
            )
        else:
            self._logger.info(
                'translating ' + msg.topic + ' to topic ' + self._topics[msg.topic]
            )
            client.publish(
                self._topics[msg.topic], msg.payload, msg.qos, msg.retain
            )

    def log_callback(self, client, userdata, level, buf):
        """Log when mqtt receive or post a message."""
        self._logger.log(mqtt.LOGGING_LEVEL[level], buf)


if __name__ == '__main__':
    """Launch mqtt client to publish and subscribe."""
    logYarn = logging.getLogger(__name__)
    logYarn.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    ch.setFormatter(formatter)
    logYarn.addHandler(ch)

    y = Yalt("localhost")
    y.enable_logger(None)
    y.run()
