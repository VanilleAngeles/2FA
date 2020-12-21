# 2FA
Double Authentification with PGP database  
![Interface](http://pix.toile-libre.org/upload/original/1608540219.png)

## Utilité
Un programme de double autehtification, lors d'un accès sécurisé à un site ou une application, permet de disposer d'une deuxième source pour confirmer l'accès. Souvent utilisé sur un smartphone (Google Authenticator...)  ou une application Web indépendante (lastpass...), la solution distribuée ici utilise une base de données cryptée et un programme de décodage pour fournir le code final de déverrouillage de l'application ou du site sécurisé.

## Outillage
Le programme est écrit en Python version 3.
Le cryptage utilise celui généralement fourni sur les machines Linux à savoir la commande **gpg**
Le GUI est ici en GTK+ (version 3)

## Construction
La distribution est composée d'un répertoire principal et de trois sous-répertoires.
Le répertoire principal contient le programme et le fichier de configuration *.ini*.
Le répertoire *Backup* contient les sauvegardes des fichiers cryptés avant chaque *save*
Le répertoire *Data* contient la feuille de style et la base cryptée.
Le répertoire *Pictures* contient les images, en particulier les icones qui seront afficheés.

## intialisation
### Création clé PGP
Il existe des interfaces graphiques pour générer des clés PGP mais comme elles sont souvent différentes les unes des autres suivant l'OS utilisé, je recommande la ligne de commande sous Terminal.
Si on ne dispose pas de clé PGP, entrer la commande  
`gpg --full-generate-key`  
Conseils de paramétrages : on laisse tout à défaut: RSA - 3072 - 0 (infinite) - PrénomNom - @mail et là on met son mot de passe
### Fichier paramètres (2FA.ini)
Il est documenté et ne nécessite aucune modification si les valeurs par défaut sont conservées. Le nom logique $HOME représente le $HOME de l'utilisateur courant Linux, le nom logique $CURRENT représente le répertoire où se trouve le programme principal en Python (2FA.py). On peut changer les répertoires, les langues, les traductions, la taille de l'affichage de la fenêtre des codes...
### Création d'un fichier crypté vide
En Terminal, se positionner sur le répertoire Data et entrer la commande en mettant le mot de passe de la clé PGP  
`gpg -e -r **adresse mail de la clé PGP** -v totp.json`  
le fichier totp.json est vide, la base cryptée le sera donc aussi. Si on veut nommer différemment la base cryptée, ne pas oublier de modifier le fichier 2FA.ini.

## Bibliothèques Python à installer
### famille Debian (Debian, Ubuntu, Mint...)
Installer pip3  
`sudo apt-get install python3-pip`  
Installer les bibliothèques nécessaires au programme python  
`sudo pip3 install python-gnupg mintotp`
### famille Arch Linux (Arch Linux, Manjaro...)
Installer pip3  
`sudo pacman -Sy python-pip`  
Installer les bibliothèques nécessaires au programme python  
`sudo pip3 install python-gnupg mintotp`  
### famille RedHat (RedHat, Centos, Fedora,Oracle Linux...)
Installer pip3 (à verifier)  
`sudo dnf install python-pip`  
Installer les bibliothèques nécessaires au programme python  
`sudo pip3 install python-gnupg mintotp`

## Lancement
On peut lancer le programme 2FA.py soit en mode terminal (python3 2FA.py), soit en créant un lanceur sur son bureau, soit en utilisant l'intégration dans le menu (Cinnamon), soit en utilisant le lanceur Argos (Gnome).

## Utilisation
Le premier lancement demande le mot de passe de la clé PGP.
Ensuite apparaiît la fenêtre principale qui se décompose comme suit:
- le menu Application dans la barre de titres (parfois un logo comme sous Fedora). Là et seulement là il est possible d'ajouter un enregistrement (add)
- ajout d'enregistrement. Seront demandés le site, l'utilisateur et la clé. Si les données sont valides, le nouvel item apparaitra à la fin de la fenêtre des codes
- la barre de progression. Il est rappelé que le principe de double authentification fournit toutes les 30 seconds un code qui est calculé à partir de la clé du site et de l'heure
- la fenêtre des codes qui est en défilement (cf paramètres). Chaque ligne est composée du logo de l'application, de son nom et son utilisateur (inutile dans le codage mais utile si plusieurs comptes sur la même application), le code généré toutes les 30 secondes (cliquer dessus met la valeur dans le presse-papier) et la corbeille qui supprime l'enregistrement  
**IMPORTANT** Toutes les modifications sont effectuées en mémoire. Les données seront sauvées dans le fichier crypté qu'avec la fonction *Save* du menu application ou du bouton qui apparait dans la fenêtre principale quand les données ont été modifiées (add ou delete).

## Images et Logo
Le répertoire des images contient les logos des applications nécessitant une double authentification.
Leur nommage est strict: le nom doit être en minuscule, doit reprendre exactement le nom du site à protégéer, est en format png. Pour une meilleure définition un format 128x128 ou 256x256 est conseillé. Dans le répertoire des images existe un programme python (favicon.py) qui tente de récupérer les favicon des sites si ils existent et accessibles. Ce programme est au titre d'utilitaire mais n'a aucune garantie.
exemple correct  
  --> amazon.png pour le site Amazon  
exemple incorrect  
  --> Amazon.png pour Amazon  
  --> amazon.png pour AmazonWebService  
Si un  logo n'esite pas, le programme le rempace pas son initiale (A dans le cas précédent).

*Aide éditeur Markdown  *[Lien](https://www.ionos.fr/digitalguide/sites-internet/developpement-web/markdown/).
