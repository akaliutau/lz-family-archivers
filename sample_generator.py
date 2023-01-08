import argparse
import datetime
import json
import random
from typing import List, Dict

from entropy_libs import EntropyRecorder


class RandomGenerators:

    def __init__(self, enumerations: Dict[str, List], schema: dict):
        self.enumerations = enumerations
        self.schema = schema
        self.random_generators = dict()
        self.random_generators['FLOAT64'] = lambda: random.uniform(-10.0, 10.0)
        self.random_generators['INTEGER'] = lambda: random.randint(0, 1000000)
        self.random_generators['ENUM'] = lambda enum_type: random.choice(self.enumerations[enum_type])

    def set_random_values_in_json_line(self, rec: dict, fields: list) -> dict:
        for field in fields:
            ftype = self.schema[field]
            if ftype == 'ENUM':
                rec[field] = self.random_generators[ftype](field)
            else:
                rec[field] = self.random_generators[ftype]()
        return rec

    def set_random_values_in_str_line(self, rec: str, fields: list) -> str:
        values = dict()
        self.set_random_values_in_json_line(values, fields)
        return rec.format_map(values)


class LoglineProducer:
    TEMPLATE = '{timestamp} temperature: {temperature}'

    def __init__(self, log_type: str):
        self.log_type = log_type
        if log_type == 'JSON':
            self.provider = lambda l: json.dumps(l)
        if log_type == 'TXT':
            self.provider = lambda l: self.TEMPLATE.format_map(l)

    def to_string(self, rec: dict) -> str:
        return self.provider(rec)


def iso_time(t: datetime) -> str:
    return t.isoformat('T', 'milliseconds') + 'Z'


enumerators = {
    'country': [
        'Australia',
        'Canada',
        'United Kingdom',
        'United States'
    ],
    'type': [
        'global'
    ]
}

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generates sample files (simulates log lines or json files')
    parser.add_argument('-o', '--out', help='output file with data', required=True)
    parser.add_argument('-s', '--schema', help='path to schema', required=True)
    parser.add_argument('-l', '--lines', help='number of lines', default=1000, required=False)
    parser.add_argument('-t', '--type', help='the type of log', default='JSON', choices=['JSON', 'TXT'], required=False)

    args = vars(parser.parse_args())

    with open(args.get('schema')) as fp:
        schema_fields = json.load(fp)
    parsed_schema = dict()
    for field_descriptor in schema_fields:
        parsed_schema[field_descriptor['name']] = field_descriptor['type']

    generators = RandomGenerators(
        enumerations=enumerators,
        schema=parsed_schema
    )
    entropy_recorder = EntropyRecorder()
    logline_producer = LoglineProducer(args.get('type'))

    t = datetime.datetime.now()
    step_ms = 73
    json_fields = ['temperature', 'rad_direct_horizontal', 'rad_diffuse_horizontal', 'type', 'country', 'hashcode']
    with open(args.get('out'), 'wt') as out:
        for i in range(int(args.get('lines'))):
            r = dict()
            r['timestamp'] = iso_time(t)
            r = generators.set_random_values_in_json_line(rec=r, fields=json_fields)
            t = t + datetime.timedelta(milliseconds=step_ms)
            line = logline_producer.to_string(r)
            out.write(entropy_recorder.add_sample(line) + '\n')

    print('entropy %s' % entropy_recorder.entropy_shannon())
