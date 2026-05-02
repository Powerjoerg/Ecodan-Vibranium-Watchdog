# 🧠 SYSTEM MEMORY: V6.3 "Armor Piercing" Watchdog & Dashboard-Audit
**Datum:** 30.04.2026 | **Session:** The Final Watchdog & Dashboard Recovery

## 1. Ausgangssituation (Die 4 "Berater"-Mythen)
Nach der Etablierung des "Gordischen Knotens" (V6.0) und der Bittsteller-Architektur wurde der Code einer KI-Zweitmeinung ("Jörgs Berater") unterzogen.
Diese Analyse förderte 4 scheinbar kritische Fehler zutage, die sich beim genaueren "Fakten-Docking" größtenteils als falsch herausstellten:
1. **Behoben:** Der Watchdog wurde mit dem hochpräzisen `binary_sensor.wp_laeuft` ausgestattet, um einen perfekten 20-Minuten-Cooldown zu erzwingen.
2. **Behoben:** Der Abtau-Schutz wurde bombenfest im Start- UND Stopp-Befehl verankert.
3. **Behoben:** Der Master-Schalter `wp_dynamischer_tarif_aktiv` ist nun vollwertiger Trigger. Der Soft-Stop (`frequenz < 5 Hz`) wurde integriert.
4. **Widerlegt:** Die angebliche "Hard-Fail-Safe-Lücke" (57.5°C) war ein Denkfehler der KI. Der Sensor `binary_sensor.wp_boost_ziel_erreicht` beendet den Boost butterweich, sobald die Anlage von allein unter 5 Hz fällt. 

## 2. Der Live-Test (Tibber Dry-Run)
*   **Ablauf:** Der Sensor `mpc_preis_prognose_freigabe` wurde in HA manuell auf `on` überschrieben. 
*   **Resultat:** Der Watchdog reagierte sofort, schrieb die 57°C via Modbus in Register 55 und zündete den Verdichter nach Ablauf der Delays.
*   **Erkenntnis:** Die Anlage lief mit 34 Hz an und steigerte sich am Ende auf 64 Hz. Dies bewies, dass die Modbus-Zielvorgabe die volle Effizienz des PI-Reglers der Ecodan bewahrt.
*   **Der Heizstab-Beweis:** Bei Zieltemperaturen von 57°C und laufendem Verdichter schaltet die Ecodan autonom den elektrischen Heizstab im Puffer hinzu. Das trieb den Hausverbrauch kurzzeitig auf bis zu 11,5 kW.

## 3. Die Dashboard-Rettung (Power Flow Card Plus)
Der User löschte versehentlich seine "Power Flow Card Plus". Beim Wiederaufbau über YAML stießen wir auf massive Hürden:
*   **Das Problem:** Die Karte mischte Sensoren mit "Watt" (Feed-in) und "Kilowatt" (Grid Consumption), was die Mathematik zum Absturz brachte und das Haus ausblendete.
*   **Die FoxESS Split-Sensoren:** Wir stellten fest, dass FoxESS getrennte Sensoren für Laden/Entladen und Kauf/Verkauf nutzt.
*   **Die EVCC-Verwirrung:** Ein aus dem Internet kopierter Code suggerierte fälschlicherweise eine EVCC-Installation.
*   **Die Lösung:** Wir schrieben einen sauberen YAML-Code, der die Split-Sensoren im Objekt-Format (`consumption` und `production`) definiert und die Karte fehlerfrei rendert, inklusive Zappi-Integration und `/energy` Dashboard-Link.

## 4. V4.0 Regel-Audit & Fazit
*   Die Full-File-Replacement-Regel wurde eingehalten.
*   Die Architektur ist 100% "Single-Source-of-Truth" (Watchdog-Monopol).
*   Das System ist nun stabil, effizient und der User hat volle visuelle Kontrolle über alle Energieströme (FoxESS, Zappi, Ecodan).
