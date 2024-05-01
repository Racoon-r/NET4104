# NET4104 - Émission / réception sous GNU Radio
Projet NET4104 Télécom SudParis
1. Romain Moreau
2. Jeremy Lenoir
3. Valentin Lantigny
4. Alan Van Trigt

Dans le monde de la communication sans fil, la technologie Bluetooth Low Energy (BLE) a gagné en popularité en raison de sa faible consommation d'énergie et de sa large gamme d'applications. La possibilité de reproduire la chaîne de transmission BLE pour comprendre et manipuler les signaux émis est d'un intérêt particulier pour de nombreux domaines, de la domotique à l'Internet des Objets.

Dans cette étude, notre objectif est de comprendre comment récupérer et décoder un signal émis par un module ESP32 en utilisant le protocole BLE sur le canal de publicité (channel advertising) n°37. Cette tâche peut sembler complexe, mais en décomposant le processus en différentes étapes et en utilisant les outils appropriés, nous pouvons explorer les mécanismes sous-jacents de cette transmission sans fil.

Notre plan de recherche se décompose en quatre grandes parties. Tout d'abord, nous explorerons l'utilisation d'Arduino et des échecs que nous avons eu avec, pour établir une base de compréhension de la communication BLE. Ensuite, nous nous tournerons vers Micropython, une autre plateforme populaire pour les microcontrôleurs, pour voir comment les mêmes concepts peuvent être appliqués dans un environnement différent.

Par la suite, nous aborderons l'utilisation de GNU Radio, un logiciel de traitement du signal et de communication, pour des analyses plus approfondies et une manipulation avancée des signaux BLE. Enfin, nous utiliserons Python, avec ses bibliothèques spécialisées, pour décoder le signal reçu.

Cette approche progressive nous permettra de couvrir un large éventail d'outils et de techniques, de la programmation embarquée à la manipulation avancée de signaux, dans le but ultime de maîtriser la reproduction et la compréhension de la chaîne de transmission Bluetooth Low Energy.

# Plan :
#   1. Arduino
#   2. Micropython
#   3. GNU Radio 
#   4. Python
# Conclusion









# Technologies utilisées
## GNU Radio

First flowgraph:

- Input: text file or PDF file.
- Byte stream (unsigned char).
- Packet of 35 bytes with 2 header bytes.
- GFSK modulation.

Parameters:

- Sample rate: 1 MHz or 2 MHz
- Frequency deviation: 50 kHz (according to `Bluetooth Core Specification V4.0`)
- Modulation index N = frequency_deviation / sample_rate
- BT (Gaussian filter bandwith): 0.5 (according to ` Bluetooth Core Specification V4.0`)
- Samples per symbol: BT / N
- Sensitivity (GFSK block): 2 * pi * frequency_deviation / sample_rate (according GNU Radio documentation)

## Emission/Reception BLE avec ESP32
Nous avons cherché à créer une architecture client-serveur en BLE avec l'ESP32. Lors de nos recherches nous avons rencontrés trois solutions potentiels. Nous détaillons ici les avantages et inconvénients de chacune de ces solutions.

### Arduino IDE 
Avantage : La liaison avec l'ESP32 est directement gérer au sein de l'IDE et on peut se baser sur des exemples existants.
Désavantage : Les librairies ne sont pas forcément tenus à jour.

### Micropython
Avantage : permet de travailler avec python qui est un langage plutôt facile d'utilisation.
Désavantage : Demande un travail de préparation assez conséquent, notament en important la librairie micropython sur l'ESP32.

### ESP-IDF
Avantage : Version native donc version la plus à jour
Désavantage : Programmation en C