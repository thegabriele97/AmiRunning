#GLOBAL VAR FILE
from sys import argv, stderr
from cfgAPI import cfg, load_configs, save_configs

if not len(argv) > 1:
    print("Error: no config file passed as argument. Exit..", file=stderr)
    exit(0x1)

print("> cfg.py: loading global configs from %s" % (argv[1]))
global_configs = load_configs(argv[1])