from paho.mqtt import client as mqtt_client
from FormattedOutput import formatOut
import time

broker = "localhost"
port = 1883
topic = "control-topic"

def connect_mqtt():
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            formatOut("Connected to MQTT Broker!")
        else:
            formatOut(f"Failed to connect, return code {rc}")

    client = mqtt_client.Client(f"{0}")
    client.on_connect = on_connect
    client.connect(broker, port)
    return client

def publish(client):
    time.sleep(0.100) ### for parallel output

    ### this value will be sent to every node
    option = input("Enter Number of products you want to build: ")

    try:
        value = int(option)
        client.publish(topic, f"NUMBER_OF_PRODUCTS#{value}") ### sending the value to all subscribers
    except:
        formatOut("Somethins is wrong ...") 
    
    flag = True
    while flag:
        printMenu()
        option = input("Enter option: ")

        ### if you exit the program(as a publisher) then the nodes/subscribers should also stop working
        if option.__eq__("END"):
            client.publish(topic, "quit", qos=1)
            flag = False
        elif option.startswith("START#") or option.startswith("STOP#") or option.startswith("MESSAGE#") or option.startswith("RUN_TIME#") or option.startswith("quit"):
            client.publish(topic, option, qos=1)
            flag = True

def run():
    client = connect_mqtt()
    client.loop_start()
    publish(client)

def printMenu():
    print("\n")
    print("=========================================")
    print("|==== MENU =============================|")
    print("|=======================================|")
    print("|== RUN_TIME#<ID>#<NUMBER> =============|") ### with this i give every node the time it will take to execute their operation
    print("|== MESSAGE#<ID>#<SOME_MESSAGE> ========|") ### with this i give every node the message it will it will print when it executes the operation
    print("|== STOP#<ID> ==========================|") ### stops working only certain node
    print("|== START#<ID> =========================|") ### start working only certain node
    print("|== STOP#ALL ===========================|") ### every node stops working
    print("|== START#ALL ==========================|") ### every node starts working
    print("|== quit ===============================|") ### every node finishes their execution immediately - without finishing their operations
    print("|== END ================================|") ### you exit the program 
    print("=========================================")
    print("\n")

run()