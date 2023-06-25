#!/usr/bin/env python
import pika, sys, os
import serial.tools.list_ports
import time
from datetime import datetime


# Arduino
arduino = None
#port_arduino ='COM3'
port_arduino  = '/dev/ttyACM0'
baud = 9600
MSG_VIDE_ARDUINO="                ;                "

## Queue
# Queue parametre
ip_rabbitMQ_service="localhost"
port_rabbitMQ_service=5672
virtual_host="/"
queue_name=""
username=""
password=""

# Queue : format message 
MSG_TEST="Toto;2023-06-04 00:35:45;2024-06-04 00:35:45;5;Message ligne 1;Message ligne2"

FORMAT_MSG="nom_publisher;date_envoie(%Y-%m-%d %H:%M:%S);date_peremption(%Y-%m-%d %H:%M:%S);duree_affichage(secondes);ligne1_msg;ligne2_msg"
NOM_PUBLISHER=0
DATE_ENVOIE=1
DATE_PEREMPTION=2
DUREE_AFFICHAGE=3
LIGNE1_MSG=4
LIGNE2_MSG=5

# Format du message : 
# nom_publisher
# date_envoie => %Y-%m-%d %H:%M:%S
# date_peremption => %Y-%m-%d %H:%M:%S.%3N"
# duree_affichage => en seconde
# ligne1_msg
# ligne2_msg



def callback(ch, method, properties, body):
    # print(" [x] Received %r" % body)
    # print(" [x] Received %r" % body + str(body.type))
    try:
        params_msg = check_msg_ok(str(body))
        if(check_validite_msg(params_msg)):
                message_complet = params_msg[LIGNE1_MSG] + ";" + params_msg[LIGNE2_MSG]
                arduino.write(message_complet.encode())
                print("Affichage pendant " + str(params_msg[DUREE_AFFICHAGE]) + "s du message : " + message_complet)
                time.sleep(params_msg[DUREE_AFFICHAGE])
                #arduino.write(MSG_VIDE_ARDUINO.encode())
    except ValueError as e:
        print("Erreur format : " + str(e))
    except Exception as e:
        print("Erreur : " + str(e))

    
def split_msg(data: str, separator : str = ";") -> list:
    return data.split(separator)

def is_ascii(s):
    return all(ord(c) < 128 for c in s)

# Renvoie la liste des paramètres correctement convertie pour un traitement
def check_msg_ok(message ) -> list:
    params_msg = split_msg(message)
    
    # Erreur de format pour le message
    if(len(params_msg) != 6):
        raise ValueError("Format message pas du bon type : " + ";".join(params_msg) + " et format attendu : " + FORMAT_MSG)

    # Vérifiacation des chaines ascii
    if(is_ascii(params_msg[NOM_PUBLISHER]) == False):
        raise ValueError("Erreur valeur non ASCII pour le nom du publisher : "+ params_msg[NOM_PUBLISHER])
    if(is_ascii(params_msg[LIGNE1_MSG]) == False):
        raise ValueError("Erreur valeur non ASCII pour le msg sur la ligne 1 : "+ params_msg[LIGNE1_MSG])
    if(is_ascii(params_msg[LIGNE2_MSG]) == False):
        raise ValueError("Erreur valeur non ASCII pour le msg sur la ligne 1 : "+ params_msg[LIGNE2_MSG])

    # Récupération date
    try: # Récupération de la date d'envoie
        date_envoie = datetime.strptime(params_msg[DATE_ENVOIE], "%Y-%m-%d %H:%M:%S")
        params_msg[DATE_ENVOIE] = date_envoie
    except ValueError as e:
       print("Erreur date d'envoie : " + str(e))
    try: # Récupération de la date de peremption
        date_peremption = datetime.strptime(params_msg[DATE_PEREMPTION], "%Y-%m-%d %H:%M:%S")
        params_msg[DATE_PEREMPTION] = date_peremption
    except ValueError as e:
       print("Erreur date de péremption :" + str(e))

    try: # Récupération duree affichage
        duree_affichage = int(params_msg[DUREE_AFFICHAGE])
        params_msg[DUREE_AFFICHAGE] = duree_affichage
    except ValueError as e:
        print("Erreur format duree affichage :" + str(e))

    return params_msg

# Check si la date de peremption n'est pas dépassee
def check_validite_msg(params_msg: list) -> bool:
    # if(time.time() + params_msg[DUREE_AFFICHAGE] > params_msg[DATE_PEREMPTION]):
    if(datetime.now() > params_msg[DATE_PEREMPTION]):
        return False
    else:
        return True

def main():

    credentials = pika.PlainCredentials(username=username, password=password)
    parameters = pika.ConnectionParameters(host=ip_rabbitMQ_service, 
                                           port=port_rabbitMQ_service,
                                           virtual_host=virtual_host,
                                           credentials=credentials)
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()
    channel.queue_declare(queue=queue_name)

    channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)

    print(' [*] Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()

if __name__ == '__main__':
    try:
        # Remplacez 'COM3' par le nom du port série utilisé par votre carte Arduino
        arduino = serial.Serial(port_arduino, baud)
        # Attendre que la connexion soit établie
        time.sleep(5)
        arduino.write("Connexion arduin;etablie         ".encode())
        time.sleep(5)
        arduino.write("Ready pour msg  ;                ".encode())
        time.sleep(2)

        main()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
    finally:
        arduino.close()
