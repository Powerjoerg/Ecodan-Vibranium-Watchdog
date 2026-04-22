# Vollumfängliche Diagnose: Ecodan PV-Boost & Ladewächter (V2 Komplett)

Nach der Prüfung der System-Architektur (Datei `packages/wp_automationen_v2_KOMPLETT.yaml` gegenüber der lokalen Systemdokumentation und der hydraulischen Gegebenheiten) wurde eine tiefgreifende Simulations-Diagnose der aktuellen Zustandsmaschine durchgeführt.

## 1. Systemarchitektur & Hydraulik-Check (Ist-Zustand)
- **Komponenten:** Ecodan Wärmepumpe -> Pufferspeicher -> (A) FriWa für Trinkwasser, (B) Heizkreise für Räume.
- **Steuerungsschnittstellen:** 
  1. Modbus RTU (Register 30) zur Manipulation der Zieltemperatur (TWW-Fake-Modus).
  2. Shelly IN1 als harter Hardware-Schalter ("Zwangsschlaf").

## 2. Analyse der geänderten Zustände (V2 KOMPLETT Paket)

Das System wurde auf die V2_KOMPLETT Architektur umgestellt. Hier ist die Diagnose aller aktiven Mechaniken:

### ✅ Positiv-Befunde (Was stabil und wasserdicht läuft)
1. **PV-Boost "Panzer-Helfer":** Die Sensoren `wp_pv_boost_freigabe`, `wp_boost_abbruch_pv` und `wp_boost_abbruch_batterie` nutzen nun `delay_on` und `delay_off`. Dadurch wird das ständige An- und Abschalten bei Wolkenflug ("Nervöser Boost") komplett unterbunden.
2. **Watchdog & Prioritäten (Single Source of Truth):** Der Modbus wird nicht mehr wild von verschiedenen Automationen beschrieben. Stattdessen weckt ein "Dirty Flag" (`wp_control_dirty_flag`) den Watchdog, welcher streng nach Priorität entscheidet: Urlaub (15/45°C) -> PV-Boost (55°C) -> Ladewächter (50°C) -> Zwangsschlaf (40°C). 
3. **Zappi EV Charger:** Die Kopplung der FoxESS Batterie an die Zappi funktioniert. Sobald auf FAST geladen wird, springt die Batterie auf "Back-up" und wird nicht versehentlich ins Auto entleert.

### 🚨 KRITISCHER BEFUND (Race-Condition & Kaltes Wasser)
Bei der Prüfung der `automations.yaml` (alt) im Vergleich zur neuen `wp_automationen_v2_KOMPLETT.yaml` wurde ein massiver Fehler im Umgang mit dem **Shelly IN1 (Zwangsschlaf-Relais)** entdeckt.

- **Altes System:** Der Shelly IN1 wurde vom Ladewächter getriggert (Puffer < 40°C = Shelly ON).
- **Neues System (V2 KOMPLETT):** Der Shelly IN1 wird *ausschließlich* vom `binary_sensor.haus_heizbedarf` (den Raumthermostaten) gesteuert (Automationen `wp_umwaelzpumpe_freigabe_an` / `_aus`).

**Die Simulation eines Edge-Cases zeigt den fatalen Domino-Effekt:**
1. Es ist Frühling, die Sonne scheint leicht, die Räume sind warm (Thermostate sind zu).
2. Der `binary_sensor.haus_heizbedarf` schaltet auf `off`.
3. Die Automation schaltet den Shelly IN1 auf **OFF (Zwangsschlaf)**.
4. Jemand duscht ausgiebig. Der Pufferspeicher kühlt auf 35°C ab.
5. Die FriWa hat keine Wärmeenergie mehr, das Wasser wird beim Duschen **kalt**.
6. Der Ladewächter erkennt < 40°C und der Watchdog sendet `50°C` an den Modbus.
7. **Fehler:** Die Wärmepumpe ignoriert den Modbus-Befehl, weil der Shelly IN1 weiterhin auf `OFF` steht (Räume sind ja noch warm)! Die Ecodan springt nicht an. 

## 3. Fazit
Das System ist in seiner jetzigen Form **nicht ausfallsicher** in Bezug auf den Warmwasser-Komfort. Die Kopplung des Zwangsschlafs (Shelly IN1) rein an den Heizbedarf der Räume entzieht der FriWa die Überlebensgrundlage.

## 4. Lösungsarchitektur
Der Shelly IN1 darf erst in den Zwangsschlaf (`OFF`) gehen, wenn **BEIDE** Bedingungen erfüllt sind:
1. Das Haus hat keinen Heizbedarf mehr.
2. Der Puffer ist voll geladen (Ladewächter meldet False).

Umgekehrt muss der Shelly IN1 **SOFORT** einschalten (`ON`), wenn:
1. Das Haus heizen will.
**ODER**
2. Der Puffer nachgeladen werden muss (Ladewächter meldet True), damit man duschen kann.
