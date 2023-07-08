#!/bin/bash

## Param TCL
# USERNAME_TCL='' # Renseigner le username d'accès à l'API
# PASSWORD_TCL='' # Renseigner le password d'accès à l'API
base_url="https://download.data.grandlyon.com/ws/rdata/tcl_sytral.tclpassagearret/all.csv"

# PATH_LAPINE='' # Chemin du script qui permet d'envoyer dans la file le message

## Paramètre sur l'arrêt
id_arret='' # Id de l'arrêt, à trouver sur https://data.grandlyon.com/jeux-de-donnees/points-arret-reseau-transports-commun-lyonnais/donnees
nom_arret='' # Rentrer manuellement le nom de l'arrêt   
ligne='' # Nom de la ligne commercial donné sur le champ "ligne" de la requête faite à l'API. 
         # Par exemple pour la ligne C26 direction Grange blanche se sera "C26A", pour la ligne T3 dans les 2 directions se sera "T3"


ligne0="${ligne} ${nom_arret}"

## Taper l'API TCL
# Création Url requête avec les paramètres
url=$base_url"?id__eq="$id_arret"&ligne__eq="$ligne"&type__eq=E"
# echo $url

# Execution de la requête
reponse_csv=$(curl -X GET -s -u $USERNAME_TCL:$PASSWORD_TCL $url)
# echo $reponse_csv

## Traitement de la réponse
reponse_csv_lignes=() # Initialisation du tableau

# Lire chaque ligne de la reponse_csv et les stocker dans le tableau
while IFS= read -r ligne; do
    reponse_csv_lignes+=("$ligne")
done <<<"$reponse_csv"

unset "reponse_csv_lignes[0]" # Supprimer la première ligne du tableau pour virer les noms des colonnes

# Processer les éléments du tableau (chaque ligne) pour extaire juste le delai de passage
delaispassage=()
for element in "${reponse_csv_lignes[@]}"; do
    # echo "$element" # Afficher la ligne
    delaispassage+=("$(echo "$element" | cut -d ';' -f 4)")
done

# Création du message à afficher
liste_messages=()
for index in "${!delaispassage[@]}"; do
    delai="${delaispassage[${index}]}"

    if [[ $index -eq 0 ]]; then
        prefixe_ligne1="Prochain"
    elif [[ $index -eq 1 ]]; then
        prefixe_ligne1="Suivant"
    else
        prefixe_ligne1="Après"
    fi
    # Calcule le nombre d'espace nécessaire pour que la ligne fasse 16 caracères
    spaces_needed=$((16 - ${#prefixe_ligne1} - ${#delai}))
    # Créée la ligne de 16 caractères
    ligne1="$(printf "%s%*s%s" "$prefixe_ligne1" "$spaces_needed" "" "$delai")"

    message_complet="${ligne0};${ligne1}"
    ${PATH_LAPINE} -m "${message_complet}" -a 5 -x "$(date --date 'now + 1 minutes' +"%Y-%m-%d %H:%M:%S")"
done

