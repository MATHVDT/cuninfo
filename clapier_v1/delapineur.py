#!/usr/bin/env python
import pika, sys, os
import serial.tools.list_ports
import time
from datetime import datetime


# Arduino
arduino = None
arduino_port=os.environ['ARDUINO_PORT']
arduino_baud=os.environ['ARDUINO_BAUD']
MSG_VIDE_ARDUINO="                ;                "
DELAY_INTERVAL = [ 0, 2000, 1500,  1000, 800, 650, 500, 300, 100, 50] # Intervalle de décalage en MILISECONDES !!! (première valeur pas utilisée)

## Queue
# Queue parametre
ip_rabbitMQ_service=os.environ['IP_QUEUE']
port_rabbitMQ_service=os.environ['PORT_QUEUE']
virtual_host=os.environ['VIRTUAL_HOST']
queue_name=os.environ['QUEUE_NAME']
username_queue=os.environ['USERNAME_DELAPINEUR']
password_queue=os.environ['PASSWORD_DELAPINEUR']

# Queue : format message 
MSG_TEST="Toto;2023-06-04 00:35:45;2024-06-04 00:35:45;5;Message ligne 1;Message ligne2"

FORMAT_MSG="nom_publisher;date_diffusion(%Y-%m-%d %H:%M:%S);date_expiration(%Y-%m-%d %H:%M:%S);duree_affichage(secondes);ligne1_msg;ligne2_msg"
NOM_PRODUCTEUR=0
DATE_DIFFUSION=1
DATE_EXPIRATION=2
DUREE_AFFICHAGE=3
LIGNE1_MSG=4
LIGNE2_MSG=5

# Format du message : 
# nom_publisher
# date_diffusion => %Y-%m-%d %H:%M:%S
# date_expiration => %Y-%m-%d %H:%M:%S.%3N"
# duree_affichage => en seconde
# ligne1_msg
# ligne2_msg


def callback(ch, method, properties, body):
    try:
        params_msg = check_msg_ok(str(body.decode('ascii')))
        if(check_validite_msg(params_msg)):
                message_complet = formate_message(params_msg)
                print(f"Affichage pendant {str(params_msg[DUREE_AFFICHAGE])}s du message : '{str(message_complet)}'")
                arduino.write(message_complet.encode())
                time.sleep(params_msg[DUREE_AFFICHAGE])
                ch.basic_publish(exchange='', routing_key=queue_name, body=body)
    except ValueError as e:
        print("Erreur format : " + str(e))
    except Exception as e:
        print("Erreur : " + str(e))

def formate_message(param : list) -> str:
    ligne1 = ajoute_scroll_ligne(param[LIGNE1_MSG],param[DUREE_AFFICHAGE])
    ligne2 = ajoute_scroll_ligne(param[LIGNE2_MSG],param[DUREE_AFFICHAGE])
    return ligne1 + ";" + ligne2

# Regarde la taille de la ligne et ajoute la valeur de scroll du texte pour la arduino
# Complete la ligne pour qu'elle fasse 17 caractères
# 1 vitesse + 16 texte
def ajoute_scroll_ligne(ligne_msg : str, duree_affichage : int) :
    ligne_msg.ljust(16, " ") # Ajuste ca taille
    nb_decalage = len(ligne_msg) - 16
    if(nb_decalage == 0): # 
        return "0" + ligne_msg
    else:
       return str(trouver_vitesse_scroll(nb_decalage, duree_affichage)) + ligne_msg


def trouver_vitesse_scroll(nb_decalage : int, duree : int):
    if nb_decalage <= 0:
        return 0
    temps_par_decalage = duree / nb_decalage
    for index, vitesse in enumerate(DELAY_INTERVAL[1:]):
        if  vitesse < temps_par_decalage * 1000:
            return index
    return 9

def split_msg(data: str, separator : str = ";") -> list:
    return data.split(separator)

def is_ascii(s):
    return all(ord(c) < 128 for c in s)

# Rdate_expiration la liste des paramètres correctement convertie pour un traitement
def check_msg_ok(message : str) -> list:
    params_msg = split_msg(message)
    
    # Erreur de format pour le message
    if(len(params_msg) != 6):
        raise ValueError("Format message pas du bon type : " + ";".join(params_msg) + " et format attendu : " + FORMAT_MSG)

    # Vérifiacation des chaines ascii
    if(is_ascii(params_msg[NOM_PRODUCTEUR]) == False):
        raise ValueError("Erreur valeur non ASCII pour le nom du publisher : "+ params_msg[NOM_PRODUCTEUR])
    if(is_ascii(params_msg[LIGNE1_MSG]) == False):
        raise ValueError("Erreur valeur non ASCII pour le msg sur la ligne 1 : "+ params_msg[LIGNE1_MSG])
    if(is_ascii(params_msg[LIGNE2_MSG]) == False):
        raise ValueError("Erreur valeur non ASCII pour le msg sur la ligne 2 : "+ params_msg[LIGNE2_MSG])

    # Récupération date
    try: # Récupération de la date de diffusion
        date_diffusion = datetime.strptime(params_msg[DATE_DIFFUSION], "%Y-%m-%d %H:%M:%S")
        params_msg[DATE_DIFFUSION] = date_diffusion
    except ValueError as e:
       print("Erreur date de diffusion : " + str(e))
    try: # Récupération de la date d'expiration
        date_expiration = datetime.strptime(params_msg[DATE_EXPIRATION], "%Y-%m-%d %H:%M:%S")
        params_msg[DATE_EXPIRATION] = date_expiration
    except ValueError as e:
       print("Erreur date de péremption :" + str(e))

    try: # Récupération duree affichage
        duree_affichage = int(params_msg[DUREE_AFFICHAGE])
        params_msg[DUREE_AFFICHAGE] = duree_affichage
    except ValueError as e:
        print("Erreur format duree affichage :" + str(e))

    return params_msg

# Check si la date d'expiration n'est pas dépassee
def check_validite_msg(params_msg: list) -> bool:
    now = datetime.now()
    if(params_msg[DATE_DIFFUSION] < now and
        now < params_msg[DATE_EXPIRATION]):
        return True
    else:
        return False

def main():

    print("Creation ou recuperation de la queue, patienter... ")
    arduino.write("5Creation ou recuperation de la queue ;5patienter... ".encode())
   
    try:
        credentials = pika.PlainCredentials(username=username_queue, password=password_queue)
        credentials = pika.PlainCredentials(username=username_queue, password=password_queue)
        parameters = pika.ConnectionParameters(host=ip_rabbitMQ_service, 
                                            port=port_rabbitMQ_service,
                                            virtual_host=virtual_host,
                                            credentials=credentials)
        connection = pika.BlockingConnection(parameters)
        channel = connection.channel()
        channel.queue_declare(queue=queue_name)

        channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
        arduino.write("0Operationnel ;7en attente de message sur la queue ".encode())
        time.sleep(2)
    except Exception as e:
        print(e) 
        os._exit(0)
   
    print(' [*] Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()

# Récupère le port sur lequel est branché la arduino
def get_arduino_port():
    ports = list(serial.tools.list_ports.comports())
    for port in ports:
        if port.manufacturer is not None and "Arduino" in port.manufacturer:
            print(f"Arduino is connected on port: {port}")
            return port.device
    print("Could not find an Arduino connected to the system.")
    return None

def FermerDelapineur():
    if arduino is not None:
        arduino.close()
    try:
      sys.exit(0)
    except SystemExit:
        os._exit(0)

if __name__ == '__main__':
    try:
        # Remplacez 'COM3' par le nom du PORT_QUEUE_API série utilisé par votre carte Arduino
        arduino_port = get_arduino_port()
        if arduino_port is None:
            raise serial.SerialException("Pas de port usb trouvé avec une arduino branché dessus")
        arduino = serial.Serial(arduino_port, arduino_baud)
        # Attendre que la connexion soit établie
        time.sleep(5)
        print("Connexion arduino etablie attente de la queue...")
        arduino.write("5Connexion arduino etablie ;5attente de la queue... ".encode())
        time.sleep(5)

        main()
    except serial.SerialException as e:
        # print(e)
        FermerDelapineur()
    except KeyboardInterrupt:
        print('Interrupted')
        FermerDelapineur()
