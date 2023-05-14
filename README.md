# Présentation
Le but de l'exercice est d'écrire une application destinée à gérée informations des joueurs et tournois d'une association d'échec.
Cette application doit être dévelopée en suivant les principes MVC (modèles, vues, contrôleurs).

# Fonctionnement 
L'application repose sur deux modules principaux : 'loader.py' et 'messenger.py'. Ces sont respéctivement résponsables de la sauvegarde/chargement des données et de l'execution des instructions utilisateurs. Ces modules peuvent être considéré les modèles principaux de l'application.

Le fichier main_view.py' est résponsable de l'affichage de l'application et peut-être considéré comme la vue principale de l'application. 

Ces modèles et la vue principale sont mis à la disposition du 'chessmanager_main.py', contrôleur principale de l'application qui les transmets ensuites aux différents contrôleurs secondaire de l'application.

Les controleurs secondaires utilisé par l'application (player_controller, match_controller, turn_controller et tournament_controller) permettent la création et la gestion des tournois et joueurs. 

Chacun de ces contrôleurs est résponsable d'un modèle qui lui est propre et dépend de la vue principale pour afficher les informations transmises par la vue corréspondante au modèle gérée par le contrôleur en question.
Les différentes actions réalisables par ces contrôleurs sont déclarée dans le fichier config.py et enregistrée auprès du messenger de l'application pour être éxécutée sur commande.

D'autres paramètres sont présent dans le fichier config.py et permettent de modifier certain comportement de l'application (tel que le répertoire de sauvegarde des données, les noms de sauvegarde des bases de données ou le nombre de joueurs à afficher par page)

# Utilisation
## 1) Creer l'environnement virtuel
Ouvrez un terminal; 

Pour ouvrir un terminal sur Windows, pressez  touche windows + r et entrez cmd.

Sur Mac, pressez touche command + espace et entrez "terminal".

Sur Linux, vous pouvez ouvrir un terminal en pressant les touches Ctrl + Alt + T.

Placez-vous dans le dossier où vous souhaitez créer l'environnement (Pour plus de facilité aux étapes suivantes, il est recommandé de faire cette opération dans le dossier contenant le script à exécuté). Puis exécutez  à présent la commande : 

`python -m venv env
`

Une fois fait, un nouveau dossier "env" devrait être créé dans le répertoire, il s'agit de votre environnement virtuel.

## 2) Activer l'environnement virtuel

Une fois la première étape réalisée, vous pouvez à présent activer votre environnement.
Pour ce faire, dans le dossier ou l'environnement a été créé :


Ouvrez un terminal, rendez-vous au chemin d'installation de votre environnement puis exécutez la commande : 

- Windows (Cmd) : `env\Scripts\activate.bat`
- bash/zsh : `source venv/bin/activate`
- fish : `source venv/bin/activate.fish`
- csh/tcsh : `source venv/bin/activate.csh`
- PowerShell : `venv/bin/Activate.ps1`

Une fois fait, vous constatez que les lignes de votre cmd commencent à présent par "(env)", cela signifie que votre environnement est actif.

## 3) Installer les dépendances

Dans le même terminal qu'à l'étape précédente :

`pip install -r requirements.txt`

## 4) Executer le programme
Lors du premier lancement du script, il est important de suivre les étapes l'une après l'autre. Lors des exécutions suivantes, il est possible de réutiliser l'environnement créer précédemment. Pour ce faire, ne suivez que l'étape 2 (Activer l'environnement virtuel), vous pouvez alors simplement contrôler que les dépendances sont bien installées via la commande : `pip freeze`. Si toutes les dépendances sont bien présentes, il est possible de passer directement à l'exécution du script.

Dans le terminal ayant servi à l'activation de l'environnement virtuel, exécuter la commande : 

`python chessmanager_main.py`

# Output
Une fois l'exécution du script terminée, les informations recueillies sont sauvegardées sous forme de fichiers jsons dans un dossier à la racine de l'application. 

Les listes de joueurs et tournois enregistrés dans l'application sont disponible à la visualisation directement depuis l'application.
