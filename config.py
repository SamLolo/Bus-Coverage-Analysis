import tomllib

with open('config.toml', 'rb') as fp:
    CONFIG = tomllib.load(fp)