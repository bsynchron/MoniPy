from influxdb import InfluxDBClient
import yaml, datetime, socket, json

clientSet = False
hostname = socket.gethostname()

def setConf(conf):
    #check if timeseries is enabled
    if conf['timeseries']['alarming'] == True or conf['timeseries']['logging'] == True:
        #load gloabl variable
        global cfg
        #set global cfg
        cfg = conf
    else:
        print("Timeseries is disabled! -> config.yml")
        return False


def connectToDB():
    #load global variables
    global clientSet
    global dbClient
    #connect to database
    dbClient = InfluxDBClient(host=cfg['db']['host'], port=cfg['db']['port'], username=cfg['db']['username'], password=cfg['db']['password'])
    #save connection state
    clientSet = True
    #create / switch to database
    dbClient.create_database(cfg['db']['database'])
    dbClient.switch_database(cfg['db']['database'])

#unused
def createDB(database):
    dbClient.create_database(database)

def insertData(data, stat=None):
    #init json data as string
    json_data=''
    #get timestamp
    timestamp = datetime.datetime.now()
    #build json structure for single stat
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
        #get last stat in dict
        keys = []
        for key in data:
            keys += [key]
        #build json array for multiple stats
        json_data='['
        for i in data:
            json_data+= '{'
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
    #convert to json object
    json_data = json.loads(json_data)
    print(json_data)

    #check if connected to database / connect to database
    if clientSet == True:
        dbClient.write_points(json_data)
    else:
        connectToDB()
        dbClient.write_points(json_data)
