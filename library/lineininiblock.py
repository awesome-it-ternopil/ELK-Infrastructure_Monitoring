#!/usr/bin/python
import ConfigParser
import shlex
import json
import sys
import re
import shutil
import time
class Read_input(object):
    def __init__(self):
        self.arguments = self.read_arg()

    def read_arg(self):
        result_dict = {}
        input_file=sys.argv[1]
        # input_file = 'line.conf'
        input_params = file(input_file).read()
        arguments = shlex.split(input_params)
        for arg in arguments:
            if '=' in arg:
                (key, value) = arg.split('=')
                result_dict[key] = value.replace('\'', '')
                if result_dict[key][0]=='[' and result_dict[key][-1]==']':
                    result_dict[key]=result_dict[key].replace('[', '').replace(']', '').split(',')
        return result_dict

class Ini_configure(object):
    def __init__(self, options):
        self.ansible_params=options
        self.input_file_name=self.ansible_params['dest']
        self.input_file=file(self.input_file_name, 'r+')
        self.parser = ConfigParser.ConfigParser()
        self.parser.readfp(self.input_file)

    def get_matched_blocks(self):
        result=[]
        for block_name in self.parser.sections():
            if re.search(block_name, self.ansible_params['block']) is not None:
                result.append(block_name)
        return result

    def get_matched_options(self, block):
        result=[]
        for option in self.parser.options(block):
            if re.search(option, self.ansible_params['option']) is not None:
                result.append(option)
        return result

    def backup_maker(self):
        shutil.copy(self.input_file_name, '%s_%s.backup' % (self.input_file_name,int(time.time())))

    def space_cleaner(self):
        good_data=self.input_file.read()
        good_data=good_data.replace(' = ', '=')
        self.input_file.write(good_data)

    def clean_file(self):
        pointer=0
        self.input_file.seek(pointer)
        lines=self.input_file.read()
        if lines.find('[') >=0:
            pointer=lines.find('[')
        self.input_file.seek(pointer)
        self.input_file.truncate()

    def worker(self):
        self.backup_maker()
        result={}
        if self.ansible_params['block'] in self.parser.sections():
            self.parser.set(self.ansible_params['block'], self.ansible_params['option'], self.ansible_params['value'])
            result= {'changed': True,
                    'block_created': False,
                    'block': self.ansible_params['block'],
                    'option': self.ansible_params['option'],
                    'value': self.ansible_params['value']}
        else:
            self.parser.add_section(self.ansible_params['block'])
            self.parser.set(self.ansible_params['block'], self.ansible_params['option'], self.ansible_params['value'])
            result= {'changed': True,
                    'block_created': True,
                    'block': self.ansible_params['block'],
                    'option': self.ansible_params['option'],
                    'value': self.ansible_params['value']}
        self.clean_file()
        self.parser.write(self.input_file)
        self.space_cleaner()
        return result

params=Read_input()
if 'dest' in params.arguments and 'state' in params.arguments and 'block' in params.arguments and 'option' in params.arguments and 'value' in params.arguments:
    ini_engine = Ini_configure(params.arguments)
    if params.arguments['state'] == 'present':
        if params.arguments['block'] in ini_engine.parser.sections() and params.arguments['option'] in ini_engine.parser.options(params.arguments['block']) and ini_engine.parser.get(params.arguments['block'], params.arguments['option'])==params.arguments['value']:
            print json.dumps({'filed': False, 'changed': False})
        else:
            print json.dumps(ini_engine.worker())
            ini_engine.input_file.close()
            sys.exit(0)
    elif params.arguments['state'] == 'absent':
        print json.dumps({
            'filed': True,
            'msg': "[ERROR] Temporary unsupported state",
        })
        sys.exit(1)

    else:
        print json.dumps({
            'filed': True,
            'msg': "[ERROR] Unknown state",
        })
        sys.exit(1)

else:
    print json.dumps({
        'filed': True,
        'msg': "[ERROR] Not all configuration options (dest, block, option, value) present",
    })
    sys.exit(1)

