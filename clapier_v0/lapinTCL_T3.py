#!/usr/bin/env python
# Librairies
import pika, sys, os
import sys
import pandas as pd
import requests
import io
from datetime import datetime, timedelta
import math
import time

# Format du message : 
# nom_publisher
# date_envoie => %Y-%m-%d %H:%M:%S
# date_peremption => %Y-%m-%d %H:%M:%S.%3N"
# duree_affichage => en seconde
# ligne1_msg
# ligne2_msg
# Queue : format message 
MSG_TEST="Toto;2023-06-04 00:35:45;2024-06-04 00:35:45;5;Message ligne 1;Message ligne2"
FORMAT_MSG="nom_publisher;date_envoie(%Y-%m-%d %H:%M:%S);date_peremption(%Y-%m-%d %H:%M:%S);duree_affichage(secondes);ligne1_msg;ligne2_msg"

## Queue
# Queue parametre
ip_rabbitMQ_service="localhost"
port_rabbitMQ_service=5672
virtual_host="/"
queue_name=""
usernameQueue=""
passwordQueue=""

## Param TCL
usernameTCL=""
passwordTCL=""
base_url = "https://download.data.grandlyon.com/ws/rdata/tcl_sytral.tclpassagearret/all.csv"
authTCL = (usernameTCL, passwordTCL)

secondes_entre_2_requetes = 60 # secondes
duree_affichage = 5
nb_message_envoye = secondes_entre_2_requetes / duree_affichage
# id_arret= 85 # Aubepin
# nom_arret = "Aubepin"
# ligne = "C26A" # C26 direction Grange blanche

id_arret= 35665 # Montchat Pinel
nom_arret = "Villeurbanne"
ligne = "T3" 


# Fait la requete pour obtenir les données d'un arrêt et d'une ligne
# Renvoie un tab a 2 dim avec 1ere dim = nom du champ et 2eme valeur (un peu dico mais appelé ici DataFrame)
def GetDataTCL(auth, id_arret, ligne, type = "E"):
    param = f"id__eq={id_arret}&ligne__eq={ligne}&type__eq=E"
    param_csv="maxfeatures=-1&ds=.&separator=;&start=1"
    url = base_url + "?" + param + "&" + param_csv
    response = requests.get(url, auth=auth)
    text_csv = response.text
    return pd.read_csv(io.StringIO(text_csv), sep=";").sort_values("heurepassage")


# Créer message
def creer_message_delaipassage(data, nom_arret):
    liste_msg = []
    lenMaxLigne = 16
    # Creation de l'entete du message
    space = ' ' * (lenMaxLigne - len(data["ligne"][0]) - len("arret ") - len(nom_arret))
    titreLigne = data["ligne"][0] + space + "arret " + nom_arret + ";"

    for index, passage in data.iterrows():
        if index == 0:
            texte = "Prochain "
        elif index == 1:
            texte = "Suivant "
        else:
            texte = "Apres "

        # Date et heure spécifiée au format "AAAA-MM-JJ HH:MM:SS"
        date_passage_str = passage['heurepassage']
        # Conversion de la chaîne de caractères en objet datetime
        date_passage = datetime.strptime(date_passage_str, "%Y-%m-%d %H:%M:%S")
        # Obtenir l'heure actuelle
        now = datetime.now()
        # Calculer la différence de temps en secondes
        delta_seconds = (date_passage - now).total_seconds()
        # Convertir la différence de temps en minutes et donne un string
        delta_minutes_str = str(math.floor(delta_seconds / 60)) # Arrondi à l'inférieur
        
        space = ' ' * (lenMaxLigne - len(texte) - len(delta_minutes_str) - len(" min"))
        liste_msg.append(titreLigne + texte + space + delta_minutes_str + " min")
    return liste_msg


def creer_msg_queue(message : str, duree_affichage : int, temps_validite : int):
    now = datetime.now()
    date_peremption = now + timedelta(seconds = temps_validite)
    date_envoie_str = now.strftime('%Y-%m-%d %H:%M:%S')
    date_peremption_str = date_peremption.strftime('%Y-%m-%d %H:%M:%S')
    return f"TCL;{date_envoie_str};{date_peremption_str};{duree_affichage};{message}"

def main(duree_script: int):
    # Connexion queue
    credentials = pika.PlainCredentials(username="tcl", password="tcl")
    parameters = pika.ConnectionParameters(host=ip_rabbitMQ_service,
                                           port=port_rabbitMQ_service,
                                           virtual_host=virtual_host,
                                           credentials=credentials)
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()

    start_time_script = datetime.now()
    while(start_time_script + timedelta(minutes=duree_script) > datetime.now()):
        data = GetDataTCL(auth=authTCL, id_arret=id_arret, ligne=ligne)
        msg_delai = creer_message_delaipassage(data=data, nom_arret=nom_arret)
        for i in range(0, int(nb_message_envoye/len(msg_delai))):
            for m in msg_delai:
                msg_queue=creer_msg_queue(message=m, duree_affichage=duree_affichage, temps_validite=duree_affichage * 2)
                channel.basic_publish(exchange='',
                                      routing_key=queue_name,
                                      body=msg_queue)
                time.sleep(duree_affichage)
        # time.sleep(secondes_entre_2_requetes)

    channel.basic_publish(exchange='',
                        routing_key=queue_name,
                        body=creer_msg_queue(message="  Bye Bye  TCL  ;                ", 
                                             duree_affichage=10,
                                             temps_validite=120))
    connection.close()

if __name__ == '__main__':
    try:
        duree_script = 10 # en minutes

        if len(sys.argv) > 1:
            arg = sys.argv[1]
            if arg.isdigit():
                arg_int = int(arg)
                if arg_int > 0:
                    duree_script = arg_int

        print(f"Durée du script : {duree_script}  minute")
        main(duree_script)

    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
