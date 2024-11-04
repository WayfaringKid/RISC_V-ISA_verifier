import sys
import json
import yaml
import os
import re
from glob import glob

def construct_binary_from_yaml(match, variables):
    binary_representation = match
    for var in variables:
        name = var['name']
        try:
            start, end = map(int, var['location'].split('-'))
            size = start - end + 1
            binary_representation = re.sub(r'-{' + str(size) + r'}', f"[{name}:{size}]", binary_representation, count=1)
        except:
            print(f"Warning: Skipping variable '{name}' with invalid location format: {var['location']}")
            continue
    return binary_representation

def construct_binary_from_json(fields):
    binary_representation = ''
    for field in fields:
        field_name = field['field']
        size = field['size']
        if field_name.startswith('0b'):
            binary_representation += field_name[2:]
        else:
            binary_representation += f"[{field_name}:{size}]"
    return binary_representation

def get_all_yaml_files(directory):
    yaml_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.yaml') or file.endswith('.yml'):
                yaml_files.append(os.path.join(root, file))
    return yaml_files

def process_yaml_file(yaml_file, json_instructions):
    with open(yaml_file, 'r') as f:
        yaml_data = yaml.safe_load(f)
    
    try:
        yaml_instruction_name = list(yaml_data.keys())[0]
        yaml_encoding = yaml_data[yaml_instruction_name].get('encoding')

        yaml_match = yaml_encoding['match']
        yaml_variables = yaml_encoding['variables']
    except:
        print(f"instruction '{yaml_instruction_name}' does not have variables or encoding, skipped")
        return
    
    json_instruction = next((inst for inst in json_instructions if inst['mnemonic'] == yaml_instruction_name), None)
    
    if not json_instruction:
        print(f"instruction '{yaml_instruction_name}' not found in json file")
    else:
        json_fields = json_instruction['fields']
        yaml_binary = construct_binary_from_yaml(yaml_match, yaml_variables)
        json_binary = construct_binary_from_json(json_fields)

        if yaml_binary == json_binary:
            print(f"instruction '{yaml_instruction_name}': match")
        else:
            print(f"instruction '{yaml_instruction_name}': not match.")
            print(f"YAML binary: {yaml_binary}")
            print(f"JSON binary: {json_binary}")

def main():
    yaml_directory = sys.argv[1]
    json_file = sys.argv[2]
    
    with open(json_file, 'r') as f:
        json_data = json.load(f)
    json_instructions = json_data.get('instructions', [])

    yaml_files = get_all_yaml_files(yaml_directory)
    for yaml_file in yaml_files:
        process_yaml_file(yaml_file, json_instructions)

if __name__ == "__main__":
    main()
