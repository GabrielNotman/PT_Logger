import datetime
import json
import requests
import sys
import time

def checkJson(jsonData, keySet):
    result = True;
    for key in keySet:
        if not key in jsonData:
            result = False
    return result

def error(message):
    print(datetime.datetime.now().strftime("%Y-%m-%d,%H:%M:%S") + ", Error: " + message)
    sys.exit()
    return

def getData(config):
    #start a session
    session = requests.Session()

    #get login cookie
    try:
        url = "http://" + config['host'] + ":" + config['port'] + "/login"
        headers = { 'content-type' : 'application/x-www-form-urlencoded' }
        data = "password=" + config['password']
        loginRequest = session.post(url,  headers = headers, data = data)
    except:
        error("Cannot load data, possible password or network issue")        

    #get data
    try:
        url = "http://" + config['host'] + ":" + config['port'] + "/monitoring/data"
        data = session.get(url)
    except:
        error("Cannot load data, possible password or network issue")   
    
    #parse json response
    try:
        jsonData = json.loads(data.text)
    except ValueError, e:
        error("Cannot load data, possible password or network issue")

    #check for the required data
    expectedKeys = { 'BTCUSDTPrice', 'balance', 'totalPairsCurrentValue', 'totalPairsRealCost', 
        'totalDCACurrentValue', 'totalDCARealCost', 'totalProfitYesterday', 'timeZoneOffset' }
    if not checkJson(jsonData, expectedKeys):
        error("Cannot load data, possible password or network issue")

    data = {}
    data['BTCPrice'] = jsonData['BTCUSDTPrice']
    data['balance'] = jsonData['balance']
    data['pairsBalance'] = jsonData['totalPairsCurrentValue']
    data['pairsCost'] = jsonData['totalPairsRealCost']
    data['pairsDiff'] = data['pairsBalance'] - data['pairsCost']
    data['dcaBalance'] = jsonData['totalDCACurrentValue']
    data['dcaCost'] = jsonData['totalDCARealCost']
    data['dcaDiff'] = data['dcaBalance'] - data['dcaCost']
    data['totalValue'] = data['balance'] + data['pairsBalance'] + data['dcaBalance'];
    data['totalDiff'] = data['pairsDiff'] + data['dcaDiff']

    data['dailyProfit'] = jsonData['totalProfitYesterday']

    #count sales from yesterday
    data['dailySales'] = 0
    yesterday = datetime.date.today() - datetime.timedelta(days=1)
    offset = time.strptime(jsonData['timeZoneOffset'], "+%H:%M")

    for sellItem in jsonData['sellLogData']:
        saleTime = datetime.datetime(sellItem['soldDate']['date']['year'], 
            sellItem['soldDate']['date']['month'], sellItem['soldDate']['date']['day'], 
            sellItem['soldDate']['time']['hour'], sellItem['soldDate']['time']['minute'], 
            sellItem['soldDate']['time']['second']) + datetime.timedelta(hours=offset.tm_hour, minutes=offset.tm_min);
        if saleTime.date() == yesterday:
            data['dailySales'] += 1
    return data

def loadConfig():
    try:
        config = json.load(open('config.json'))
    except ValueError, e:
        error("Cannot load config data, check config.json")

    #check for the required data
    expectedKeys = { 'host', 'port', 'password', 'writeApiKey', 'maxAttempts' }
    if not checkJson(config, expectedKeys):
        error("Cannot load config data, check config.json")
    return config

def printData(data):
    print (datetime.datetime.now().strftime("%Y-%m-%d,%H:%M:%S") + "," + "%.0f" % data['BTCPrice'] + "," + "%.8f" % data['balance'] + "," 
        + "%.8f" % data['pairsBalance'] + "," + "%.8f" % data['pairsCost'] + "," + "%.8f" % data['pairsDiff'] + ","
        + "%.8f" % data['dcaBalance'] + "," + "%.8f" % data['dcaCost'] + "," + "%.8f" % data['dcaDiff'] + ","
        + "%.8f" % data['totalValue'] + "," + "%.8f" % data['totalDiff'] + "," + "%.8f" % data['dailyProfit'] + "," + str(data['dailySales']))
    return

def sendDataThingSpeak(config, data):
    parameters = {}
    parameters['key'] = config['writeApiKey']
    parameters['field1'] = data['BTCPrice']
    parameters['field2'] = "%.8f" % data['totalValue']
    parameters['field3'] = "%.8f" % data['totalDiff']    
    parameters['field4'] = "%.8f" % data['dailyProfit']
    parameters['field5'] = data['dailySales']

    attempts = 1
    success = False
    submit = requests.get("http://api.thingspeak.com/update", params = parameters)

    while not success and attempts < int(config['maxAttempts']):
        submit = requests.get("http://api.thingspeak.com/update", params = parameters)
        success = submit.status_code == requests.codes.ok
        attempts += 1
         
    if not success:
        error("Failure to send data to ThingSpeak, check WriteApiKey")
    return

#main
config = loadConfig()
data = getData(config)
printData(data)
sendDataThingSpeak(config, data)
