import smtplib, yaml, time, datetime, socket, json
import timeseries, slack_connector


times = {} #Persistent timekeeping storage

def dprint(txt):
    if cfg['mode'] == 'cli':
        print(txt)
        return True
    else:
        return False

def mailAlarm(stat, value, trigger):
    #check if alarming is enabled
    if cfg['alarming'] == False:
        return False

    #create email head + body
    header = f"Subject: Alarming for {stat}"
    body = f"- Automated Alarming -\n{stat} is higher than defined limit! ({value}/{trigger})"
    message = f"{header}\n\n{body}"

    #connect to smtp server
    s = smtplib.SMTP(cfg['smtp']['smtp_server'], cfg['smtp']['port'])
    s.starttls()
    s.login(cfg['smtp']['username'], cfg['smtp']['password'])
    s.sendmail(cfg['smtp']['username'], cfg['smtp']['mailTo'], message)

    dprint("Sent mail")

def startAlarm(stat, values, trigger_value, cap):
    if cfg['alarming'] == False:
        return False
    dprint(f"ALARM: {stat} has {values[stat]}/{trigger_value} ({cap})")
    if cfg['timeseries']['alarming'] == True:
        #insert data into influxdb
        timeseries.insertData(values, stat)
    if cfg['slack']['enabled'] == True:
        slack_connector.sendMsg(stat, values[stat], trigger_value, cap)

def setConf(conf):
    timeseries.setConf(conf)
    slack_connector.setConf(conf)
    if conf['alarming'] == False:
        print("Alarming not enabled! -> config.yml")
        return False
    global cfg
    cfg = conf

def checkStat(values):
    #check if alarming is enabled
    if cfg['alarming'] == False:
        return False
    #hard cap / loop over hard_cap in config
    for i in range(len(cfg['trigger']['hard_cap'])):
        #get first key name from dict (stat)
        stat = next(iter(cfg['trigger']['hard_cap'][i]))
        #load trigger value for alarm
        trigger_value = cfg['trigger']['hard_cap'][i]['value']
        #check if alarm is enabled
        if cfg['trigger']['hard_cap'][i][stat] == True:
            #check if stat value is higher than the trigger value
            if values[stat] > trigger_value:
                #only log if logging is enabled
                if cfg['trigger']['hard_cap'][i]['log'] == True:
                    log(time.time(), stat, values[stat], trigger_value, "ALARM")
                #send alarm to cli
                startAlarm(stat, values, trigger_value, "HARD_CAP")
                #check if mail is enabled for stat trigger
                if cfg['trigger']['hard_cap'][i]['mail'] == True:
                    mailAlarm(stat, values[stat], trigger_value)
    #soft cap / use global times (persistent storage)
    global times
    #loop over soft_cap in config
    for i in range(len(cfg['trigger']['soft_cap'])):
        #get first key name from dict (stat)
        stat = next(iter(cfg['trigger']['soft_cap'][i]))
        #load trigger value for alarm
        trigger_value = cfg['trigger']['soft_cap'][i]['value']
        #check if alarm is enabled
        if cfg['trigger']['soft_cap'][i][stat] == True:
            #check if stat value is over the trigger_value
            if values[stat] > trigger_value:
                #check if stat has an entry in times
                if stat in times:
                    dprint(f"INFO: {stat} = {values[stat]} / {trigger_value}")
                    if cfg['trigger']['soft_cap'][i]['log'] == True:
                        log(time.time(), stat, values[stat], trigger_value, "INFO")
                    #compare current time to saved timestamp + softcap_time
                    if time.time() >= (times[stat] + cfg['trigger']['soft_cap'][i]['time']):
                        startAlarm(stat, values, trigger_value, "SOFT_CAP")
                        if cfg['trigger']['soft_cap'][i]['log'] == True:
                            log(time.time(), stat, values[stat], trigger_value, "ALARM")
                        if cfg['trigger']['soft_cap'][i]['mail'] == True:
                            mailAlarm(stat, values[stat], trigger_value)
                        #remove entry from timekeeping storage (reset timer)
                        del times[stat]
                #stat not in times
                else:
                    #create entry in times (starting timestamp)
                    times[stat] = time.time()
                    dprint(f"{stat} registered in 'times'")
            #value below trigger value
            else:
                if stat in times:
                    #delete any old entry of stat
                    del times[stat]
                    dprint(f"{stat} deleted from 'times'")

def log(ts, stat, value, trigger_value, level):
    #open / create logfile
    f = open('alarm.log', 'a')
    f.write(f"{level} // {datetime.datetime.fromtimestamp(ts)} // {socket.gethostname()} // Stat: '{stat}' ({value}/{trigger_value})\n")
    f.close()
