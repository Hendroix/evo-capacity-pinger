import requests, json, sys, time
from datetime import datetime

locationURL = 'https://visits.evofitness.no/api/v1/locations?operator=5336003e-0105-4402-809f-93bf6498af34'
capacityForURL = 'https://visits.evofitness.no/api/v1/locations/{}/current'
attempts = 1
responses = []

def getArgument(argumentKey):
    args = sys.argv[1:]
    for (numb, arg) in enumerate(args):
        if arg == argumentKey and len(args) > numb + 1:
            return args[numb + 1]
        elif arg == '-h':
            return args[numb]
        
def printHelpMessage():
    print('This script allows for Pings of EVO gyms capacity checks.')
    print(' [-i] Allows a index or id to be predefined, selection is then not shown.')
    print(' [-n] Allows a name to be predfined, selection is then not shown.')
    print(' [-h] Bring up this help text.')
    

def getAllGyms():
    req = requests.get(locationURL)
    if req.status_code == 200:
        return json.loads(req.content)
        
def findSelectedGym(gyms, argumentIndex, argumentName):
    if argumentIndex is not None:
        answer = argumentIndex
    elif argumentName is not None:
        answer = argumentName
    else:
        answer = input()
        
    if answer.isnumeric() and len(gyms) >= int(answer):
        return gyms[int(answer) - 1]
    else:
        answer = answer.lower()
        for gym in gyms:
            city = gym['name'].split(" ", 1)[1].lower()
            if answer == gym['name'].lower() or answer == city:
                return gym
            elif answer == gym['id'].lower():
                return gym
    print('No gym found please try again.')
    return findSelectedGym(gyms, None, None)

def pingGym(gym, attempts):
    req = requests.get(capacityForURL.format(gym['id']))
    if req.status_code == 200:
        response = json.loads(req.content)
        print('{} - {} - {}/{} - {}%{}'.format(attempts, datetime.now().strftime('%H:%M:%S'), response['current'], response['max_capacity'], calculatePercenageCapacity(response['current'], response['max_capacity']), calculateDiff(response)))
        responses.append(response)
        attempts = attempts + 1
        time.sleep(15)
        pingGym(gym, attempts)

def calculatePercenageCapacity(current_capacity, max_capacity):
        curCap = int(current_capacity)
        maxCap = int(max_capacity)
        percentageCap = (curCap / maxCap) * 10
        return round(percentageCap, 2);
    
def calculateDiff(response):
    if len(responses) > 0:
        prevResponse = responses[len(responses) - 1]
        if int(response['current']) > prevResponse['current']:
            return ' (+)'
        elif int(response['current']) < prevResponse['current']:
            return ' (-)'
        else:
            return ''
    else:
        return ''

def main():
    argumentIndex = getArgument('-i')
    argumentName = getArgument('-n')
    if getArgument('-h') is not None:
        return printHelpMessage()
    
    gyms = getAllGyms()
    if argumentIndex is None and argumentName is None:
        print('Please choose one of the following gyms to ping, either by Index, Name or Id')
        for num, gym in enumerate(gyms, start=1):
            print('{}: {} ({})'.format(num, gym['name'], gym['id']))

    selectedGym = findSelectedGym(gyms, argumentIndex, argumentName)
    if selectedGym is not None:
        print('You selected: {}'.format(selectedGym['name']))
        pingGym(selectedGym, attempts)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)
