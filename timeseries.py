from influxdb import InfluxDBClient
import yaml, datetime, socket, json

clientSet = False
hostname = socket.gethostname()

def setConf(conf):
    if conf['timeseries']['alarming'] == True or conf['timeseries']['logging'] == True:
        global cfg
        cfg = conf
    else:
        print("Timeseries is disabled! -> config.yml")
        return False


def connectToDB():
    global clientSet
    global dbClient
    dbClient = InfluxDBClient(host=cfg['db']['host'], port=cfg['db']['port'], username=cfg['db']['username'], password=cfg['db']['password'])
    clientSet = True
    dbClient.create_database(cfg['db']['database'])
    dbClient.switch_database(cfg['db']['database'])

def createDB(database):
    dbClient.create_database(database)

def insertData(data, stat=None):
    json_data=''
    timestamp = datetime.datetime.now()
    if stat!=None:
        json_data+= '[{'
        json_data+=f'   "measurement": "{stat}",'
        json_data+= '   "tags": {'
        json_data+=f'       "host": "{hostname}"'
        json_data+= '   },'
        json_data+=f'   "time": "{timestamp}",'
        json_data+= '   "fields": {'
        json_data+=f'       "value": "{data[stat]}",'
        json_data+=f'       "state": "ALARM"'
        json_data+= '   }'
        json_data+= '}'
        json_data+= ']'
    else:
        keys = []
        for key in data:
            keys += [key]
        for i in data:
            json_data+= '[{'
            json_data+=f'   "measurement": "{i}",'
            json_data+= '   "tags": {'
            json_data+=f'       "host": "{hostname}",'
            json_data+=f'       "state": "INFO"'
            json_data+= '   },'
            json_data+=f'   "time": "{timestamp}",'
            json_data+= '   "fields": {'
            json_data+=f'       "value": "{data[i]}",'
            json_data+=f'       "state": "INFO"'
            json_data+= '   }'
            if i == keys[-1]:
                json_data+= '}'
            else:
                json_data+= '},'
            json_data+=']'
    json_data = json.loads(json_data)
    print(json_data)
    if clientSet == True:
        dbClient.write_points(json_data)
    else:
        connectToDB()
        dbClient.write_points(json_data)
