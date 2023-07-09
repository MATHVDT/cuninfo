#!/bin/bash
#----------------------------------------------#
# Ce script permet de checker si vos amis sont
# actuellement sur un jeu spécifié, et envoie
# un message via le scrip lapine.sh pour
# sur la queue
#----------------------------------------------#

## Param Steam
# NOM_JEU_STEAM='' # Remplacez par le nom du jeu
# ID_JEU_STEAM=''  # Rempalcez par l'id de votre jeu
# API_KEY_STEAM='' # Remplacez par votre clé d'API Steam
#                  # Demande de clé API Steam ici https://steamcommunity.com/dev/apikey, et mettre localhost comme nom de domaine
# STEAM_ID_USER='' # Remplacez par votre ID Steam

# PATH_LAPINE='' # Chemin du script qui permet d'envoyer dans la file le message

# Récuperer la liste des amis
URL_LISTE_AMIS="http://api.steampowered.com/ISteamUser/GetFriendList/v0001/?steamid=${STEAM_ID_USER}&key=${API_KEY_STEAM}&relationship=friend"

if [ -z $LISTE_ID_AMIS_STEAM ]; then
    response_liste_amis=$(curl -X GET -s $URL_LISTE_AMIS)

    # Formate la liste d'amis sur 1 seule ligne avec ',' comme séparateur des ids
    LISTE_ID_AMIS_STEAM=$(echo "$response_liste_amis" | grep -o '"steamid":"[^"]*' | grep -o '[^"]*$' | tr '\n' ',')
fi

# Récup info sur le user
BASE_URL_INFO_USER="http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key=${API_KEY_STEAM}"
url_info_user=$BASE_URL_INFO_USER"&steamids=${LISTE_ID_AMIS_STEAM}"
response_info_amis=$(curl -X GET -s $url_info_user)

# Check s'il a un jeu en cours et si celui correspond au jeu spécifié
nb_amis_en_jeu=$(echo "$response_info_amis" | grep -o '"gameid":"[^"]*' | grep -o '[^"]*$' | grep -o "${ID_JEU_STEAM}" | wc -w)

if [ $nb_amis_en_jeu -gt 0 ]; then
    # Création du message
    message_complet=""${NOM_JEU_STEAM}" :;$nb_amis_en_jeu joueur(s)"
    echo "$message_complet"
    # Envoie du message
    ${PATH_LAPINE} -m "${message_complet}" -a 5 -x "$(date --date 'now + 5 minutes' +"%Y-%m-%d %H:%M:%S")"
fi
