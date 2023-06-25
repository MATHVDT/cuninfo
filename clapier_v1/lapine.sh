#!/bin/bash

## Renseigner les paramètres le script .env n'a pas été lancé
# IP_QUEUE='localhost'
# PORT_QUEUE_API='15672'
# QUEUE_NAME='arduino'
# URL_QUEUE="http://${IP_QUEUE}:${PORT_QUEUE_API}/api/exchanges/%2F/amq.default/publish"
# USERNAME_LAPINE_QUEUE=''
# PASSWORD_LAPINE_QUEUE=''

# Format du message :
# nom_producteur => lapin qui envoie le msg
# date_envoie => au format : %Y-%m-%d %H:%M:%S
# date_peremption => au format : %Y-%m-%d %H:%M:%S.%3N"
# duree_affichage => en seconde
# ligne1_msg
# ligne2_msg

# Queue : format message
# MSG_TEST="lapinTest;2023-06-04 00:35:45;2024-06-04 00:35:45;5;Message ligne 1;Message ligne2"
# FORMAT_MSG="nom_producteur;date_envoie(%Y-%m-%d %H:%M:%S);date_peremption(%Y-%m-%d %H:%M:%S);duree_affichage(secondes);ligne1_msg;ligne2_msg"

parent_name=$(ps -o comm= -p $PPID)

DEFAUT_PRODUCTEUR=${parent_name}
DEFAUT_DATE_DIFFUSION=$(date +"%Y-%m-%d %H:%M:%S")
DEFAUT_DATE_EXPIRATION=$(date --date 'now + 5 minutes' +"%Y-%m-%d %H:%M:%S")
DEFAUT_DUREE_AFFICHAGE=5
DEFAUT_MESSAGE="                ;                "

producteur=${DEFAUT_PRODUCTEUR}
date_diffusion=${DEFAUT_DATE_DIFFUSION}
date_expiration=${DEFAUT_DATE_EXPIRATION}
duree_affichage=${DEFAUT_DUREE_AFFICHAGE}
message=${DEFAUT_MESSAGE}

while getopts ":p:m:a:d:x:" opt; do
    case $opt in
    p)
        producteur="$OPTARG"
        ;;
    m)
        message="$OPTARG"
        ;;
    a)
        duree_affichage="$OPTARG"
        ;;
    d)
        date_diffusion="$OPTARG"
        ;;
    x)
        date_expiration="$OPTARG"
        ;;
    \?)
        echo "Option invalide: -$OPTARG" >&2
        ;;
    esac
done

# Vérifier si le paramètre message est spécifié (obligatoire)
if [[ -z $message ]]; then
    echo "Le paramètre -m (message) est obligatoire."
    exit 1
fi

## Afficher les paramètres spécifiés
# echo "Producteur: $producteur"
# echo "Date de diffusion: $date_diffusion"
# echo "Date d'expiration: $date_expiration"
# echo "Durée d'affichage: $duree_affichage"
# echo "Message: $message"

# Création du message avec les méta-données pour la queue
message_complet="${producteur};${date_diffusion};${date_expiration};${duree_affichage};${message}"

## Publication du message
# Via requête CURL
reponse_code=$(curl \
    -s -o /dev/null -w "%{http_code}" \
    --location "${URL_QUEUE}" \
    --header "Content-Type: application/json" \
    --user "${USERNAME_LAPINE_QUEUE}:${PASSWORD_LAPINE_QUEUE}" \
    --data "{
    \"properties\": {},
    \"routing_key\": \"${QUEUE_NAME}\",
    \"payload\": \"${message_complet}\",
    \"payload_encoding\": \"string\"
}")

# Via cmd rabbit
# reponse_code=$(rabbitmqadmin --host=${IP_QUEUE} --PORT_QUEUE_API=${PORT_QUEUE_API} --username=${USERNAME} publish routing_key=${QUEUE_NAME} payload=${message_complet})

if [ $? -eq 0 ] && [ $reponse_code -eq 200 ]; then
    echo "Success (${reponse_code}) : msg = \"${message_complet}\" -> url = \"${URL_QUEUE}\""
else
    echo "Failure (${reponse_code}) : msg = \"${message_complet}\" -> url = \"${URL_QUEUE}\""
fi
