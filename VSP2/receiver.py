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
        print("Mit Server verbunden")
        bytes = s.recv(4096) # receive the response
        json_data = bytes.decode()
        data = json.loads(json_data)
        amount = data["amount"]
        prevNeighbor = data["neighbor1"]
        nextNeighbor = data["neighbor2"]
        list_numbers = data["list_numbers"]
        print(f"Nachricht erhalten. Berechne für {list_numbers}")
        threads = []

        # Variable Anzahl an Threads
        anzahl_threads = data["amount"]
        # Mein Port, für die Threads dann + i
        port = 7778
        # Anzahl Threads starten
        for i in range(anzahl_threads):
            # Using `args` to pass positional arguments and `kwargs` for keyword arguments
            if i == 1 and anzahl_threads == 1:
                t = threading.Thread(target=startTask, args=(prevNeighbor, nextNeighbor, list_numbers[i], port), daemon=True)
            elif i == 1:
                localNextNeighbor = "127.0.0.1", port + 1
                t = threading.Thread(target=startTask, args=(prevNeighbor, localNextNeighbor, list_numbers[i], port), daemon=True)
            elif i == anzahl_threads:
                localPrevNeighbor = "127.0.0.1", port - 1
                t = threading.Thread(target=startTask, args=(localPrevNeighbor, nextNeighbor, list_numbers[i], port), daemon=True)
            else:
                localNextNeighbor = "127.0.0.1", port + 1
                localPrevNeighbor = "127.0.0.1", port - 1
                t = threading.Thread(target=startTask, args=(localPrevNeighbor, localNextNeighbor, list_numbers[i], port), daemon=True)
            threads.append(t)
            port += 1

        # Start each thread
        for t in threads:
            t.start()
        print("Alle Threads gestartet")

        # Wait for all threads to finish
        for t in threads:
            t.join()

def startTask(prevNeighbor, nextNeighbor, number, port):
    asyncio.run(async_main(prevNeighbor, nextNeighbor, number, port))

async def start_server(host, port):
    server = await asyncio.start_server(handle_neighbor, host, port)
    print(f"Lausche auf {port}")

async def connectToPrevNeighbor(host, port):
    # Verbinde dich zum nächsten Nachbarn
    prev_reader, prev_writer = await asyncio.open_connection(host, port)
    print("Verbunden mit nächstem Nachbarn")  

async def connectToNextNeighbor(host, port):
    # Verbinde dich zum nächsten Nachbarn
    next_reader, next_writer = await asyncio.open_connection(host, port)
    print("Verbunden mit nächstem Nachbarn")

async def listenToServer(reader_server):
    # Auf Nachrichten vom Server warten
    while True:
            data = await reader_server.readline()
            if not data:
                print("Verbindung vom Server getrennt")
                break
            SERVER_VALUE = int(data.decode().strip())

async def listenToPrevNeighbor(reader):
    # Auf Nachrichten vom vorherigen Nachbarn warten
    while True:
            data = await reader.readline()
            if not data:
                print("Verbindung vom Server getrennt")
                break
            SERVER_VALUE = int(data.decode().strip())

async def ggT(y, M):
    if y < M:
        M = 


async def async_main(prevNeighbor, nextNeighbor, number, port):
    M = number
    # Eigenen Server starten
    HOST, PORT = "127.0.0.1", port
    server = asyncio.create_task(start_server(HOST, PORT))
    # Mit nächstem Nachbarn verbinden
    HOST_PREV_NEIGHBOR, PORT_PREV_NEIGHBOR = prevNeighbor
    HOST_NEXT_NEIGHBOR, PORT_NEXT_NEIGHBOR = nextNeighbor

    connectionToPrevNeighbor = asyncio.create_task(connectToPrevNeighbor(HOST_PREV_NEIGHBOR, PORT_PREV_NEIGHBOR))
    connectionToNextNeighbor = asyncio.create_task(connectToNextNeighbor(HOST_NEXT_NEIGHBOR, PORT_NEXT_NEIGHBOR))

    task_listenToServer = asyncio.create_task(listenToServer(task_listenToServer))
    task_listenToPrevNeighbor = asyncio.create_task(listenToPrevNeighbor(reader=asyncio.StreamReader))
    task_listenToNext_Neigbor = asyncio.create_task(listenToNextNeigbor)
    task_ggT = asyncio.create_task(ggT(y, M))

async def handle_neighbor():
    return

main()