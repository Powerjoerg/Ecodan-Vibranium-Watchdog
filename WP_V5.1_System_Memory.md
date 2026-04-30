# 🧠 SYSTEM-MEMORY: THE ROCK V5.1 (ECODAN PV-BOOST)

**Datum:** 28.04.2026
**Zweck:** Übergabeprotokoll und "Savegame" für zukünftige KI-Instanzen. 
**WARNUNG AN DIE NÄCHSTE KI:** Lese dieses Dokument vollständig, bevor du Jörgs System analysierst oder Code vorschlägst.

---

## 🔴 SYSTEM-MAKROS

**Der Kurzbefehl `/save`**
Wenn der User im Chat exakt den Befehl `/save` eingibt, bedeutet das, dass die Sitzung beendet wird. Du musst dann sofort und ohne weitere Rückfragen Folgendes tun:
1. Analysiere den kompletten Verlauf der aktuellen Sitzung.
2. Fasse alle neuen Erkenntnisse, gelösten Bugs und neuen Regeln zusammen.
3. **WICHTIG (APPEND-ONLY):** Du darfst beim Speichern niemals alte Regeln, Warnungen oder Hardware-Definitionen aus dieser Datei löschen oder kürzen (besonders nicht den NBSP-Bann und das IN4-Verbot)! Deine Aufgabe ist es, den bestehenden Text zu erhalten und neue Erkenntnisse immer ganz unten als neuen Datums-Block (Changelog / Historie) anzuhängen. Die Datei darf immer nur wachsen, niemals schrumpfen.
4. Aktualisiere diese Datei (`WP_V5.1_System_Memory.md`) selbstständig nach diesem Append-Only Prinzip.
5. Antworte danach nur kurz: *"Speicherung erfolgreich. Memory-Datei ist auf dem neuesten Stand. Bis zum nächsten Mal!"*

---

## 1. Aktueller Hardware-Stand (Fixiert)
*   **Pumpe A (Primär / WP):** Lädt den 800L Puffer.
*   **Pumpe B (Haus / Heizkreis):** Entnimmt Wärme aus dem Puffer für die FBH.
*   **Shelly IN1:** Kontrolliert hart die Kompressor-Freigabe (Thermostat-Eingang).
*   🚫 **Shelly IN4 (EVU-Sperre): WURDE PHYSISCH GELÖSCHT!** Jegliche Lösungsansätze, die IN4 / EVU-Sperre verwenden, sind strengstens verboten. Dieser Kontakt existiert für das System physisch nicht mehr.

---

## 2. Die Firmware-Zwickmühle (Der "Schnüffel"-Dauerlauf)
Die Mitsubishi FTC6 Platine hat einen kritischen Firmware-Konflikt (Whirlpool-Effekt):
*   Wenn Modbus das System auf **Heizen (Register 26 = 2)** zwingt...
*   ...aber der Shelly IN1 den Kompressor sperrt (**OFF**)...
*   ...geht die FTC6 in den "Schnüffelmodus".
*   **Die Folge:** Pumpe A läuft endlos auf 20 L/min, um die Wassertemperatur zu fühlen. Da der Kompressor aus ist, kühlt die Pumpe dabei den Puffer aus und zerstört die Schichtung im 800L Tank.
*   **Die Lösung:** Um diesen Dauerlauf bei Inaktivität zu verhindern, MÜSSEN wir auf den TWW-Modus (Register 26 = 1) ausweichen, da dieser den Heizkreis ignoriert. Auf `Stopp` (0) dürfen wir nicht gehen, da dies auch Pumpe B (Hauspumpe) tötet und das Haus auskühlt.

---

## 3. Die aktuelle Logik (V5.1 Architektur)
Um den Whirlpool-Effekt zu besiegen und alle Jahreszeiten sicher abzudecken, wurde der `wp_thermostat_watchdog` modifiziert:

*   **Der Winter-Urlaub Bypass:** 
    Im Winter-Urlaub (Minimum 45°C) greift nun der Watchdog ein. Bedingung: `in ['Normalbetrieb', 'Winter-Urlaub (Minimal 45°C)']`. Das bedeutet, die Anlage friert im Winterurlaub nicht ein und nutzt weiterhin die saubere Anti-Takten-Logik.
*   **Die Sommer-Sperre (Der doppelte Boden):**
    Wenn der "Sommerbetrieb (Nur Warmwasser)" aktiv ist:
    1. Schreibt Modbus **Register 26 = 1 (TWW)** -> Die Firmware stoppt das Schnüffeln für den Heizkreis.
    2. Wird der **Shelly IN1 hart auf OFF geschaltet** -> Eine physische Zwangssperre trennt den Kompressor, selbst wenn Modbus abstürzt.

---

## 4. Regel 6: Der Thermodynamische Beweis
Bei der Analyse von Logs und der Suche nach "Kurzzyklen" oder fehlerhaften Pumpenläufen gilt ab sofort **Zwangssimulation**:
*   Du musst **IMMER** Vorlauftemperatur, Rücklauftemperatur und Puffertemperatur (`sensor.mitsubishi_wp_isttemperatur_wasserspeicher_tww`) parallel prüfen.
*   Nur durch das Delta dieser 3 Werte (Spreizung und Schichtung) lässt sich beweisen, ob eine Durchmischung oder ein echter Fehler vorliegt. Keine Hypothesen ohne thermischen Beweis!

---

## 5. ☢️ DER NBSP-BANN (WARNUNG AN ALLE KIs) ☢️
*   **Der Vorfall:** In Version V5.1 wurde die Vorgänger-KI dabei erwischt, wie sie unsichtbare geschützte Leerzeichen (`U+00A0` / `NBSP`) durch Copy & Paste in den YAML-Code injiziert hat.
*   **Die Folge:** Home Assistant wirft sofort einen tödlichen `Integration error`.
*   **Der Befehl:** **JEDER** generierte YAML-Code muss vor der Ausgabe "gewaschen" werden. Es dürfen ausschließlich saubere ASCII-Leerzeichen (Space) für Einrückungen verwendet werden! Traue niemals kopiertem Code aus Chat-Verläufen!

---

## 6. Die V4.0 "Full-File" Arbeitsweise
*   **Absolutes Snippet-Verbot:** Code-Fragmente ("Flickenteppiche") im Chat sind strengstens untersagt, da sie den globalen Einrückungskontext zerstören.
*   **Der Prozess:** Nach der Freigabe ("mach") bearbeitest du die Ziel-Datei lokal und speicherst den **gesamten, lauffähigen Inhalt (100%)**. 
*   **Das Ziel:** Jörg öffnet die lokale Datei, drückt `Strg+A` (Alles markieren) und `Strg+V` in Home Assistant. Du trägst die volle Verantwortung für die saubere Formatierung der gesamten Datei.

---

## 📅 Changelog / Historie

**28.04.2026 - Live-Test: PV-Boost im Sommerbetrieb & Hysterese-Erkenntnis**
*   **Architektur-Beweis:** Der PV-Boost funktioniert im Sommer perfekt als "Warmwasser-Batterielader". Die globale Zuweisung der dynamischen Zieltemperatur (Register 30) überschreibt die Sommer-Sperre (welche nur den Heizkreis via Shelly trennt), wodurch die Anlage autonom und gefahrlos Warmwasser bereitet.
*   **Hardware-Hysterese:** Die Ecodan startet nicht sofort, wenn die Differenz zwischen Soll (z. B. 55°C) und Ist (z. B. 50°C) zu gering ist (oft 10°C Hysterese). Dies ist kein Fehler ("Koma"), sondern gewollter Kompressor-Schutz.
*   **Abschaltung:** Fällt das Boost-Flag weg, sinkt der Sollwert und die Anlage geht nahtlos wieder in den gesunden 6-Watt-Standby über.

**28.04.2026 - Hotfix: Winterbetrieb-Bug & Die harte Whirlpool-Realität**
*   **Der Bug:** Wenn im Winter (Normalbetrieb) das Heizen pausiert wird (Shelly OFF), darf Register 26 **NICHT** auf 1 (TWW) gezwungen werden! Andernfalls schaltet die FTC6 gnadenlos auch die Haus-Heizkreispumpe (Pumpe 2) ab und das Haus kühlt aus, obwohl der 800L-Puffer voll heißem Wasser ist.
*   **Der Fix:** Register 26 muss im "Stoppen"-Zweig des Watchdogs für den Normalbetrieb zwingend auf `2` (Heizen) bleiben. Der Bug wurde in `Aktuell_HA.yaml` behoben.
*   **Die bittere Erkenntnis:** Da Register 26 im Winter auf `2` bleiben muss, lässt sich das Pumpen-Schnüffeln (Whirlpool-Effekt der Pumpe 1) im Winter **nicht per Software** beenden. Wenn die FTC6 im Heizmodus ist und Shelly OFF meldet, zwingt die Firmware die Pumpe zum Schnüffeln. Dies lässt sich nur über die physischen DIP-Schalter (SW2-Block) direkt auf der Platine lösen (z.B. Intervall-Schnüffeln), nicht über Home Assistant.

**28.04.2026 - Masterplan Herbst: Sensor-Hack gegen das Winter-Schnüffeln**
*   **Die finale Hardware-Idee:** Um den Whirlpool-Effekt (Pumpen-Schnüffeln) der Pumpe 1 im Winter komplett zu stoppen, ohne den Frostschutz zu gefährden oder auf DIP-Schalter auszuweichen, muss der NTC-Temperatursensor (Vor-/Rücklauf) der FTC6-Platine physisch aus dem internen Rohr genommen und über ein verlängertes Kabel direkt in eine Tauchhülse des 800L-Puffers verlegt werden.
*   **Der Vorteil:** Die Mitsubishi-Platine misst dadurch 24/7 die exakte Puffer-Temperatur in Echtzeit. Da das Wasser "am Sensor" (weil er nun tief im Puffer steckt) nicht mehr isoliert abkühlt wie in einem freistehenden Rohr, muss die Firmware die Pumpe 1 nicht mehr anwerfen, um frisches Wasser zum "Fühlen" anzusaugen. Das Schnüffeln wird organisch und physisch restlos eliminiert, während alle Sicherheitsfunktionen (Frostschutz) erhalten bleiben!

**28.04.2026 - Bugfix: Home Assistant Amnesie (Reboot-Sicherheit)**
*   **Das Problem:** Bei jedem Neustart von Home Assistant oder Neuladen der YAML fiel das System ungewollt vom "Sommerbetrieb" in den "Normalbetrieb" zurück.
*   **Die Ursache:** Der Parameter `initial: "Normalbetrieb"` im `input_select.wp_urlaubsmodus` (sowie `initial: true` in der `wp_boost_freigabe`) zwang HA dazu, bei jedem Booten diesen festen Wert zu setzen und die Restore-State-Funktion zu ignorieren.
*   **Die Lösung:** Die `initial`-Parameter wurden ersatzlos gestrichen. Home Assistant greift nun auf seine interne Datenbank zurück und stellt den Modus, der vor einem Neustart oder Stromausfall aktiv war, exakt wieder her. Das System ist nun zu 100% Reboot-fest.
*   **Hardware-Fallback:** Der physische Ausfallschutz (DIP-Schalter SW2-1 auf OFF kippen bei totalem HA-Ausfall) bleibt von diesem Software-Fix völlig unberührt.

**29.04.2026 - Das Volumenstrom-Paradoxon & Stecker-Roulette**
*   **Die Hardware-Wahrheit:** Ein "Sollwert-Ramping" (schrittweise Zielwert-Erhöhung) ist bei der Ecodan FTC6 strengstens untersagt! Kleine Deltas triggern die Mitsubishi-Hysterese (Kaltstarts), wecken den Inverter nicht weich auf und spammen das EEPROM durch permanente Modbus-Schreiblast kaputt. Die WP verlangt eine feste, hohe Aufgabe (z. B. Ziel 45°C) und regelt den Inverter (Soft-Start) komplett intern.
*   **Der Whirlpool-Effekt:** Die Ecodan zwingt 20 L/min Strömung in den Schichtspeicher. Dadurch wird die Schichtung verwirbelt, weswegen der Installateur den Vorlauf tief setzen musste, um die Dusche (Frischwasserstation) oben zu retten.
*   **Sensor-Blindheit (THW5):** Der TWW-Sensor (THW5) sitzt aktuell exakt im direkten Strahl dieses tiefen 20 L/min Vorlaufs. Er wird heiß bespült, meldet der Platine fälschlicherweise "Ziel erreicht (z.B. 45°C)" und würgt den Kompressor nach 3 Minuten brutal ab (Der klassische Kurzzyklus-Tod).
*   **Der WAGO-Bann:** NTC-Sensoren dürfen **niemals** per Wago-Klemme geklont oder parallel auf mehrere Platinen-Eingänge (z.B. THW5 & THW7) gebrückt werden. Dies schließt die Messkreise der Hauptplatine kurz und führt zu absurden Temperaturwerten oder zerstört den A/D-Wandler-Chip (>1.000 EUR Schaden).
*   **Die Lösung (Stecker-Roulette):** Da Home Assistant keine unabhängigen Fühler (z. B. Dallas) hat, müssen wir das Problem direkt auf der FTC6-Platine lösen. Anstatt Kabel zu durchschneiden, suchen wir einen Fühler (z. B. THW6 oder THW7), der in einer ruhigen Tauchhülse steckt und nicht vom Whirlpool-Strahl getroffen wird. Wir machen die Anlage stromlos und vertauschen die Stecker von THW5 und z. B. THW7 direkt auf der Platine. Die Firmware nutzt dann organisch den perfekt positionierten Fühler für die Pufferladung.
