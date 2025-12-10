from socket import *
import json
import threading
import asyncio
import signal
import time

PREV_VALUE = 0
SERVER_VALUE = 0

serverIp = "192.168.43.50"
clientIP = "192.168.43.50"

def main() -> None:
    s = socket(AF_INET, SOCK_STREAM)
    try:
        # Zum Server (Verteiler) verbinden
        s.connect((serverIp, 7777)) # connect to server (block until accepted) 127.0.0.1 localhost
    except Exception as e:
        print(f"Error: {e}")
        exit()

    while True:
        bytes = s.recv(4096) 
        json_data = bytes.decode()
        data = json.loads(json_data)
        prevNeighbor = data["neighbor1"]
        nextNeighbor = data["neighbor2"]
        list_numbers = data["list_numbers"]
        threads = []
        anzahl_threads = data["amount"]

        threadSockets = []
        threadPorts = []
        port = data["port"]
        for i in range(anzahl_threads):

            if (i == 0) and (anzahl_threads == 1):
                t = threading.Thread(target=startTask, args=(prevNeighbor, nextNeighbor, list_numbers[i], port,))
            elif i == 0:
                localNextNeighbor = (clientIP, port + 1)
                t = threading.Thread(target=startTask, args=(prevNeighbor, localNextNeighbor, list_numbers[i], port,))
            elif i == (anzahl_threads - 1):
                localPrevNeighbor = (clientIP, port - 1)
                t = threading.Thread(target=startTask, args=(localPrevNeighbor, nextNeighbor, list_numbers[i], port,))
            else:
                localNextNeighbor = (clientIP, port + 1)
                localPrevNeighbor = (clientIP, port - 1)
                t = threading.Thread(target=startTask, args=(localPrevNeighbor, localNextNeighbor, list_numbers[i], port,))
            threads.append(t)
            threadPorts.append(port)
            port += 1
            
        print(f"threads anzahl: {len(threads)} ThreadPorts anzahl: {len(threadPorts)}")
        for t in threads:
            t.start()
        
        time.sleep(1)
        for port in threadPorts:
            so = socket(AF_INET, SOCK_STREAM)
            try:
                so.connect((clientIP, port))
                threadSockets.append(so)
            except Exception as e:
                print(f"Error: {e}")
                exit()

        bytes = s.recv(4096) 
        data = bytes.decode()

        if data == "Send result":
            for _socket in threadSockets:
                bytes_data = str(-1).encode()
                _socket.send(bytes_data)
        
        dataSet = set()
        for port in threadPorts:
            so = socket(AF_INET, SOCK_STREAM)
            try:
                so.connect((clientIP, port))
                dataSet.add(int(so.recv(4096).decode()))
                so.close()
            except Exception as e:
                print(f"Error: {e}")
                exit()
            threadSockets.append(so)
        if len(dataSet) == 1:
            s.send(str(dataSet.pop()).encode())
        else:
            s.send(str(-1).encode())
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
    server_socket.bind((clientIP, port))
    server_socket.listen(3)
    server_socket.setblocking(False)

    print(f"Starte Server mit IP: {clientIP} über Port {port}")
    server = asyncio.create_task(accept_clients(server_socket, taskQue))
    await asyncio.sleep(1)

    print(f"Opening Conection zu {prevIP} über Port {prevPort}")
    prevNeighborReader, prevNeighborWriter = await asyncio.open_connection(
        prevIP, prevPort)
    
    
    print(f"Opening Conection zu {nextIP} über Port {nextPort}")
    nextNeighborReader, nextNeighborWriter = await asyncio.open_connection(
        nextIP, nextPort)
    
    
    worker = asyncio.create_task(worker_and_sender(prevNeighborWriter, nextNeighborWriter, taskQue, number))

    await server
    M = await worker
    
    server_socket.setblocking(True)
        
    try:
        # Accept client connection
        print("Waiting for client connection...")
        client_socket, client_address = server_socket.accept()
        print(f"Client connected from: {client_address}")
        
        # Convert M to string and encode it
        message_str = str(M)
        message_bytes = message_str.encode('utf-8')
        print(f"Preparing to send message: '{message_str}' ({len(message_bytes)} bytes)")
        
        # Send the message with error handling
        try:
            bytes_sent = client_socket.send(message_bytes)
            
            if bytes_sent == len(message_bytes):
                print(f"✓ Successfully sent {bytes_sent} bytes to client")
                print(f"✓ Message: '{message_str}' sent successfully")
            else:
                print(f"⚠ Warning: Only {bytes_sent} of {len(message_bytes)} bytes were sent")
                print(f"  Message may not have been fully transmitted")
                
        except ConnectionResetError:
            print("✗ Error: Connection was reset by the client")
            print("  The client may have disconnected unexpectedly")
            
        except BrokenPipeError:
            print("✗ Error: Broken pipe - connection lost")
            print("  The client has disconnected or network failed")
            
        except socket.timeout:
            print("✗ Error: Send operation timed out")
            print("  The client is not responding")
            
        except BlockingIOError:
            print("✗ Error: Socket is in non-blocking mode")
            print("  Operation would block, but socket is set to blocking=True")
            
        except OSError as e:
            print(f"✗ OS Error during send: {e}")
            print(f"  Error code: {e.errno}")
            
        except Exception as e:
            print(f"✗ Unexpected error during send: {type(e).__name__}: {e}")
            
        finally:
            # Always try to close the client socket
            try:
                client_socket.close()
                print("✓ Client socket closed")
            except:
                print("⚠ Could not properly close client socket")
                
    except socket.timeout:
        print("✗ Error: Connection accept timed out")
        print("  No client connected within the timeout period")
        
    except OSError as e:
        print(f"✗ OS Error during accept: {e}")
        print(f"  Error code: {e.errno}")
        
    except KeyboardInterrupt:
        print("\n⚠ Server interrupted by user (Ctrl+C)")
        
    except Exception as e:
        print(f"✗ Unexpected error during accept: {type(e).__name__}: {e}")

    server_socket.close()
    print("Alles beendet!")

async def accept_clients(socket, taskQue):
    connection_count = 0
    tasks = []
    while connection_count < 3:
        client_socket, address = await asyncio.get_running_loop().sock_accept(socket)
        connection_count += 1
        print(f"Verbindung {connection_count}/3 von {address}")
        tasks.append(asyncio.create_task(handle_client(client_socket, taskQue)))
    for task in tasks:
        await task



async def handle_client(client_socket, taskQue):
    while True:
        data = await asyncio.get_running_loop().sock_recv(client_socket, 1024)
        if not data:
            client_socket.close()
            break
        decodetData = int(data.decode())       
        await taskQue.put(decodetData)
        if decodetData == -1:
            break

async def worker_and_sender(prevNeighborWriter, nextNeighborWriter, taskQue, M):
    print(f"Worker mit M: {M} gestartet")
    message = str(M).encode()
    prevNeighborWriter.write(message)
    await prevNeighborWriter.drain()
    nextNeighborWriter.write(message)
    await nextNeighborWriter.drain()
    
    y = await taskQue.get()
    while y != -1:
        if y < M:
            M = ((M - 1) % y) + 1
            message = str(M).encode()
            prevNeighborWriter.write(message)
            await prevNeighborWriter.drain()
            nextNeighborWriter.write(message)
            await nextNeighborWriter.drain()
            print(f"M aktualiesiert: {M}")
        y = await taskQue.get()

    message = str(-1).encode()
    prevNeighborWriter.write(message)
    await prevNeighborWriter.drain()
    nextNeighborWriter.write(message)
    await nextNeighborWriter.drain()
    return M 

signal.signal(signal.SIGINT, signal.SIG_DFL)
signal.signal(signal.SIGTERM, signal.SIG_DFL)
main()