# !/bin/bash
#----------------------------------------------#
# Ce script envoie l'heure actuelle sur le
# script lapine.sh pour un affichage d'une min
#----------------------------------------------#

# PATH_LAPINE='' # Chemin du script qui permet d'envoyer dans la file le message
LANG=fr_FR.UTF-8

jour="$(date +"%A %d %b")"
jour=${jour::-1} # Supprime la dernière le . de l'abréviation du mois
heure="$(date +%R)"

# Calcule le nombre d'espace nécessaire pour que la ligne fasse 16 caracères
espace_date=$((16 - ${#heure}))
espace_date=$((space_needed_date / 2))

# Créée la ligne de 16 caractères
ligne0="$(printf "%*s%s%*s" "$espace_date" "" "$jour" "$espace_date" "")"
ligne1="$(printf "%*s%s%*s" "5" "" "$heure" "5" "")"
message_complet="${ligne0};${ligne1}"

${PATH_LAPINE} -m "${message_complet}" -a 5 -x "$(date --date 'now + 1 minutes' +"%Y-%m-%d %H:%M:%S")"
