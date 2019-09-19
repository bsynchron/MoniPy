import slack, socket

#init some variables for later use
cfg = {}
isSet = False

#load config
def setConf(conf):
    global cfg
    cfg = conf
    return True

#create the connection to slack
def setClient():
    global isSet
    global client
    if isSet == False:
        client = slack.WebClient(cfg['slack']['api-key'])
        isSet = True
        return True
    else:
        return False

#format and send the message
def sendMsg(stat, value, limit, cap):
    if cfg['slack']['enabled'] == False:
        return False
    else:
        msg = f"Alarm:\n{stat} triggered an alarm! ({value}/{limit})\nThis is a {cap} on {socket.gethostname()}"
        setClient()
        response = client.chat_postMessage(
                channel=cfg['slack']['channel'],
                text=msg)
        #make sure the message got through
        assert response["ok"]
        return True
