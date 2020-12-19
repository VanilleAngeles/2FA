# 2FA
Double Authentification with PGP database
## Utilité
Un programme de double autehtification, lors d'un accès sécurisé à un site ou une application, permet de disposer d'une deuxième source pour confirmer l'avvès. Souvent utilisé sur un smartphone (Google Authenticator...)  ou une application Web indépendante (lastpass...), la solution distribuée ici utilise une base de données cryptée et un programme de décodage pour fournir le code final de déverrouillage de l'application ou du site sécurisé.

## Outillage
Le programlme est écrit en Python version 3.
Le cryptage utilise celui généralement fourni sur les machines Linux à savoir la commande **gpg**
Le GUI est ici en GTK+ (version 3)

## Construction
La distrinution est composée d'un répertoire principal et de trois sous-répertoires
Le répertoire principal contient le programme 
