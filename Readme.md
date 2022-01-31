# Mini-Praktikum: Venen Funktionsmessung mittels PPG
Bei der venösen Photoplethysmographie wird die Lichtreflexion (Synonym: Licht-Reflexions-Rheographie, LRR)
mittels eines PPG-Sensors gemessen. Da Licht von Blut stärker als vom Gewebe absorbiert wird, nimmt
die Lichtreflexion bei steigendem Blutvolumen im Bein ab. Das LRR-Signal spiegelt daher Blutvolumenschwankungen wider.
Das LRR-Signal gliedert sich in einen gleich bleibenden Anteil durch Lichtabsorption in „undurchblutetem“ Gewebe 
(ca. 90 %), eine variable Lichtabsorption durch das venöse Blutvolumen (ca. 10 %) und eine periodische arterielle 
Lichtabsorption (ca. 0,5 %). Mithilfe digitaler Filtertechniken können diese Signale voneinander getrennt werden 
(digitale Photoplethysmographie, dPPG) [[1]](https://docplayer.org/21805396-Phlebologische-funktionsdiagnostik.html).

## Durchführung der Messung

Der sitzende Patient führt acht Dorsalextensionen im Sprunggelenk innerhalb von 16 Sekunden im Metronomrhythmus durch. Die Ferse ist dabei am Boden
abgestützt. Der PPG-Sensor wird mithilfe des 3D gedruckten Gehäuses ca. 10 cm oberhalb des Malleolus medialis angebracht (Abbildung 1). 

<img src="https://github.com/Gruftgrabbler/Ambient_Intelligence_PPG/blob/main/images/Durchf%C3%BChrung%20der%20dPPG-Messung.png" width="421" height="329">

**Abbildung 1:** Empfohlene Körperhaltung während der Messdurchführung [[2]](https://www.researchgate.net/publication/6482990_Photoplethysmography_and_its_application_in_clinical_physiological_measurement)

Die Fußbewegung führt zur Kompression der Beinvenen und damit zu einem Bluttransport nach proximal (Muskelpumpe). Das abnehmende Blutvolumen
spiegelt sich in der LRR-Kurve durch eine zunehmende Lichtreflexion wider (Abbildung 2). Nach Beendigung der Fußbewegungen fließt das 
Blut wieder nach distal. Bei insuffizienten Venen geschieht das schneller, als bei suffizienten Venenklappen 
[[1]](https://docplayer.org/21805396-Phlebologische-funktionsdiagnostik.html).

![Mustermessung](https://media.springernature.com/original/springer-static/image/chp%3A10.1007%2F978-3-642-23804-8_36/MediaObjects/67823_2_De_36_Fig4_HTML.gif)

**Abbildung 2:** LRR-Kurve mit zunehmender Lichtreflexion während der Fußbewegungen  [[3]](https://link.springer.com/chapter/10.1007/978-3-642-23804-8_36)

Der Messzyklus läuft vollautomatisch ab, die Messsignale werden ebenfalls automatisch ausgewertet.
Erfasst werden folgende Parameter zur unterstützenden Diagnostik der Venenfunktion:
* Venöse Wiederauffüllzeit <img src="https://render.githubusercontent.com/render/math?math=T_0">
* Venöse Halbwertszeit <img src="https://render.githubusercontent.com/render/math?math=T_{50}">
* Initiale Auffüllzeit <img src="https://render.githubusercontent.com/render/math?math=T_i">
* Venöse Pumpleistung <img src="https://render.githubusercontent.com/render/math?math=V_0">
* Venöse Pumparbeit <img src="https://render.githubusercontent.com/render/math?math=F_0">


## Vorverarbeitung der Daten

Der MAX30102 PPG-Sensor enthält zwei Leuchtdioden (LEDs), eine infrarote LED (Spitzenwellenlänge 880 nm) und eine rote LED (Spitzenwellenlänge 660 nm); dazu kommt eine Photodiode, die spezifisch für Wellenlängen zwischen 600 und 900 nm ausgelegt ist. Im MAX30102 Sensor ist ein integrierter Temperatursensor zur Messung von Temperaturschwankungen, ein Analog-Digital Wandler (ADC) und eine I2C-Schnittstelle. Durch die Integration des ADC und der I2C-Schnittstelle in den Sensor selbst werden Rauschen und Artefakte, die zwischen der Fotodiode und dem ADC entstehen, auf ein Minimum reduziert. Außerdem werden die vom Sensor gemessenen Werte mit einer Prüfsumme übertragen, so dass die Gültigkeit der Daten die Gültigkeit der Daten beim Empfang durch den unterstützenden Mikrocontroller überprüft wird. Die Firmware für den Mikrocontroller wurde so entwickelt, dass der I2C-Multiplexer durch die einzelnen I2C-Kanäle schaltet und den Wert jedes Lese- und Schreibzeigers des PPG-Sensors liest. Eine Diskrepanz zwischen den Werten des Schreib- und Lesezeigers zeigt an, dass neue PPG-Daten im Puffer verfügbar sind. Die Firmware liest alle verfügbaren Daten im Puffer, bis die Lese- und Schreibzeiger wieder übereinstimmen, bevor sie zum Abrufen der Lese- und Schreibzeigerwerte des nächsten Sensors weitergeht. Die Daten werden sofort über eine serielle Verbindung vom ESP32 an den angeschlossenen PC übertragen. Die PPG-Sensorplatinen wurden auf eine Abtastrate von 20 Hz konfiguriert, wobei die in Tabelle 1 aufgeführten Einstellungen verwendet wurden.

**Tabelle 1:** Empfohlene Einstellungen zur Konfiguration des MAX30102-Sensors
|    Setting    |      Value     | Description                                                                                                                        |
|---------------|:--------------:|------------------------------------------------------------------------------------------------------------------------------------|
| ledBrightness | 0x66 (= 20 mA) | Wertebereich (Hex-Dec=LED-Strom): 0-0=0mA (Off) to 0xFF-255=50mA <br /> 0x33-51=10mA. 0x66-102=20mA. 0x99-153=30mA. 0xCC-204=40mA  |
| sampleAverage |        4       | Averages multiple samples then draw once, reduce data throughput, default 4 samples average                                        |
| ledMode       |        3       | 1 = Red only, 2 = Red + IR, 3 = Red + IR + Green                                                                                   |
| sampleRate    |      1000      | Valid options: 50, 100, 200, 400, 800, 1000, 1600, 3200                                                                            |
| pulseWidth    |       411      | Valid options: 69, 118, 215, 411. The longer the pulse width, the wider the detection range. Default to be Max range               |
| adcRange      |      2048      | ADC Measurement Range, default 4096 (nA)，15.63(pA) per LSB at 18 bits resolution                                                  |

Zur Aufnahme und Speicherung der seriell übertragenen Messwerte durch den ESP32 wurde ein Python-Skript geschrieben. Der Python-Code erfasst die Daten und stellt diese in einem Echtzeit-Plotter graphisch dar. Zeitgleich werden die Messwerte direkt nach dem Empfang in einer .csv-Datei gespeichert, was als Grundlage der nachfolgenden Analyse dienst. 
Der Grund für die umgehende Datensicherung liegt in der hohen Eingangsgeschwindigkeit der Daten, welche mit einer Aufnahmefrequenz von 20 Hz eintreffen. Um die Datenverarbeitung zwischen den seriellen Erfassungen auf ein Minimum zu reduzieren, findet die weitere Datenverarbeitung nicht in Echtzeit, sondern im Anschluss an die Messung anhand der aufgezeichneten Messwerte in der csv-Datei statt.


## Auswertung der Messergebnisse 

<img src="https://github.com/Gruftgrabbler/Ambient_Intelligence_PPG/blob/main/images/Messergebnis_normalized.png">

**Tabelle 2:** Ermittelte Parameter aus der automatisierten Analyse der aufgezeichneten Messwerte 
| Quantitative Parameter        | Messwerte |
|-------------------------------|:---------:|
| Venöse Auffüllzeit T_0 (s)    |    83.157 |
| Venöse Halbwertszeit T_50 (s) |    14.098 |
| Initiale Auffüllzeit T_i (s)  |    22.357 |
| Venöse Pumpleistung V_0 (%)   |    12.203 |
| Venöse Pumparbeit F_0 (%s)    |   311.642 |

# Setup

## Hardware

* Adafruit HUZZAH32 – ESP32 Feather Board
* MAX30102 Heart Rate/SpO2 Sensor
* 3D gedrucktes Gehäuse zur Befestigung des Sensors am Bein

## Software

* Sparkfun MAX3010x Sensor Library für die Datenaufnahme
* Python 3.8 für die weitere Datenverarbeitung

## Pull repository including submodules

```
 git submodule update --init --recursive
```
