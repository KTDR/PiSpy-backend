from lomond import WebSocket
from lomond.persist import persist
import queue


class S:
    def __init__(self, path, send_queue, recieve_queue):
        self.binded = None
        self.sendQueue = send_queue
        self.receiveQueue = recieve_queue
        self.websocket = WebSocket(path)
        self.run()

    def run(self):
        for event in persist(self.websocket, poll=1):
            while not self.sendQueue.empty():
                self.websocket.send_json(self.sendQueue.get())
            if event.name == 'poll':
                self.websocket.send_ping()
            elif event.name == 'text':
                self.receiveQueue.put(event.text)
