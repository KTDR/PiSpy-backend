import os, json, base64, datetime
from datetime import datetime

# CyPi - Team 4 - Leon Zhu
# Functions for executing websocket commands

# Directories
knownNames = r'C:\Users\amana\OneDrive\Development\CyPi\Backend\FaceRec\KnownFaces\KnownNames.txt'
knownFaces = r'C:\Users\amana\OneDrive\Development\CyPi\Backend\FaceRec\KnownFaces'
eventsDir = r'C:\Users\amana\OneDrive\Development\CyPi\Backend\FaceRec\Events'

# CyPi - Team 4 - Joshua Bush
# Routing requests to their designated functions.

import asyncio
from FaceRec import websocket2
import threading
import queue

# CyPi - Team 4 - Joshua Bush
# Routing requests to their designated functions.



def get_input(send_q, rec_q, kb_q):
    while True:
        request = ''
        if not kb_q.empty():
            request = kb_q.get()

        if not rec_q.empty():
            request = rec_q.get()

        if request != '':
            print('\nReceived request! content:[' + request + ']')
            request.strip()
            try:
                print("attempting deserialize")
                request2 = json.loads(request)
                print('request deserialized')
                print('Request is ' + str(request2))
                command = request2['command']
                print('Command is ' + command)
                replying = request2['replying']
                print('Replying is ' + str(replying))
                payload = request2['payload']
                print('Payload is' + str(payload))

            except Exception as e:
                print('failed to load request object')
                print(e)
                request = ''
                command = ''


            if command == "TEST":
                print('test command received')

            elif command == "ADD_USER":
                ADD_USER(payload)

            elif command == "DELETE_USER":
                DELETE_USER(payload)

            elif command == "UPDATE_USER":
                print("Calling updateUser()")

            elif command == "DELETE_ALL_USERS":
                print("Calling DELETE_ALL_USERS()")
                DELETE_ALL_USERS()
                # return (commands.GET_LOG_JSON())

            elif command == "GET_USERLIST":
                # sendObject = create_wrapper(command)
                # sendObject['replying'] = True
                # sendObject['payload'] = GET_USERLIST()
                request2['replying'] = True
                request2['payload'] = GET_USERLIST()
                send_q.put(request2)
                print('added userlist to send queue')

            elif command == "GET_UPTIME":
                print("Calling getUptime")

            elif command == "EVENT_UNAUTHORIZED_USER":
                print("Calling eventUnauthorizedUser")

            elif command == "EVENT_UNLOCK_REQUEST":
                print("Calling eventUnlockRequest")

            # If the request does not match any of our valid requests.
            else:
                print('{' + request, "is not a valid request.}")


def websocket_thread(q, r):
    global websocket
    websocket = websocket2.S('wss://ltasus.asuscomm.com:225', q, r)


def get_input_kb(kb_q):
    while True:
        kb_q.put(input('Type your request: '))


# Add specified user to authorized users
def ADD_USER(payload):
    try:
        nameCheck = '%s\n' % payload['name']
        name = payload['name']
        imageEncode = payload['image']

        # Check to see if user exists, then add
        with open(knownNames, 'r') as txtFile:
            allLines = txtFile.readlines()

        if name not in allLines:
            with open(knownNames, 'a') as txtFile:
                txtFile.write('\n' + name)

            # Decode image from base64 string
            with open(r'C:\Users\amana\OneDrive\Development\CyPi\Backend\FaceRec\KnownFaces\%s.jpg' % name, "wb") as image_file:
                print('file written')
                image_file.write(base64.b64decode(imageEncode))
    except Exception as e:
        print('failed to add user')
        print(e)



# Delete specified user from authorized users
def DELETE_USER(payload):
    try:
        name = '%s' % payload['name']

        # Check to see if user exists, then remove
        with open(knownNames, 'r') as txtFile:
            allLines = txtFile.readlines()

        if name in allLines:
            with open(knownNames, 'w') as txtFile:
                for each in allLines:
                    if each != (name):
                        txtFile.write(each)

            imageFile = '%s\%s.jpg' % (knownFaces, payload['name'])
            os.remove(imageFile)
    except Exception as e:
        print('failed to delete user')
        print(e)
    print('deleted file?')
# Delete all authorized users (by deleting all photos and wiping text file)
def DELETE_ALL_USERS():

    for each in os.scandir(knownFaces):
        os.remove(each)

    file = open(knownNames, 'w')
    file.close()


# Return JSON object of a dictionary of all log data
def GET_LOG_JSON():

    # Dictionary of all log info
    logDic = {}

    # Go through all events folders, for each folder: create a key-value pair in logDic with all logs lines in text file
    for folder in os.scandir(eventsDir):
        eventsTxt = r'%s\%s\%s_Events.txt' % (eventsDir, folder.name, folder.name)

        with open(eventsTxt, 'r') as txtFile:
            allLines = txtFile.readlines()
            strippedLines = []

            for each in allLines:
                strippedLines.append(each.strip())

            logDic[folder.name] = strippedLines               

    # Convert logDic to JSON and return
    jsonDump = json.dumps(logDic)
    return jsonDump


# Return JSON object of a dictionary of all authorized users
def GET_USERLIST():
    userObjects = {}
    try:
        with open(knownNames, 'r') as txtFile:
            allLines = txtFile.readlines()
            for name in allLines:
                user = {}
                name = name.strip()
                user['name'] = name
                print(name)
                with open(r'C:\Users\amana\OneDrive\Development\CyPi\Backend\FaceRec\KnownFaces\%s.jpg' % name, "rb") as image_file:
                    print('test')
                    user['image'] = base64.b64encode(image_file.read()).decode('utf8')
                userObjects[name] = user
    except Exception as e:
        print('failed to get user list')
        print(e)
    finally:
        return userObjects


    allUsers = {}
    allNames = []

    # # Get all user's names and create dictionary with them in 'names'
    # with open(knownNames, 'r') as txtFile:
    #     allLines = txtFile.readlines()
    #
    #     for each in allLines:
    #         allNames.append(each.strip())
    #
    # allUsers['names'] = allNames
    # jsonDump = json.dumps(allUsers)
    # return jsonDump


def create_wrapper(command='unspecified'):
    blank_wrapper = {
        "command": command,
        "passkey": "",
        "replying": False,
        "payload": {}   # empty dictionary object
    }
    return blank_wrapper

if __name__ == "__main__":
    websocket = None
    send_queue = queue.Queue()  # Shared queue for data that needs to be sent
    receive_queue = queue.Queue()  # Shared queue for data that needs to be processed
    keyboard_queue = queue.Queue()  # Shared queue for input from keyboard
    t1 = threading.Thread(target=websocket_thread, args=(send_queue, receive_queue))
    t2 = threading.Thread(target=get_input, args=(send_queue, receive_queue, keyboard_queue))
    t3 = threading.Thread(target=get_input_kb, args=(keyboard_queue,))
    t1.start()
    t2.start()
    t3.start()
    t1.join()
    t2.join()
    t3.join()
    NOT_IMPLEMENTED = "This function is not yet available."
