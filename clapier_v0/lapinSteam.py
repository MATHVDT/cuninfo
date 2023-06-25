#!/usr/bin/env python
# Librairies
import pika, sys, os
import sys
import requests
from datetime import datetime, timedelta
import time
import requests
import steam.webauth as wa
import steam.webapi as api
import random

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

# variables
id_jeu_valheim = 892970
api_key = ""
steam_id = ""

TEMPS_AFFICHAGE=5
TEMPS_VALIDITE=60

def recup_username(api_key, steam_id_user):
    username = "Not found"
    # URL de l'API Steam pour obtenir les informations de l'utilisateur
    url_player_info = f"http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key={api_key}&steamids={steam_id_user}"
    # Faites une requête GET à l'API Steam pour obtenir les informations de l'utilisateur
    response = requests.get(url_player_info)
    data = response.json()

    if data.get("response"):
        player_info = data["response"]["players"][0]
        player_name = player_info["personaname"]
        username = player_name
    return username

def recup_liste_amis(api_key, steam_id):
    liste_amis = {}
    # URL de l'API Steam pour obtenir la liste d'amis
    url_friends = f"http://api.steampowered.com/ISteamUser/GetFriendList/v0001/?steamid={steam_id}&key={api_key}&relationship=friend"
    # Faites une requête GET à l'API Steam pour obtenir la liste d'amis
    response = requests.get(url_friends)
    data = response.json()

    if data.get("friendslist"):
        friends = data["friendslist"]["friends"]
        for friend in friends:
            # Obtenir l'ID Steam de l'ami
            friend_id = friend["steamid"]
            username = recup_username(api_key, friend_id)
            liste_amis[friend_id] = username
    return liste_amis

def copains_sur_un_jeu(api_key, liste_amis, id_jeu):
    nbAmis = 0
    for id_ami in liste_amis.keys():
        # URL de l'API Steam pour obtenir les infos sur l'ami
        url_info_ami = f"http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key={api_key}&steamids={id_ami}"
        # Faites une requête GET à l'API Steam pour obtenir les jeux possédés par l'ami
        response = requests.get(url_info_ami)
        info_ami = response.json()
        if info_ami.get("response"):
            # print(info_ami)
            if info_ami["response"]["players"][0].get("gameid"):
                if info_ami["response"]["players"][0]["gameid"] == str(id_jeu):
                    print(liste_amis[id_ami] + " est sur le jeu " + str(id_jeu))
                    nbAmis +=1
    return nbAmis

def creer_msg_joueur_sur_jeu(nb_joueur : int, nom_jeu : str):
    ligne1      = ["    VALHEIM     ", "   Par Odin !   ", "   Par Thor !   ", "Drakkar en mer !", "  Skal a toi !  ", "Fureur viking ! ", "Valhalla attend "]
    ligne2_sing = [" brave Viking  " , " fier guerrier "  , " fier guerrier "  , " copain en jeu " , " brave Nordique"]
    ligne2_plu = [" braves Vikings "  , " fiers guerriers" , " fiers guerriers" , " copains en jeu", " viking en jeu "]

    msg = ligne1[random.randint(0, len(ligne1))] + ";" 
    if(nb_joueur > 1):
        msg += ligne2_plu[random.randint(0, len(ligne2_plu))]
    else:
        msg += ligne2_sing[random.randint(0, len(ligne2_sing))]
    return msg 

def creer_msg_queue(message : str, duree_affichage: int, temps_validite: int):
    now = datetime.now()
    date_peremption = now + timedelta(seconds = temps_validite)
    date_envoie_str = now.strftime('%Y-%m-%d %H:%M:%S')
    date_peremption_str = date_peremption.strftime('%Y-%m-%d %H:%M:%S')
    return f"TCL;{date_envoie_str};{date_peremption_str};{duree_affichage};{message}"


def main(duree_script: int):
    # Connexion queue
    credentials = pika.PlainCredentials(username=usernameQueue, password=passwordQueue)
    parameters = pika.ConnectionParameters(host=ip_rabbitMQ_service,
                                           port=port_rabbitMQ_service,
                                           virtual_host=virtual_host,
                                           credentials=credentials)
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()

    liste_amis = recup_liste_amis(api_key=api_key, steam_id=steam_id)

    start_time_script = datetime.now()
    while(start_time_script + timedelta(minutes=duree_script) > datetime.now()):
        nb_copains_en_jeu = copains_sur_un_jeu(api_key=api_key, liste_amis=liste_amis, id_jeu=id_jeu_valheim)
        if(nb_copains_en_jeu > 0):
            msg = creer_msg_joueur_sur_jeu(nb_joueur=nb_copains_en_jeu, nom_jeu='Valheim')
            msg_queue = creer_msg_queue(msg, TEMPS_AFFICHAGE, TEMPS_VALIDITE)
            channel.basic_publish(exchange='',
                                routing_key=queue_name,
                                body=creer_msg_queue(message=" Bye Bye steam  ; Viking go dodo ", 
                                                    duree_affichage=10,
                                                    temps_validite=120))
            time.sleep(TEMPS_AFFICHAGE * 2)
        time.sleep(TEMPS_VALIDITE * 2)
   
    connection.close()

if __name__ == '__main__':
    try:
        duree_script = 60 # en minutes

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
