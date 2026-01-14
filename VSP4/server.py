from socket import *
import json
import threading
import signal
from concurrent.futures import ThreadPoolExecutor

signal.signal(signal.SIGINT, signal.SIG_DFL)
signal.signal(signal.SIGTERM, signal.SIG_DFL)

MAX_CLIENTS = 10

data_lock = threading.Lock()
daten = ["cat", "dog", "papagei", "pigeon", "hamster", "lion", "dino", "koala"]

def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        port = int(input("Port: ")) 
        s.bind(("192.168.193.98", port))
        s.listen(MAX_CLIENTS)
        print(f"Server läuft auf Port {port}...")
    except Exception as e:
        print(f"Fehler beim Starten des Servers: {e}")
        return

    with ThreadPoolExecutor(max_workers=MAX_CLIENTS) as executor:
        while True:
            try:
                conn, addr = s.accept()
                print(f"Verbindung von {addr}")
##################################################################################################              
#### wird zwar von mit threadpool gestartet aber geht von immer genau einem client der anfragt aus
### Threadpol damit viele anfragen hintereinanderr kommen können###
##################################################################################################
                executor.submit(handle_client, conn)
                
            except Exception as e:
                print(f"Fehler bei der Verbindungsannahme: {e}")

def handle_client(conn):
    while True:
        try:
            bytes = conn.recv(1024)
            if not bytes: break

            data_unmarsh = json.loads(bytes.decode())

            if data_unmarsh["method"] == "write":
                try:
                    write(data_unmarsh["v1"], data_unmarsh["v2"])
                except Exception as e:
                    answer = {
                        "ok": 0,
                        "return": f"Error: {e}"
                    }
                else:
                        read_answer = 0

                        answer = {
                        "ok": 1,
                        "return": 0
                    }               
            elif data_unmarsh["method"] == "read":
                try:
                    read_answer = read(data_unmarsh["v1"])
                except IndexError:
                    answer = {
                        "ok": 0,
                        "return": "NoSuchElementException Index wurde nicht gefunden"
                    }
                except Exception as e:
                    answer = {
                        "ok": 0,
                        "return": f"Error: {e}"
                    }
                else:
                    answer = {
                    "ok": 1,
                    "return": read_answer
                }
            else : break
            print(data_unmarsh)
            print(daten)
            

            json_data = json.dumps(answer)
            bytes_data = json_data.encode()
            conn.send(bytes_data)

        except Exception as e:
            print(f"error in handle Client: {e}")
        finally:
            conn.close()

def write(i: int, d:str):
    global daten
    daten[i] = d

def read(i: int):
    global daten 
    return daten[i]

if __name__ == "__main__":
    main()