from socket import *
import json

class Server:
    def run(self):
        s = socket(AF_INET, SOCK_STREAM)
        port = input("Port: ")
        
        s.bind(("192.168.193.98", port))
        s.listen(1)
        (conn, addr) = s.accept() # returns new socket and addr. client
        while True: # forever
            bytes = conn.recv(1024) # receive data from client

            if not bytes: continue
            data = bytes.decode()
            data_unmarsh = json.loads(data)

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

        conn.close() # close the connection

daten = ["cat", "dog", "papagei", "pigeon", "hamster", "lion", "dino", "koala"]
def write(i: int, d:str):
    daten[i] = d

def read(i: int): 
    return daten[i]

s = Server
s.run(s) # type: ignore
