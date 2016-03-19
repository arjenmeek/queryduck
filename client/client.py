import sys

import yaml

from crunchyclient import CrunchyClient


with open('config.yml', 'r') as f:
    config = yaml.load(f.read())

client = CrunchyClient(config)
client.run(*sys.argv[1:])
