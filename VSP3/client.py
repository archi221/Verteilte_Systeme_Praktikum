from socket import *
import json
from abc import ABC, abstractmethod
from typing import Protocol, Any, Dict
import time
import threading

def register(client_name) -> tuple[bool, bool]:
    liste = {"clientName": client_name, "type": "client", "ip": OWN_IP, "port": OWN_PORT}
    marsh_data = json.dumps(liste)
    bytes_data = marsh_data.encode()

    with server_lock:
        s.send(bytes_data) # send same data

        bytes = s.recv(1024) # receive the response

    json_data = bytes.decode()
    data = json.loads(json_data)
    befehl = data.get("befehl")
    if befehl == "Ok":
        alone = data.get("alleiniger_Client")
        token = alone
        if token:
            token_erhalten_event.set()
        print("Erfolgreich registriert!")
        if token:
            print("Du bist alleiniger Client und hast den TOKEN.")
        else:
            print("Registriert. Warte auf TOKEN von Vorgänger.")
        return True, token
    else:
        code = data.get("code")
        print(f"{befehl}: fehler bei der Registrierung! {code}")
        return False, False

def unregister() -> bool:
    liste = {"befehl": "dead"}
    marsh_data = json.dumps(liste)
    bytes_data = marsh_data.encode()

    with server_lock:
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

    with server_lock:
        s.send(bytes_data) # send same data

        bytes = s.recv(1024) # receive the response

    json_data = bytes.decode()
    data = json.loads(json_data)
    if data.get("befehl") == "nachbarn_antwort":
        return (
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

    with server_lock:
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

    with server_lock:
        s.send(bytes_data) # send same data

        bytes = s.recv(1024) # receive the response

    json_data = bytes.decode()
    data = json.loads(json_data)
    if data.get("befehl") == "liste_antwort":
        return data.get("daten")
    else:
        print("Fehler bei Antwort von Befehl: liste, type: node")
        return None
    
def start_token_listener():
    def run():
        global token
        sendSocket = socket(AF_INET, SOCK_STREAM)
        sendSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        sendSocket.bind((OWN_IP, OWN_PORT))
        sendSocket.listen(5)
        sendSocket.settimeout(1.0)

        while not token_stop.is_set():
            try:
                conn, _ = sendSocket.accept()
            except timeout:
                continue
            except Exception:
                break

            try:
                msg = conn.recv(1024)
                if msg:
                    data = json.loads(msg.decode("utf-8").strip())
                    if data.get("befehl") == "token":
                        token = True
                        token_erhalten_event.set()
                        print("\n TOKEN erhalten, du darfst arbeiten.")
                        print("NODE> ", end="", flush=True)
            except Exception:
                pass
            finally:
                try:
                    conn.close()
                except Exception:
                    pass

        try:
            sendSocket.close()
        except Exception:
            pass

    t = threading.Thread(target=run, daemon=True)
    t.start()

def sende_token_zu_nachfolger() -> bool:
    global token

    nachbarn = neighbours()
    if nachbarn is None:
        print("Kann Token nicht senden: keine Nachbarn")
        return False

    alone, _, nachfolger = nachbarn
    if alone:
        print("Du bist alleiniger Client, TOKEN bleibt bei dir.")
        return True

    ip = nachfolger.get("ip")
    port = nachfolger.get("port")
    name = nachfolger.get("name")

    if ip == OWN_IP and port == OWN_PORT:
        print("Du bist alleiniger Client, TOKEN bleibt bei dir.")
        return True


    try:
        sendSocket = socket(AF_INET, SOCK_STREAM)
        sendSocket.settimeout(2.0)
        sendSocket.connect((ip, port))
        sendSocket.sendall((json.dumps({"befehl": "token"}) + "\n").encode("utf-8"))
        sendSocket.close()

        token = False
        print(f"TOKEN gesendet an {name} ({ip}:{port})")
        return True
    except Exception as e:
        print(f"Token senden fehlgeschlagen: {e}")
        return False

def send_move(node_ip: str, node_port: int, achse: str, wert: int):
    payload = {"befehl": "move", "achse": achse, "wert": wert}
    try:
        sock = socket(AF_INET, SOCK_STREAM)
        sock.settimeout(3.0)
        sock.connect((node_ip, node_port))
        sock.sendall((json.dumps(payload) + "\n").encode("utf-8"))
        sock.close()
        print(f"move gesendet an {node_ip}:{node_port} ({achse}={wert})")
    except Exception as e:
        print(f"move fehlgeschlagen ({node_ip}:{node_port}): {e}")


#---------------------------MAIN----------------------------
SERVER_IP = "127.0.0.1"
SERVER_PORT = 7777
OWN_IP = "127.0.0.1"
OWN_PORT = int(input("Eigener Port (z.B. 5001): "))

print("Wie ist der Name des Clients?")
client_name = input()
print("Registrieren sie sich nun mit: register")
s = socket(AF_INET, SOCK_STREAM)

connected = False
registered = False
token = False
token_stop = threading.Event()
server_lock = threading.Lock()
token_erhalten_event = threading.Event()
nodes_cache = []

while True:

    if token_erhalten_event.is_set():
        token_erhalten_event.clear()
        nodes = liste_nodes()
        nodes_cache = nodes or []
        print("\n Verfügbare Nodes:")
        if not nodes_cache:
            print("  (keine)")
        else:
            for name, cid, ip, port in nodes_cache:
                print(f"  - {name} (id={cid}) {ip}:{port}")


    prompt = "NODE> " if token else ""
    user_input = input(prompt)


    if user_input == "register":
        if registered:
            print("Bereits registriert")
            continue
        
        if not connected:
            try:
                print("\nVerbindung zum Server wird aufgebaut!")
                s.connect((SERVER_IP, SERVER_PORT)) # connect to server (block until accepted) 127.0.0.1 localhost
                connected = True
            except Exception as e:
                print(f"Error: {e}")
                connected = False
                registered = False
                continue

        while True:
            registered, token = register(client_name)
            if registered:
                start_token_listener()
                break
            print("\nWählen Sie einen neuen Namen für den Client:")
            client_name = input()
            
        continue


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

                vorgänger, nachfolger = answer
                print(f"Test: {vorgänger}, {nachfolger}")
                continue

            case "liste client":
                try:
                    answer = liste_clients()
                    if answer is None:
                        continue
                except Exception as e:
                    print(f"Liste_Clients fehlgeschlagen: {e}")
                    continue

                for name, cid, ip, port in answer:
                    print(f"{name} (id={cid}) {ip}:{port}")
                continue

            case "liste node":
                try:
                    answer = liste_nodes()
                    if answer is None:
                        print("Keine Nodes vorhanden")
                        continue
                except Exception as e:
                    print(f"Liste_Nodes fehlgeschlagen: {e}")
                    continue

                for name, cid, ip, port in answer:
                    print(f"{name} (id={cid}) {ip}:{port}")
                continue
            
            case "work done":
                if not token:
                    print("Du hast keinen Token. Warte bis du den Token hast.")
                    continue
                sende_token_zu_nachfolger()
                continue

            case "move":
                print("Beispiel Syntax:")
                print("  move all <achse> <wert>")
                print("  move NodeA,NodeB <achse> <wert>")
                print("Achsen: leftRight | upDown | backForth | openClose")
                continue

            case cmd if cmd.startswith("move "):
                if not token:
                    print("Kein Token. Node-Steuerung nicht erlaubt.")
                    continue

                parts = cmd.split()
                if len(parts) != 4:
                    print("Beispiel Syntax:")
                    print("  move all <achse> <wert>")
                    print("  move NodeA,NodeB <achse> <wert>")
                    continue

                targets_raw = parts[1]
                achse = parts[2]
                try:
                    wert = int(parts[3])
                except ValueError:
                    print("wert muss eine Zahl sein (0-100)")
                    continue

                if achse not in {"leftRight", "upDown", "backForth", "openClose"}:
                    print("Ungültige achse")
                    continue
                if not (0 <= wert <= 100):
                    print("wert muss 0-100 sein")
                    continue

                nodes = liste_nodes()
                if not nodes:
                    print("Keine Nodes bekannt.")
                    continue

                # Ziel-Nodes bestimmen
                if targets_raw == "all":
                    targets = nodes
                else:
                    target_names = [n.strip() for n in targets_raw.split(",")]
                    targets = [n for n in nodes if n[0] in target_names]

                    if not targets:
                        print("Keine der angegebenen Nodes gefunden.")
                        continue

                for name, cid, ip, port in targets:
                    print(f"→ {name}")
                    send_move(ip, port, achse, wert)

                continue
            
            case _:
                print("Commands: liste client | liste node | nachbarn | move | dead | work done")
    else:
        print("Bitte registrieren sie sich vorher mit: register!")