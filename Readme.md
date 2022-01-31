# Mini-Praktikum: Venen Funktionsmessung mittels PPG
Bei der venösen Photoplethysmographie wird die Lichtreflexion (Synonym: Licht-Reflexions-Rheographie, LRR)
mittels eines PPG-Sensors gemessen. Da Licht von Blut stärker als vom Gewebe absorbiert wird, nimmt
die Lichtreflexion bei steigendem Blutvolumen im Bein ab. Das LRR-Signal spiegelt daher Blutvolumenschwankungen wider.
Das LRR-Signal gliedert sich in einen gleich bleibenden Anteil durch Lichtabsorption in „undurchblutetem“ Gewebe 
(ca. 90 %), eine variable Lichtabsorption durch das venöse Blutvolumen (ca. 10 %) und eine periodische arterielle 
Lichtabsorption (ca. 0,5 %). Mithilfe digitaler Filtertechniken können diese Signale voneinander getrennt werden 
(digitale Photoplethysmographie, dPPG) [[1]](https://docplayer.org/21805396-Phlebologische-funktionsdiagnostik.html).

## Durchführung der Messung

Der sitzende Patient führt acht Dorsalextensionen in 16 Sekunden im Sprunggelenk durch. Die Ferse ist dabei am Boden
abgestützt. Der PPG-Sensor wird mithilfe des 3D gedruckten Gehäuses ca. 10 cm oberhalb des Malleolus medialis angebracht (Abb. 1). 

<img src="https://github.com/Gruftgrabbler/Ambient_Intelligence_PPG/blob/main/images/Durchf%C3%BChrung%20der%20dPPG-Messung.png" width="421" height="329">

Die Fußbewegung führt zur Kompression der Beinvenen und damit zu einem Bluttransport nach proximal (Muskelpumpe). Das abnehmende Blutvolumen
spiegelt sich in der LRR-Kurve durch eine zunehmende Lichtreflexion wider. Nach Beendigung der Fußbewegung fließt das 
Blut wieder nach distal. Bei insuffizienten Venen geschieht das schneller, als bei suffizienten Venenklappen 
[[1]](https://docplayer.org/21805396-Phlebologische-funktionsdiagnostik.html).

![Mustermessung](https://media.springernature.com/original/springer-static/image/chp%3A10.1007%2F978-3-642-23804-8_36/MediaObjects/67823_2_De_36_Fig4_HTML.gif)[[2]](https://link.springer.com/chapter/10.1007/978-3-642-23804-8_36)

Der Messzyklus läuft vollautomatisch ab, die Messsignale werden ebenfalls automatisch ausgewertet.
Erfasst werden folgende Parameter zur unterstützenden Diagnostik der Venenfunktion:
* Venöse Wiederauffüllzeit <img src="https://render.githubusercontent.com/render/math?math=T_0">
* Venöse Halbwertszeit <img src="https://render.githubusercontent.com/render/math?math=T_{1/2}">
* Initiale Auffüllzeit <img src="https://render.githubusercontent.com/render/math?math=T_i">
* venöse Pumpleistung <img src="https://render.githubusercontent.com/render/math?math=V_0">
* venöse Pumparbeit <img src="https://render.githubusercontent.com/render/math?math=F_0">


## Vorverarbeitung der Daten

Zur Aufnahme und Speicherung der seriell übertragenen Messwerte durch den ESP32 wurde ein Python-Skript geschrieben. Der Python-Code erfasst die Daten und stellt diese in einem Echtzeit-Plotter graphisch dar. Zeitgleich werden die Messwerte direkt nach dem Empfang in einer .csv-Datei gespeichert zur späteren Analyse. Der Grund, warum wir sie sofort speichern, ist, dass die Daten mit so hoher Geschwindigkeit eintreffen, dass wir die Datenverarbeitung zwischen den seriellen Erfassungen auf ein Minimum reduzieren wollen.

## Auswertung der Messergebnisse 

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
