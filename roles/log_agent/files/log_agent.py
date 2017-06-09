#!/usr/bin/python
import kafka
import os
import time
import json
import socket
import yaml

kafka_config = {'broker_url': '192.168.37.10:9092', 'topic': 'test_log'}
log_names = ['systema.log', 'test.log']
start_seek = 0
config_path = 'config.yaml'


class ConfiguratorActor(object):
    default_params = {'kafka': {'topic': 'test_log', 'broker_url': '192.168.37.10:9092'}, 'log': {'paths': []},
                      'system': {'sleep_time': 1, 'pid_file': "PIDFILE", 'position_filename': 'logs_positions.tmp'}}

    def __init__(self, config_file='config.yaml'):
        self.update_config(self.default_params)
        self.config_file = config_file
        self.update_config(self.read_config())

    def read_config(self):
        conf = file(self.config_file)
        result = yaml.load(conf)
        return result

    def update_config(self, input_dict):
        for x in input_dict:
            setattr(self, x, input_dict[x])


class LogImporter(object):
    def __init__(self, log_file_names=[], positions_filename="logs_positions.tmp"):
        self.log_files_names = log_file_names
        self.descriptors = {}
        self.update_descriptors()
        self.positions_filename = positions_filename
        if os.path.exists(os.path.expanduser(self.positions_filename)):
            self.positions_file = file(self.positions_filename, 'r+')
            self.update_read_positions(self.read_position_file())
        else:
            self.positions_file = file(self.positions_filename, 'w+')

    def get_read_positions(self):
        return {x: self.descriptors[x].tell() for x in self.descriptors.keys()}

    def read_position_file(self):
        self.positions_file.seek(0)
        return json.load(self.positions_file)

    def write_position_file(self):
        self.positions_file.seek(0)
        self.positions_file.write(json.dumps(self.get_read_positions()))
        self.positions_file.close()

    def update_read_positions(self, position_dic):
        for key in position_dic:
            if key in self.descriptors:
                self.descriptors[key].seek(int(position_dic[key]))

    def update_descriptors(self):
        for file_name in self.log_files_names:
            if file_name not in self.descriptors:
                if os.path.exists(os.path.expanduser(file_name)):
                    self.descriptors[file_name] = file(file_name, 'r')

    def read_files(self):
        result = {}
        for key in self.descriptors:
            result[key] = [x.replace('\n', '') for x in self.descriptors[key].readlines()]
        return result

    def close_files(self):
        closer = lambda x: x.close()
        for key in self.descriptors:
            closer(self.descriptors[key])


class KafkaActor(object):
    def __init__(self, **kwargs):
        self.kafka_config = {'broker_url': '127.0.0.1:9092', 'topic': 'test_log', 'key': None, 'partition': 0}
        self.update_kafka_config(kwargs)
        self.kafka_prod = kafka.KafkaProducer(bootstrap_servers=self.kafka_config['broker_url'])

    def update_kafka_config(self, user_configs):
        for key in user_configs:
            self.kafka_config[key] = user_configs[key]

    def write(self, message, topic=None, key=None, partition=None):
        if topic is None:
            topic = self.kafka_config['topic']
        if key is None:
            key = self.kafka_config['key']
        if partition is None:
            partition = self.kafka_config['partition']
        self.kafka_prod.send(topic, message, key=key, partition=int(partition))


conf = ConfiguratorActor()
input_logs = LogImporter(conf.log['paths'], positions_filename=conf.system['position_filename'])
kaf = KafkaActor(**conf.kafka)
play = True

try:
    while play:
        input_logs.update_descriptors()
        read_result = input_logs.read_files()
        for file_name in read_result:
            if len(read_result[file_name]) > 0:
                print "[DEBUG] Changing topic to %s" % socket.gethostname().lower()
                kaf.kafka_config['topic'] = socket.gethostname()
                print "[DEBUG] Adding key %s" % file_name
                kaf.kafka_config['key'] = file_name
                print "[DEBUG] Setting partition %s" % input_logs.log_files_names.index(file_name)
                kaf.kafka_config['partition'] = input_logs.log_files_names.index(file_name)
                map(kaf.write, read_result[file_name])
        time.sleep(conf.system['sleep_time'])
except KeyboardInterrupt:
    print json.dumps(input_logs.get_read_positions())
finally:
    input_logs.write_position_file()
    input_logs.close_files()
