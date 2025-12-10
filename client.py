from socket import *
import json
from abc import ABC, abstractmethod
from typing import Protocol, Any, Dict
import time

class Datastore(ABC):
    @abstractmethod
    def read(self, key: int) -> Any:
        pass

    @abstractmethod
    def write(self, key: int, value: str) -> None:
        pass

class server_data(Datastore):
    def __init__(self) -> None:
        s = socket(AF_INET, SOCK_STREAM)
        try:
            s.connect(("127.0.0.1", 7777)) # connect t o server (block until accepted) 127.0.0.1 localhost
        except Exception as e:
            print(f"Error: {e}")
            exit()
        else:
            self.s = s
            bytes = self.s.recv(1024) # receive the response
            json_data = bytes.decode()
            data = json.loads(json_data)
            print(data)

    
    def read(self, key: int) -> Any:
        liste = {"method": "read", "v1":key}
        marsh_data = json.dumps(liste)
        bytes_data = marsh_data.encode()
        self.s.send(bytes_data) # send same data

        bytes = self.s.recv(1024) # receive the response
        json_data = bytes.decode()
        data = json.loads(json_data)
        if (data["ok"] == 0):
            raise Exception(f"Server returned error: {data['return']}")
        return data["return"]

      
    
    def write(self, key: int, value: str) -> None:
        liste = {"method": "write", "v1":key, "v2": value}
        marsh_data = json.dumps(liste)
        bytes_data = marsh_data.encode()
        self.s.send(bytes_data) # send same data

        bytes = self.s.recv(1024) # receive the response
        json_data = bytes.decode()
        data = json.loads(json_data)
        if (data["ok"] == 0):
            raise Exception(f"Server returned error: {data['return']}")
        return



class client_data(Datastore):
    def __init__(self) -> None:
        self.daten = ["cat", "dog", "papagei", "pigeon", "hamster", "lion", "dino", "koala"]
    
    def read(self, key: int) -> Any:
        return self.daten[key]

    def write(self, key: int, value: str) -> None:
        self.daten[key] = value

#---------------------------------------------------------------

c = client_data()
s = server_data()

key = 5
value = "value"

# Annahme: c = ClientDatastore(), s = ServerDatastore()
# Du hast die schon gebaut, also hier nur die Nutzung:
# c.write(key, value)
# c.read(key)
print(f"Schicke an {key} den Wert: {value}")
s.write(key, value)
s.read(key)
