from socket import *
import json
import signal

signal.signal(signal.SIGINT, signal.SIG_DFL)
signal.signal(signal.SIGTERM, signal.SIG_DFL)

while True:
    try:
        number_clients = int(input("Anzahl Computer zum berechnen: "))
        if number_clients > 0:
            break
        else:
            print("Zahl muss größer als 0 sein")
    except ValueError:
        print("Value Error: Ganzzahl eingeben")

s = socket(AF_INET, SOCK_STREAM)
s.bind(("127.0.0.1", 7777))
s.listen(number_clients)

clients = []  # Liste zum Speichern aller Client-Verbindungen

# Mehrere Clients akzeptieren
for i in range(number_clients):
    print(f"Warte auf Client: {i+1}/{number_clients}...")
    conn, addr = s.accept()  # Jedes accept() nimmt einen neuen Client an
    clients.append((conn, addr))
    print(f"Client {i+1} verbunden: {addr}")

while(True):

    inpup_string = input("Liste von nummern mit leerzeichen getrennt:")
    numbers_as_string_list = inpup_string.split()
    number_int_list = []
    for number in numbers_as_string_list:
        try:
            number_int_list.append(int(number))
        except ValueError:
            print(f"Value Error akured on :{number}")
    start_port = 3000
    if len(number_int_list) <= number_clients:
        
        clients_needet = clients[:len(number_int_list) - 1]
        for i in range(len(number_int_list)):
            numbers_client =[]
            numbers_client.append(number_int_list[i])

            _, adress_neigbor1 = clients[i - 1]
            _, adress_neigbor2 = clients[(i + 1) % len(clients)]
            adress_neigbor1 = (adress_neigbor1[0], start_port + (i - 1) * 10)
            adress_neigbor2 = (adress_neigbor2[0], start_port + (i + 1) * 10)

            if i == 0:
                adress_neigbor1 = (adress_neigbor1[0], start_port + (len(number_int_list) - 1) * 10)
            if i == len(number_int_list) - 1:
                adress_neigbor2 = (adress_neigbor2[0], start_port)

            command = {
                        "amount": 1,
                        "neighbor1": adress_neigbor1, 
                        "neighbor2": adress_neigbor2,
                        "list_numbers": numbers_client,
                        "port": (start_port + i * 10)
                    }
            
            json_data = json.dumps(command)
            bytes_data = json_data.encode()
            conn, _ = clients[i]
            conn.send(bytes_data)
    else:
        for i, (conn, addr) in enumerate(clients):
            amount_numbers = int(len(number_int_list) / number_clients)
            if i < number_clients - 1:
                numbers_client = number_int_list[amount_numbers * i:
                amount_numbers * i + amount_numbers]
            else:
                numbers_client = number_int_list[amount_numbers * i:]
            _, adress_neigbor1 = clients[i - 1]
            _, adress_neigbor2 = clients[(i + 1) % len(clients)]
            command = {
                        "amount": amount_numbers,
                        "neighbor1": adress_neigbor1, 
                        "neighbor2": adress_neigbor2,
                        "list_numbers": numbers_client
                    }
            json_data = json.dumps(command)
            bytes_data = json_data.encode()
            conn.send(bytes_data)

    command = "Send result"
    conn, _ = clients[0]
    bytes_data = command.encode()
    conn.send(bytes_data)
    
    while True:
            bytes = conn.recv(1024) # receive data from client

            if not bytes: continue
            data = bytes.decode()
            data_unmarsh = json.loads(data)
            print(data_unmarsh['result'])
            break
