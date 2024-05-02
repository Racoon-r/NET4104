# Projet NET4104 - Réception d'un signal BLE émis par ESP32 sur le channel 37

Projet s'inscrivant dans le cours NET4104 à Télécom SudParis. 
**Auteurs :**
- Valentin LANTIGNY ; 
- Jeremy LENOIR ;
- Romain MOREAU ;
- Alan VAN TRIGT.

**Encadrant :** 
- Rémy GRUNBLATT.

## Introduction

Dans le monde de la communication sans fil, la technologie Bluetooth Low Energy (BLE) a gagné en popularité en raison de sa faible consommation d'énergie et de sa large gamme d'applications. La possibilité de reproduire la chaîne de transmission BLE pour comprendre et manipuler les signaux émis est d'un intérêt particulier pour de nombreux domaines, de la domotique à l'Internet des Objets.

Dans cette étude, notre objectif est de comprendre comment récupérer et décoder un signal émis par un module ESP32 en utilisant le protocole BLE sur le canal de publicité (channel advertising) n°37. Cette tâche peut sembler complexe, mais en décomposant le processus en différentes étapes et en utilisant les outils appropriés, nous pouvons explorer les mécanismes sous-jacents de cette transmission sans fil.

Notre plan de recherche se décompose en trois grandes parties. Tout d'abord, nous explorerons des interfaces codes hardware. Par la suite, nous aborderons l'utilisation de GNU Radio, un logiciel de traitement du signal et de communication, pour des analyses plus approfondies et une manipulation avancée des signaux BLE. Enfin, nous utiliserons Python, avec ses bibliothèques spécialisées, pour décoder le signal reçu.

Cette approche progressive nous permettra de couvrir un large éventail d'outils et de techniques, de la programmation embarquée à la manipulation avancée de signaux, dans le but ultime de maîtriser la reproduction et la compréhension de la chaîne de transmission Bluetooth Low Energy.

# 1. Choix des technologies
Émission/Réception BLE avec ESP32
Lors de notre exploration pour créer une architecture client-serveur en Bluetooth Low Energy (BLE) avec l'ESP32, nous avons identifié trois solutions potentielles. Dans cette section, nous détaillons les avantages et les inconvénients de chacune de ces solutions.

Arduino IDE
Avantage : La liaison avec l'ESP32 est directement gérée au sein de l'IDE, offrant ainsi une facilité d'utilisation et la possibilité de se baser sur des exemples existants pour démarrer rapidement.

Désavantage : Cependant, les librairies disponibles peuvent ne pas être toujours tenues à jour, ce qui peut poser des problèmes de compatibilité avec les versions plus récentes de l'ESP32 ou avec d'autres composants.

Micropython
Avantage : Micropython offre la possibilité de travailler avec Python, un langage largement utilisé et apprécié pour sa simplicité et sa lisibilité. Cela peut faciliter le développement et la maintenance du code pour certains utilisateurs.

Désavantage : Cependant, l'utilisation de Micropython demande un travail de préparation assez conséquent, notamment en ce qui concerne l'importation de la librairie Micropython sur l'ESP32, ce qui peut ajouter une étape supplémentaire dans le processus de développement.

ESP-IDF
Avantage : L'ESP-IDF (Espressif IoT Development Framework) est la solution native pour le développement sur les microcontrôleurs ESP32, offrant ainsi une compatibilité et une intégration optimales avec les fonctionnalités matérielles de ces dispositifs. De plus, en tant que version officielle, elle est souvent la plus à jour.

Désavantage : Cependant, la programmation en C, utilisée dans l'ESP-IDF, peut être considérée comme plus complexe pour certains développeurs habitués à des langages de haut niveau comme Arduino ou Python.

###   2. GNU Radio 

Pour recevoir un signal Bluetooth Low Energy, la première étape va être de recevoir et démoduler les données. Pour ce faire, une antenne connectée à un HackRF comportant un oscillateur intégré (40 MHz) va permettre la bonne réception du signal et l'outil GNU Radio permettra d'effectuer la démodulation pour obtenir les données transmises.

Pour les caractéristiques techniques, la documentation `Bluetooth Core Specification v5.3` est utilisé comme référence. Dans le cadre du projet, seul le `canal 37 Advertising` sera étudié pour simplifier les démarches, celui-ci étant à la fréquence $f = 2.402 \ GHz$.
Le BLE utilisé également 40 canaux de 2 MHz de large, il faudra donc une fréquence d'échantillonnage $f_{e} = 4 MHz$ pour satisfaire le théorème de Nyquist-Shannon.  

Le HackRF [^1] est un émetteur - récepteur de la marque Great Scott Gadgets opérant de 1 MHz à 6 GHz. Comme plusieurs systèmes d'échantillonnage en quadrature, il peut présenter un _DC Offset_ : c'est un pic au centre du spectre causé par un biais interne. Pour faire face à ce problème, le choix retenu est de régler le HackRF sur une fréquence $f + \delta f$ puis d'effectuer un décalage fréquentiel de $-\delta f$ pour revenir au cadre d'étude [^2], ici, il sera fixé à $\delta f = 1.5 \ MHz$. Par ailleurs, les données sont au format I/Q (type *complex - float32*).

Le logiciel GNU Radio permet de traiter le signal, notamment pour moduler et démoduler. Deux types de données seront utilisés : les *complex Float 32* en sortie du HackRF, et des *bytes* après démodulation. 

**Réception et filtrage**
 Sous GNU Radio, le bloc `RTL-SDR Source` va permettre de recevoir le signal BLE. Il est réglé avec une fréquence $f = 2.0435 \ GHz$, et une fréquence d'échantillonnage $f_e = 4 \ MHz$.
Le décalage fréquentiel pour recentrer le signal est opéré par le bloc `Frequency Xlating FIR Filter`, et un `Simple Squelch` permet de traiter les données uniquement quand la puissance moyenne est supérieure à -80 dBm, ceci pour éviter d'avoir trop d'informations.

Enfin, un deuxième `Frequency Xlating FIR Filter` va servir cette fois de filtre passe-bande pour garder l'information sur 2 MHz. 

**Démodulation**
Le Core v5.3 décrit les paramètres principaux de la modulation GFSK.
Supposant un signal message $m$ à transmettre, sur une fréquence $f_m$ et d'amplitude $A_m$,  ainsi que le signal modulé $s_{FM}$ à une fréquence $f_c$ et une amplitude $A_c$. 
Il vient alors :

$$\begin{align*}
\begin{dcases}
{m(t) = A_m cos(2 \pi f_m t)} \\
{s_{FM}(t) = A_c cos[2\pi f_c t + \beta_f sin(2 \pi f_mt)]} \\
{\beta_f = \frac{k_f A_m}{2 \pi f_m}}
\end{dcases}
\end{align*}$$

$k_f$ est la sensibilité de la modulation, définis par $k_ f = \frac{2 \pi \Delta f_{max}}{A_m}$.

À noter que si $\beta_f$ << 1, la modulation est appelée Narrow Band Frequency Modulation (NBFM), et pour ($\beta_f$ > 1) elle est appelée Wideband Frequency Modulation (WBFM).

Pour démoduler le signal, il va falloir une boucle à verrouillage de phase, mais elle ne sera pas étudiée ici. Il existe en effet un bloc `GFSK Demod`, lui-même composé de trois autres blocs : un `Quadrature Demod`, un `Symbol Sync` et un `Binary Slicer`. Les deux premiers permettent de démoduler en quadrature (car la modulation fréquentielle est une modulation de phase) et de synchroniser l'horloge. Le dernier bloc lui permet d'obtenir uniquement des bits (0 ou 1).

Ici, pour plus de simplicité, ce sera le bloc `GFSK Demod` qui sera utilisé. Il y a seulement deux variables à changer :  le `Samples/Symbol`, défini comme le rapport de la fréquence d'échantillonnage sur le débit symbole : 
$$\begin{align*}
sps = \frac{f_e}{D_s},
\end{align*}$$

et la `Sensitivity`, représentant l'écart possible de fréquence lors de la modulation :
$$\begin{align*}
s = \frac{\pi}{2} \frac{1}{sps}.
\end{aign*}$$

La synchronisation d'horloge n'est pas étudiée ici, les valeurs sont celles par défaut. Cela correspond à l'algorithme de Mueller & Muller.

Pour le BLE, l'envoi de donnée commence toujours par le bit de poids faible. C'est le rôle des deux derniers blocs, `Unpacked to Packed` et `File Sink` permettant d'obtenir une suite de byte dans un fichier suivant la convention _Petit Boutiste_. 

Pour visualiser la réception (et donc voir quand une trame Bluetooth est reçu), un bloc `QT GUI Frequency Sink` permettra de voir le spectre du signal en temps réel ainsi que le signal retenu (_i.e._ quand sa valeur moyenne est à plus de -80 dBm), et un bloc `QT GUI Time Sink` permet de voir les bits.
 
[^1]: HackRF: https://greatscottgadgets.com/hackrf/one/
[^2]: DC offset : https://hackrf.readthedocs.io/en/latest/faq.html#bigspike.

###   3. Python












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



# Conclusion
