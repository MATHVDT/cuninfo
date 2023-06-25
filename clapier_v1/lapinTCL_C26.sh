#!/bin/bash

## Param TCL
# USERNAME_TCL='' # Renseigner le username d'accès à l'API
# PASSWORD_TCL='' # Renseigner le password d'accès à l'API
base_url="https://download.data.grandlyon.com/ws/rdata/tcl_sytral.tclpassagearret/all.csv"

## Paramètre sur l'arrêt
id_arret=2042 # Montchat Pinel
nom_arret='Pinel'
ligne='C26A' # C26 direction Grange blanche

id_arret=35665 # Gare de Villerbanne
nom_arret='Gare Villerbanne'
ligne='T3' # 

id_arret=43119 # Montchat Place Ronde
nom_arret='Place ronde'
ligne='C26A' # C26 direction Grange blanche



ligne0="{$ligne} ${nom_arret}"

## Taper l'API TCL
# Création Url requête avec les paramètres
url=$base_url"?id__eq="$id_arret"&ligne__eq="$ligne"&type__eq=E"
# Execution de la requête
reponse_csv=$(curl -X GET -s -u $USERNAME_TCL:$PASSWORD_TCL $url)

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

Création du message à afficher
liste_messages=()
for index in "${!delaispassage[@]}"; do
    element="${delaispassage[${index}]}"

    if [[ $index -eq 0 ]]; then
        prefixe_ligne1="Prochain"
    elif [[ $index -eq 1 ]]; then
        prefixe_ligne1="Suivant"
    else
        prefixe_ligne1="Après"
    fi

    ligne1="${prefixe_ligne1} ${element}"
    message_complet=("${ligne0};${ligne1}")
    echo $message_complet
    ${PATH_LAPINE} -m "${message_complet}" -a 5 -x "$(date --date 'now + 1 minutes' +"%Y-%m-%d %H:%M:%S")"
done
