# NET4104 - Émission / réception sous GNU Radio
Projet NET4104 Télécom SudParis
1. Romain Moreau
2. Jeremy Lenoir
3. Valentin Lantigny
4. Alan Van Trigt

# Objectif : Reproduire la chaîne de transmission BLE
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