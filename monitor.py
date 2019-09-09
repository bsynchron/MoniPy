import psutil, alarm, yaml, json, time, os, sys

if "-h" in sys.argv:
    print("helptext")
    sys.exit(0)

#######################
#Make config avaliable in monitor and alarm
def loadConf():
    f=open("config.yml", "r")
    cfg = yaml.load(f.read(), Loader=yaml.CLoader)
    f.close()
    return cfg

def cls():os.system('cls' if os.name=='nt' else 'clear')
cfg = loadConf()
alarm.setConf(cfg)
#######################
#Get stats from host

def getStat(stat):
    #check if requested stat is enabled in config
    if stat not in cfg['modules']['enabled']:
        if stat not in cfg['modules']['disabled']:
            alarm.dprint(f"Stat: '{stat}' not found!")
            return False
        else:
            alarm.dprint(f"Stat: '{stat}' is disabled!")
            return False
    #return stat if enabled
    else:
        if stat == "cpu_stat":
            return psutil.cpu_stats()
        elif stat == "cpu_util":
            return psutil.cpu_percent()
        elif stat == "mem_stat":
            return psutil.virtual_memory()
        elif stat == "disk_IO":
            return psutil.disk_io_counters()
        elif stat == "disk_space":
            return psutil.disk_usage("C:/")[3]
        elif stat == "network_io":
            return psutil.net_io_counters()
        elif stat == "network_io":
            return psutil.net_if_addrs()
        elif stat == "processes":
            return len(psutil.pids())
        elif stat == "cpu_clock":
            return psutil.cpu_freq()

#Main loop
while True:
    if cfg['mode'] == 'cli': cls()
    alarm.dprint("#"*10)
    values = {}
    #loop over enabled modules
    for stat in cfg['modules']['enabled']:
        values[stat] = getStat(stat)
        alarm.dprint(f"Stat: {stat} / {values[stat]}")

    #pass values to alarming
    alarm.checkStat(values)
    alarm.dprint("#"*10)
    #define "framerate"
    time.sleep(1/cfg['tickrate'])
