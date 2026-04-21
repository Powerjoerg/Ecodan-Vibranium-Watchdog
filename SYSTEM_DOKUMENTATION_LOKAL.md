# Mitsubishi Ecodan PV-Boost — Home Assistant Integration (LOKALES DOKUMENT)

⚠️ **INTERNE VERSION: ENTHÄLT SENSIBLE NETZWERK- & GERÄTEDATEN - NICHT TEILEN!** ⚠️

Automatische PV-Überschuss-Steuerung für Mitsubishi Ecodan Wärmepumpen mit Home Assistant, Modbus (Procon A1M) und Shelly Pro 3EM. Dies ist die **Version 2.8 "The Rock" (Decoupled)**.

> **Ziel:** Wenn genug Solarstrom vorhanden ist und die Batterie ausreichend geladen ist, wird die Warmwasser-Solltemperatur automatisch von 50°C auf 60°C angehoben. Dadurch wird überschüssiger PV-Strom als Wärme gespeichert. Ein Ladewächter sorgt für den "Zwangsschlaf" durch Modbus-Temperatur-Absenkung (auf 40°C), während ein Hardware-Shelly In1 als Ausfallsicherung dient.

---

## 1. Systemübersicht & Hydraulik

```text
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   PV-Anlage     │────▶│ FoxESS H3-Pro    │────▶│   Batterie      │
│   14,5 kWp      │     │ Wechselrichter   │     │ FoxESS ESC 2900 │
└─────────────────┘     └──────┬───────────┘     │ 17,28 kWh       │
                               │                  └─────────────────┘
                               │ PV-Daten via HA
                               ▼
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│ Mitsubishi       │     │  Home Assistant  │     │ Shelly Pro 3EM  │
│ Ecodan WP        │◀──▶│  Raspberry Pi 5  │◀───│ WP-Verbrauch    │
│ PUD-SHWM140YAA  │     │                  │     │ CT1: Außen (×3) │
│ EHSD-YM9D       │     │  WP-Steuerung v2 │     │ CT2: Heizstab(×3)
│ FTC6 Controller  │     │  "The Rock"      │    │ CT3: Innen (×1) │
└────────┬─────────┘     └───────┬──┬───────┘     └─────────────────┘
   │     │                       │  │                      
  Hydr.  │ Modbus RTU            │  │ WLAN (192.168.178.106)
   │     │ RS-485                │  │                      
   ▼     ▼                       │  ▼                      
┌─────────────────┐     ┌────────┴─────────┐     ┌─────────────────┐
│ Procon A1M      │     │ Waveshare        │     │ Shelly 1 Mini   │
│ MelcoBEMS MINI  │◀───▶│ USB to RS-485    │     │ P-Relais an IN1 │
│ Modbus Adapter  │     │ /dev/ttyUSB0     │     │ (Zwangsschlaf)  │
└─────────────────┘     └──────────────────┘     └─────────────────┘
   │
   ▼ (Hydraulik)
┌─────────────────┐     ┌──────────────────┐
│ Trenn-/Puffer-  │────▶│ TWL Frischwasser-│ (Oventrop Regumaq)
│ speicher        │     │ station (FriWa)  │
└──────┬──────────┘     └──────────────────┘
       │
       ▼
┌─────────────────┐
│ externe Pumpen- │
│ gruppe & FBH    │
└─────────────────┘
```

**Hydraulische Arbeitsweise:** 
Die Ecodan speist in einen Puffer. An diesem Puffer hängt eine TWL/Oventrop Frischwasserstation, welche ihre Wärme für TWW direkt aus dem Puffer bezieht. Eine externe Pumpengruppe mischt die FBH-Kreise. Dadurch kann die WP über den reinen TWW-Modus (Register 30 Manipulation via Modbus) in einen Zwangsschlaf versetzt werden, ohne dass die Hausheizung abbricht, sofern der Puffer Restwärme besitzt und die Raumthermostate bedient.

---

## 2. Hardware & Entitäten (LOKALE IDs)

| Gerät | Typ | HA Entität / IP / MAC |
|-------|-----|----------------------|
| **WP Thermostat-Relais** | Shelly 1 Mini Gen4 | `switch.wp_thermostat_in_1` (IP: 192.168.178.106) |
| **WP Verbrauchsmessung** | Shelly Pro 3EM | `sensor.shellypro3em_e08cfe95cbe0_phase_a_leistung` |
| **Zappi EV Charger** | myenergi Zappi | `sensor.myenergi_zappi_15553841_plug_status` (Kuga) |
| **Räume** | Tuya/Moes ST1820 | `climate.st1820_80b54e38809c`, `st1820_b08184f2dbc8`, `b08184f4860c` udglm. |
| **Räume (Küche/Büro)** | Thermostate | `climate.t_kuche_eg`, `climate.thermostat_buro` |

DIP-Switches (Müssen zwingend so stehen!):
- **FTC6 SW2-1**: ON (Externe Thermostatsteuerung IN1 aktiv)
- **A1M Modbus**: DIP 1, 6, 7 auf ON

---

## 3. Die v2.5 "The Rock" Logik

### 3.1 Zwangsschlaf & Ladewächter-Hysterese
Die Kernlogik eliminiert das Takten der WP. Die Automation `sensor.wp_ladewaechter` erzeugt eine Hysterese:
- Puffer unter 40°C → Modbus Set Temp auf 50°C, Shelly ON (Heizbedarf).
- Puffer über 50°C → Modbus Set Temp auf 40°C, Shelly OFF (Zwangsschlaf!).

### 3.2 PV-Boost
- Wenn Überschuss (`sensor.feed_in`) > 1200 W (streng in Watt reglementiert!) und Batterie > 50% (Tagsüber).
- Ignoriert die 50°C Grenze des Ladewächters und überschreibt Modbus Register 30 auf 5500 (55°C). 
- Fällt PV weg, beendet sich der Boost. Modbus bringt WP in die Ladewächter-Hysterese (bzw. Zwangsschlaf 40°C) zurück.

### 3.3 Modbus-Heartbeat Watchdog (Sicherheitsschicht!)
- **Problem**: Der FTC6 hat einen 30-Minuten Timeout (Item 128). Kommt kein Signal, wird das Register gelöscht.
- **Lösung**: Automation `wp_thermostat_watchdog` sendet alle 10 Minuten den aktuellen Soll-Wert per Modbus (4000, 5000 oder 6000) exakt an `/dev/ttyUSB0` (Slave 1, Register 30) durch. Dadurch geht der Mitsubishi-Controller niemals in den Timeout-Modus.

### 3.4 Tibber & Dynamische Preise ("Schattenbetrieb")
- Solange das Smart Meter fehlt, ist die Tibber-Logik (`sensor.wp_puffer_soll_dynamisch`) **physisch komplett vom Watchdog abgekoppelt**.
- Tibber berechnet im Hintergrund dynamische Werte (z.B. 48°C) und zeigt diese im Dashboard / Notifications an (reine Testanordnung).
- **Wichtig:** Der Watchdog greift niemals auf Tibber zu! Die Maschine wird extrem felsenfest ("The Rock") ausschließlich über Ladewächter (40/50°C) und PV-Boost (55°C) gesteuert.

### 3.5 Fallback-Strategie & Notfallhandbuch
- **Shelly Auto-Off vs Power-on-Default**: Konfiguriert auf "Restore Last" oder "ON".
- Fällt der Raspberry Pi (Home Assistant) komplett aus, greift Stufe 2 aus dem `NOTFALL_HANDBUCH.md` (DIP Switch SW2-1 auf OFF kippen), damit die Ecodan den Shelly ignoriert und autonom weiterläuft.

---

### 3.6 Geplante Zappi-Erweiterung (Smart Meter Tibber-Laden)
Sobald das physische Smart Meter installiert ist, wird die starre `01:00` Uhr Nachtladung der Zappi durch eine "Gleitende Preisbremse" in der YAML ersetzt.
**Konzept:** Die Zappi wird so gekoppelt, dass sie nur dann auf `FAST` schaltet, wenn der `sensor.aktueller_strompreis` pauschal extrem günstig ist (z.B. < 18 ct/kWh) ODER der aktuelle Preis maximal 3 ct über dem absoluten Tagestief (`sensor.electricity_price_min_your_home`) liegt. Verlässt der Preis dieses Tal, fällt die Zappi automatisch wieder auf `ECO +` zurück.

---
*Lokal verifizierter Stand - Alle Entitäten entsprechen der YAML v2.5 config. *
