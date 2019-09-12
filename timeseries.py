from influxdb import InfluxDBClient
import yaml, time

clientSet = False

def setConf(conf):
    if conf['timeseries'] == False:
        print("Timeseries is disabled! -> config.yml")
        return False
    global cfg
    cfg = conf

def connectToDB():
    global clientSet
    global dbClient
    dbClient = InfluxDBClient(host=cfg['db']['host'], port=cfg['db']['port'], username=cfg['db']['username'], password=cfg['db']['password'])
    clientSet = True
    dbClient.create_database(cfg['db']['database'])
    dbClient.switch_database(cfg['db']['database'])

def createDB(database):
    dbClient.create_database(database)

def insertData(data):
    timestamp = time.time()
    json_data='['
    for i in data:
        print(i)
        #https://www.influxdata.com/blog/getting-started-python-influxdb/
        json_data+=f"{{}}"

    json_data+=']'
    if clientSet == True:
        dbClient.write_points(data)
    else:
        connectToDB()
        dbClient.write_points(data)

# f = open("config.yml", "r")
# conf = f.read()
# cfg = yaml.load(conf)
# f.close()
#
# connectToDB()
# print("Connected!")
