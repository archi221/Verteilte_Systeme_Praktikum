from socket import *
import json
from abc import ABC, abstractmethod
from typing import Protocol, Any, Dict
import time

def register(client_name) -> bool:
    liste = {"clientName": client_name, "type": "client", "ip": OWN_IP, "port": OWN_PORT}
    marsh_data = json.dumps(liste)
    bytes_data = marsh_data.encode()
    s.send(bytes_data) # send same data

    bytes = s.recv(1024) # receive the response
    json_data = bytes.decode()
    data = json.loads(json_data)
    befehl = data.get("befehl")
    if befehl == "Ok":
        print("Erfolgreich registriert!")
        return True
    else:
        code = data.get("code")
        print(f"{befehl}: fehler bei der Registrierung! {code}")
        return False

def unregister() -> bool:
    liste = {"befehl": "dead"}
    marsh_data = json.dumps(liste)
    bytes_data = marsh_data.encode()
    s.send(bytes_data) # send same data

    bytes = s.recv(1024) # receive the response
    json_data = bytes.decode()
    data = json.loads(json_data)
    answer = data.get("befehl")
    if answer == "Ok":
        print("Erfolgreich abgemeldet!")
        return True
    else:
        print("Beim Abmelden ist ein Fehler aufgetaucht!")
        return False

def neighbours() -> Any:
    liste = {"befehl": "nachbarn"}
    marsh_data = json.dumps(liste)
    bytes_data = marsh_data.encode()
    s.send(bytes_data) # send same data

    bytes = s.recv(1024) # receive the response
    json_data = bytes.decode()
    data = json.loads(json_data)
    if data.get("befehl") == "nachbarn_antwort":
        return (
            data.get("alleiniger_Client"),
            data.get("vorgänger"),
            data.get("nachfolger"),
        )
    else:
        print("Fehler bei Antwort von Befehl: nachbarn")
        return None

def liste_clients() -> Any:
    liste = {"befehl": "liste", "type": "client"}
    marsh_data = json.dumps(liste)
    bytes_data = marsh_data.encode()
    s.send(bytes_data) # send same data

    bytes = s.recv(1024) # receive the response
    json_data = bytes.decode()
    data = json.loads(json_data)
    if data.get("befehl") == "liste_antwort":
        return data.get("daten")
    else:
        print("Fehler bei Antwort von Befehl: liste, type: client")
        return None
    
def liste_nodes() -> Any:
    liste = {"befehl": "liste", "type": "node"}
    marsh_data = json.dumps(liste)
    bytes_data = marsh_data.encode()
    s.send(bytes_data) # send same data

    bytes = s.recv(1024) # receive the response
    json_data = bytes.decode()
    data = json.loads(json_data)
    if data.get("befehl") == "liste_antwort":
        return data.get("daten")
    else:
        print("Fehler bei Antwort von Befehl: liste, type: node")
        return None

#---------------------------MAIN----------------------------
OWN_IP = "127.0.0.1"
OWN_PORT = 5001

print("Wie ist der Name des Clients?")
client_name = input()
print("Registrieren sie sich nun mit: register")
s = socket(AF_INET, SOCK_STREAM)

connected = False
registered = False
while True:
    user_input = input()

    if user_input == "register":
        if registered:
            print("Bereits registriert")
            continue
        
        if not connected:
            try:
                print("Verbindung zum Server wird aufgebaut!")
                s.connect(("127.0.0.1", 7777)) # connect to server (block until accepted) 127.0.0.1 localhost
                connected = True
            except Exception as e:
                print(f"Error: {e}")
                connected = False
                registered = False
                continue

        while True:
            registered = register(client_name)
            if registered:
                break
            print("\nWählen Sie einen neuen Namen für den Client:")
            client_name = input()


    if registered:
        match user_input:
            case "dead":
                try:
                    ok = unregister()
                except Exception as e:
                    print(f"Unregister fehlgeschlagen: {e}")
                    ok = False

                # Wenn erfolgreich abgemeldet: Socket schließen, Status zurücksetzen
                if ok:
                    registered = False
                    connected = False
                    try:
                        s.close()
                    except Exception:
                        pass
                    s = socket(AF_INET, SOCK_STREAM)

            case "nachbarn":
                try:
                    answer = neighbours()
                    if answer is None:
                        continue
                except Exception as e:
                    print(f"Neighbours fehlgeschlagen: {e}")
                    continue

                alone, vorgänger, nachfolger = answer
                print(f"Test: {alone}, {vorgänger}, {nachfolger}")
                continue

            case "liste client":
                try:
                    answer = liste_clients()
                    if answer is None:
                        continue
                except Exception as e:
                    print(f"Liste_Clinets fehlgeschlagen: {e}")
                    continue

                for name, cid, ip, port in answer:
                    print(f"{name} (id={cid}) {ip}:{port}")
                continue

            case "liste node":
                try:
                    answer = liste_nodes()
                    if answer is None:
                        continue
                except Exception as e:
                    print(f"Liste_Clinets fehlgeschlagen: {e}")
                    continue

                for name, cid, ip, port in answer:
                    print(f"{name} (id={cid}) {ip}:{port}")
                continue

            case _:
                print("Commands: liste client | liste node | nachbarn | dead")
    else:
        print("Bitte registrieren sie sich vorher mit: register!")