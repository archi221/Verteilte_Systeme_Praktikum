from socket import *
import json
import signal
import threading
import time

signal.signal(signal.SIGINT, signal.SIG_DFL)
signal.signal(signal.SIGTERM, signal.SIG_DFL)

SERVER_IP = "127.0.0.1"
SERVER_PORT = 7777
MAX_CLIENTS = 100

server_socket = socket(AF_INET, SOCK_STREAM)
server_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
server_socket.bind((SERVER_IP, SERVER_PORT))
server_socket.listen(MAX_CLIENTS)

data_lock = threading.Lock()
client_id_counter = 0
clients = {}
robot_nodes = {}
clients_token_ring = []

def client_daemon(conn):
    client_type, client_name = accept_new_client(conn)
    if not client_name:
        conn.close()
        return

    if client_type == "node":
        handle_node(conn, client_name)
    elif client_type == "client":
        handle_client(conn, client_name)

def handle_node(conn, client_name):
    print("startet handle node")
    conn.settimeout(3.0)
    try:
        while True:
            bytes_received = conn.recv(1024)
            if not bytes_received:
                break

            data = json.loads(bytes_received.decode())
            if data.get("befehl") != "Im Alive":
                print(f"Unerwarteter Befehl: {data.get('befehl')}")
            
    except TimeoutError:
        print(f"Timeout bei Kommunikation mit {client_name} - Keine Daten innerhalb von 3 Sekunden")
    except Exception as e:
        print(f"error {client_name}: {e}")
    finally:
        with data_lock:
            robot_nodes.pop(client_name, None)
        conn.close()

def handle_client(conn, mein_name):
    try:
        while True:
            received_bytes = conn.recv(1024)
            if not received_bytes:
                break

            data = json.loads(received_bytes.decode())
            befehl = data.get("befehl")

            if befehl == "liste":
                target_type = data.get("type")
                with data_lock:
                    if target_type == "node":
                        ergebnis = [[k, v['id'], v['ip'], v['port']] for k, v in robot_nodes.items()]
                    elif target_type == "client":
                        ergebnis = [[k, v['id'], v['ip'], v['port']] for k, v in clients.items()]
                    else:
                        ergebnis = []
                conn.sendall((json.dumps({
                    "befehl": "liste_antwort",
                    "daten": ergebnis
                }) + "\n").encode("utf-8"))

            elif befehl == "nachbarn":
                with data_lock:
                    if mein_name in clients_token_ring:
                        n = len(clients_token_ring)
                        idx = clients_token_ring.index(mein_name)
                        name_v = clients_token_ring[(idx - 1) % n]
                        name_n = clients_token_ring[(idx + 1) % n]

                        v_info = clients[name_v]
                        n_info = clients[name_n]

                        antwort = {
                            "befehl": "nachbarn_antwort",
                            "alleiniger_Client": n == 1,
                            "vorgänger": {"name": name_v, "ip": v_info["ip"], "port": v_info["port"]},
                            "nachfolger": {"name": name_n, "ip": n_info["ip"], "port": n_info["port"]}
                        }
                    else:
                        antwort = {"befehl": "error", "code": "nicht_registriert"}

                conn.sendall((json.dumps(antwort) + "\n").encode("utf-8"))

            elif befehl == "dead":
                with data_lock:
                    if mein_name in clients_token_ring:
                        clients_token_ring.remove(mein_name)
                    clients.pop(mein_name, None)
                    robot_nodes.pop(mein_name, None)

                conn.sendall((json.dumps({"befehl": "Ok"}) + "\n").encode("utf-8"))
                return

    except Exception:
        pass
    finally:
        with data_lock:
            if mein_name in clients_token_ring:
                clients_token_ring.remove(mein_name)
            clients.pop(mein_name, None)
        conn.close()

def accept_new_client(conn):
    global client_id_counter
    try:
        while True:
            received_bytes = conn.recv(1024)
            if not received_bytes:
                return None, None

            data = json.loads(received_bytes.decode())
            client_name = data.get("clientName")
            client_type = data.get("type")
            ip = data.get("ip")
            port = data.get("port")

            with data_lock:
                if client_name in robot_nodes or client_name in clients:
                    error_msg = {"befehl": "error", "code": "name schon vorhanden"}
                    conn.sendall((json.dumps(error_msg) + "\n").encode("utf-8"))
                else:
                    client_id_counter += 1
                    client_data = {"id": client_id_counter, "ip": ip, "port": port}

                    if client_type == "node":
                        robot_nodes[client_name] = client_data
                    elif client_type == "client":
                        clients[client_name] = client_data
                        clients_token_ring.append(client_name)

                    conn.sendall((json.dumps({"befehl": "Ok"}) + "\n").encode("utf-8"))
                    print(f"client: {client_name} des types: {client_type} akzeptiert")
                    return client_type, client_name

    except Exception:
        print("error in accept_new_client")
        return None, None

while True:
    conn, addr = server_socket.accept()
    t = threading.Thread(target=client_daemon, args=(conn,))
    t.daemon = True
    t.start()
