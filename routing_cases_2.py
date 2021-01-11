# CyPi - Team 4 - Joshua Bush
# Routing requests to their designated functions.

#import commands
import asyncio
from FaceRec import websocket2
import threading
import queue


def get_input(send_q, rec_q, kb_q):

    while True:
        request = ''
        if not kb_q.empty():
            request = kb_q.get()

        if not rec_q.empty():
            request = rec_q.get()

        if request != '':
            print('\nReceived request! content:[' + request + ']')
            if request == "TEST":
                send_q.put('queued')

            elif request == "ADD_USER":
                # addUser() is a function in Leon's code
                print("Calling ADD_USER()")
                # The parameter for ADD_USER is the payload
                # commands.ADD_USER(payload)
                # then add the wrapped ADD_USER object to the send queue


            elif request == "DELETE_USER":
                # deleteUser()
                print("Calling DELETE_USER()")
                # The parameter for DELETE_USER is the payload
                # commands.DELETE_USER(payload)

            elif request == "UPDATE_USER":
                print("Calling updateUser()")

            elif request == "DELETE_ALL_USERS":
                print("Calling DELETE_ALL_USERS()")
                # return (commands.GET_LOG_JSON())

            elif request == "GET_USERLIST":
                print("Returning GET_USERLIST()")
                # return (commands.GET_USERLIST())

            elif request == "GET_UPTIME":
                print("Calling getUptime")

            elif request == "EVENT_UNAUTHORIZED_USER":
                print("Calling eventUnauthorizedUser")

            elif request == "EVENT_UNLOCK_REQUEST":
                print("Calling eventUnlockRequest")


            # These functions are not yet implemented
            elif request == "WEBCAM_STREAM_FRAME":
                print(NOT_IMPLEMENTED)
            elif request == "ADD_DOCUMENT":
                print(NOT_IMPLEMENTED)
            elif request == "DELETE_DOCUMENT":
                print(NOT_IMPLEMENTED)
            elif request == "GET_DOCUMENT":
                print(NOT_IMPLEMENTED)
            elif request == "GET_CAM_STREAM":
                print(NOT_IMPLEMENTED)

            # If the request does not match any of our valid requests.
            else:
                print('{' + request, "is not a valid request.}")

def websocket_thread(q, r):
    global websocket
    websocket = websocket2.S('wss://ltasus.asuscomm.com:225', q, r)

def get_input_kb(kb_q):
    while True:
        kb_q.put(input('Type your request: '))

if __name__ == "__main__":
    websocket = None
    send_queue = queue.Queue() #Shared queue for data that needs to be sent
    receive_queue = queue.Queue() # Shared queue for data that needs to be processed
    keyboard_queue = queue.Queue()  # Shared queue for input from keyboard
    t1 = threading.Thread(target=websocket_thread, args=(send_queue, receive_queue))
    t2 = threading.Thread(target=get_input, args=(send_queue, receive_queue, keyboard_queue))
    t3 = threading.Thread(target=get_input_kb, args=(keyboard_queue,))
    t4 = threading.Thread()
    t1.start()
    t2.start()
    t3.start()
    t1.join()
    t2.join()
    t3.join()
    NOT_IMPLEMENTED = "This function is not yet available."