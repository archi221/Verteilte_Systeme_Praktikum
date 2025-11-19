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
            s.connect(("172.18.27.132", 7777)) # connect t o server (block until accepted) 127.0.0.1 localhost
        except Exception as e:
            print(f"Error: {e}")
            exit()
        else:
            self.s = s
    
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



# Annahme: c = ClientDatastore(), s = ServerDatastore()
# Du hast die schon gebaut, also hier nur die Nutzung:
# c.write(key, value)
# c.read(key)
# s.write(key, value)
# s.read(key)

# Hilfsfunktion zum Messen einer einzelnen Ausführung
def time_single_call(func, *args, **kwargs):
    start = time.perf_counter()
    result = func(*args, **kwargs)
    end = time.perf_counter()
    duration = end - start
    return result, duration  # wir geben beides zurück: Rückgabewert + Dauer in Sekunden

# Hilfsfunktion zum Messen vieler Ausführungen
def time_multi_call(func, n, *args, **kwargs):
    start = time.perf_counter()
    last_result = None
    for _ in range(n):
        last_result = func(*args, **kwargs)
    end = time.perf_counter()
    total_duration = end - start
    avg_duration = total_duration / n
    return last_result, total_duration, avg_duration


# --- BENCHMARK ---

N = 1000  # Anzahl Wiederholungen für den Client

# 1. SERVER write einmal messen
server_write_result, server_write_time = time_single_call(s.write, 5, "Test")

# 2. SERVER read einmal messen
server_read_result, server_read_time = time_single_call(s.read, 5)

# 3. CLIENT write 1000x messen
client_write_result, client_write_total, client_write_avg = time_multi_call(c.write, N, 5, "Test")

# 4. CLIENT read 1000x messen
client_read_result, client_read_total, client_read_avg = time_multi_call(c.read, N, 5)


# --- AUSGABE ---

print("=== Ergebnisse ===")
print(f"Server.write(5, 'Test') -> {server_write_result}")
print(f"   Dauer gesamt (1x): {server_write_time * 1000:.3f} ms")

print(f"Server.read(5) -> {server_read_result}")
print(f"   Dauer gesamt (1x): {server_read_time * 1000:.3f} ms")

print(f"Client.write(5, 'Test') -> {client_write_result}")
print(f"   Dauer gesamt ({N}x): {client_write_total * 1000:.3f} ms")
print(f"   Durchschnitt/Aufruf: {client_write_avg * 1000:.6f} ms")

print(f"Client.read(5) -> {client_read_result}")
print(f"   Dauer gesamt ({N}x): {client_read_total * 1000:.3f} ms")
print(f"   Durchschnitt/Aufruf: {client_read_avg * 1000:.6f} ms")

