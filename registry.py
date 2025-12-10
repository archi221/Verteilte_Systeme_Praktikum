from socket import * # type: ignore
import json
import threading
import time

def handle_client():
    welcomeMsg = """\nWillkommen beim Registry Service!\nMit folgenden Befehlen kannst du mit mir interagieren:\n
    register = Anmelden\n
    unregister = Abmelden\n
    list = Keine Ahnung\n"""
    for client in clients:
        json_data = json.dumps(welcomeMsg)
        bytes_data = json_data.encode()
        conn, _ = client
        conn.send(bytes_data)

def register_client():
    while True:
        conn, addr = s.accept()  # Jedes accept() nimmt einen neuen Client an
        if len(clients) < number_clients:
            clients.append((conn, addr))
            print(f"Client verbunden: {addr}")
            handleThread = threading.Thread(target=handle_client)
            handleThread.start()
        else:
            conn.close()
        if not clients:
            print("Keine Clients mehr verbunden")
            break

clients = []  # Liste zum Speichern aller Client-Verbindungen
number_clients = int(input("Wieviele Clients sollen zugelassen werden: "))
s = socket(AF_INET, SOCK_STREAM)
s.bind(("127.0.0.1", 7777))
s.listen(number_clients)

registerThread = threading.Thread(target=register_client)
registerThread.start()

registerThread.join()

# json_data = json.dumps(welcomeMsg)
# bytes_data = json_data.encode()
# conn.send(bytes_data)