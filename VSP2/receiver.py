from socket import *
import json
import concurrent.futures
import threading
import asyncio

PREV_VALUE = 0
SERVER_VALUE = 0

def main() -> None:
    s = socket(AF_INET, SOCK_STREAM)
    try:
        # Zum Server (Verteiler) verbinden
        s.connect(("127.0.0.1", 7777)) # connect to server (block until accepted) 127.0.0.1 localhost
    except Exception as e:
        print(f"Error: {e}")
        exit()
    else:
        bytes = s.recv(1024) # receive the response
        json_data = bytes.decode()
        data = json.loads(json_data)
        amount = data["amount"]
        prevNeighbor = data["neighbor1"]
        nextNeighbor = data["neighbor2"]
        list_numbers = data["list_numbers"]

        # Eigenen Server starten
        HOST, PORT = "127.0.0.1", 7777
        asyncio.create_task(start_server(HOST, PORT))

        # Mit nächstem Nachbarn verbinden
        HOST_NEIGHBOR, PORT_NEIGHBOR = nextNeighbor
        connection_neighbor = asyncio.create_task(connectToNeighbor(HOST_NEIGHBOR, PORT_NEIGHBOR))

        task_listenToServer = asyncio.create_task(listenToServer(task_listenToServer))


async def start_server(host, port):
    server = await asyncio.start_server(handle_prev_neighbor, host, port)
    print(f"Lausche auf {port}")

async def listenToServer(reader_server):
    while True:
            data = await reader_server.readline()
            if not data:
                print("Verbindung vom Server getrennt")
                break
            SERVER_VALUE = int(data.decode().strip())

async def connectToNeighbor(self, host, port):
    # Verbinde dich zum nächsten Nachbarn
    self.next_reader, self.next_writer = await asyncio.open_connection(host, port)
    print("Verbunden mit nächstem Nachbarn")













async def listen(self):
    bytes = self.s.recv(1024) # receive the response
    json_data = bytes.decode()
    data = json.loads(json_data)

    # Variable Anzahl an Threads
    anzahl_threads = data["anzahl"]
    # Anzahl Threads starten
    with concurrent.futures.ThreadPoolExecutor(max_workers=anzahl_threads) as executor:
        for i in range(anzahl_threads):
            executor.submit(ggT, i)


def ggT():
    return

async def handle_prev_neighbor(self, reader, writer):
        # Nimm Daten vom vorherigen Nachbarn entgegen
        while True:
            data = await reader.readline()
            if not data:
                break
            PREV_VALUE = data
            print("Vom vorherigen Nachbarn:", data.decode().strip())


