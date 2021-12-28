import requests
import pprint



def forecode(time):
    r = requests.get('http://api.weatherapi.com/v1/forecast.json?key=c74c64ce928f48fd80d175452211812&q=78641&aqi=no&lat=30.548440&lon=-97.785090')
    save = r.json()
    fore = save['forecast']
    forelist = fore['forecastday']
    fhour = forelist[0]
    forehour = fhour["hour"]
    #pprint.pprint(forehour)
    hourcast = forehour[time]
    pprint.pprint(forehour)
    hourcon = hourcast['condition']
    weathercode = [hourcon['code'], hourcon['text']]
    return weathercode[0]
    

def forelogic(hournum):
    codenum = forecode(hournum)
    print(codenum)
    if codenum > 1009:
        if codenum > 1087:
            return "dclose"
        else:
            time.sleep(300)
            aftercode = forcode(hournum)
            if aftercode > 1087:
                return "pclose"
            elif aftercode < 1087:
                time.sleep(300)
                return "mopen"
            else:
                return "popen"
                    
    else:
        return "dopen"


      
forecode(1)
