from socket import *
import json
import concurrent.futures
import threading
import asyncio

async def __init__(self) -> None:
        # Eigenen Server starten
        HOST = "127.0.0.1"
        PORT = 7777
        server = await asyncio.start_server(self.handle_prev_neighbor, HOST, PORT)
        print(f"Lausche auf {PORT}")

        # Mit Nachbarn verbinden
        HOST_NEIGHBOR = "127.0.0.1"
        PORT_NEIGHBOR = 7778
        connection_neighbor = asyncio.create_task(self.connectToNeighbour(HOST_NEIGHBOR, PORT_NEIGHBOR))

        # Mit Server (Verteiler) verbinden
        HOST_SERVER = "127.0.0.1"
        PORT_SERVER = 7779
        connection_server = asyncio.create_task(self.connectToServer(HOST_SERVER, PORT_SERVER))



async def handle_prev_neighbor(self, reader, writer):
        # Nimm Daten vom vorherigen Nachbarn entgegen
        while True:
            data = await reader.readline()
            if not data:
                break
            self.prev_value = data
            print("Vom vorherigen Nachbarn:", data.decode().strip())

async def connectToNeighbor(self, host, port):
    # Verbinde dich zum nächsten Nachbarn
    self.next_reader, self.next_writer = await asyncio.open_connection(host, port)
    print("Verbunden mit nächstem Nachbarn")
     
async def connectToServer(self, host, port):
    # Verbinde dich zum Server
    self.next_reader, self.next_writer = await asyncio.open_connection(host, port)
    print("Verbunden mit Server")


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

