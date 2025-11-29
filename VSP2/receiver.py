from socket import *
import json
import threading
import asyncio
import signal

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

    bytes = s.recv(4096) # receive the response
    json_data = bytes.decode()
    data = json.loads(json_data)
    prevNeighbor = data["neighbor1"]
    nextNeighbor = data["neighbor2"]
    list_numbers = data["list_numbers"]
    threads = []
    anzahl_threads = data["amount"]

    # Mein Port, für die Threads dann + i
    port = data["port"]
    for i in range(anzahl_threads):

        if i == 0 and anzahl_threads == 1:
            t = threading.Thread(target=startTask, args=(prevNeighbor, nextNeighbor, list_numbers[i], port,))
        elif i == 0:
            localNextNeighbor = "127.0.0.1", port + 1
            t = threading.Thread(target=startTask, args=(prevNeighbor, localNextNeighbor, list_numbers[i], port,))
        elif i == anzahl_threads:
            localPrevNeighbor = "127.0.0.1", port - 1
            t = threading.Thread(target=startTask, args=(localPrevNeighbor, nextNeighbor, list_numbers[i], port,))
        else:
            localNextNeighbor = ("127.0.0.1", port + 1)
            localPrevNeighbor = "127.0.0.1", port - 1
            t = threading.Thread(target=startTask, args=(localPrevNeighbor, localNextNeighbor, list_numbers[i], port,))
        threads.append(t)
        port += 1

    for t in threads:
        t.start()

    for t in threads:
        t.join()

def startTask(prevNeighbor, nextNeighbor, number, port):
    
    asyncio.run(async_main(prevNeighbor, nextNeighbor, number, port))

async def async_main(prevNeighbor, nextNeighbor, number, port):
    prevIP, prevPort = prevNeighbor
    nextIP, nextPort = nextNeighbor
    taskQue = asyncio.Queue()


    server_socket = socket(AF_INET, SOCK_STREAM)
    server_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    server_socket.bind(('127.0.0.1', port))
    server_socket.listen(2)
    server_socket.setblocking(False)

    server = asyncio.create_task(accept_clients(server_socket, taskQue))
    await asyncio.sleep(1)

    print(f"Opening Conection zu {prevIP} über Port {prevPort}")
    prevNeighborReader, prevNeighborWriter = await asyncio.open_connection(
        prevIP, prevPort)
    
    
    await asyncio.sleep(1)
    print(f"Opening Conection zu {nextIP} über Port {nextPort}")
    nextNeighborReader, nextNeighborWriter = await asyncio.open_connection(
        nextIP, nextPort)
    
    
    worker = asyncio.create_task(worker_and_sender(prevNeighborWriter, nextNeighborWriter, taskQue, number))

    await worker
    server_socket.close()

async def accept_clients(socket, taskQue):
    connection_count = 0
    while connection_count < 2:
        client_socket, address = await asyncio.get_running_loop().sock_accept(socket)
        connection_count += 1
        print(f"✅ Verbindung {connection_count}/2 von {address}")
        asyncio.create_task(handle_client(client_socket, taskQue))



async def handle_client(client_socket, taskQue):
    while True:
        data = await asyncio.get_running_loop().sock_recv(client_socket, 1024)
        if not data:
            client_socket.close()
            break
            
        await taskQue.put(int(data.decode()))

async def worker_and_sender(prevNeighborWriter, nextNeighborWriter, taskQue, M):
    message = str(M).encode()
    prevNeighborWriter.write(message)
    await prevNeighborWriter.drain()
    nextNeighborWriter.write(message)
    await nextNeighborWriter.drain()
    while True:
        y = await taskQue.get()

        if y < M:
            M = ((M - 1) % y) + 1
            message = str(M).encode()
            prevNeighborWriter.write(message)
            await prevNeighborWriter.drain()
            nextNeighborWriter.write(message)
            await nextNeighborWriter.drain()
            print(f"📨 M aktualiesiert: {M}")

signal.signal(signal.SIGINT, signal.SIG_DFL)
signal.signal(signal.SIGTERM, signal.SIG_DFL)
main()