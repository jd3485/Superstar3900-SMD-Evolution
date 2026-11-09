# Superstar 3900 SMD Evolution — Rapporto tecnico V6.4

**9 novembre 2026 — progetto progressivo PLL/LO RX — NO FAB, NO TX.**

## Sviluppo elettrico e funzionale effettivo

Questa revisione rende esplicita la progettazione candidata del PLL ricevente: LMX2572 con TCXO 12,8 MHz, predivisore R=10, rilevatore di fase fPFD=1,28 MHz, modulatore **integer-N**, VCO 4,64768–4,992 GHz e ÷128 su RFoutA, LO iniettato sopra RF su prima FI candidata **10,695 MHz**. Sono allegati schema funzionale per componenti, pin↔rete sui 41 terminali LMX incluso exposed pad, 5 pin STM32 V6.1, BOM di **16 righe** e ECO d'integrazione con la V6.3. **Non è stato creato uno schematico KiCad nativo verificato, né un PCB.**

## Piano canali e osservazioni

| Risultato | Valore | Metodo |
|---|---:|---|
| Posizioni RX / ALFA | 270 / 30 | import storico `frequency_plan.py`, aritmetica intera |
| Bande | A–F | 6 × (40 + 5) |
| RF min–max | 25.615–28.305 MHz | tabella esatta |
| LO min–max | 36.310–39.000 MHz | fLO = fRF +10,695 MHz |
| VCO min–max | 4.64768–4.99200 GHz | fVCO=fLO×128 |
| N integer min–max | 3631–3900 | fVCO/fPFD, resto zero |
| Frequenze immagine prima conversione | 47.005–49.695 MHz | fimage=fRF+2×FI1 |
| Scarto immagine da RF | 21.390 MHz | differenza matematica |
| Consenso TX su tutte le posizioni | **FALSE** | invariante software; nessun collegamento a finale |

La frequenza dell'immagine da 47,005 a 49,695 MHz è solo un **obiettivo per la reiezione** del front-end e non misura la selettività. Anche la frequenza LO non prova che il PLL agganci realmente. Il valore di fPFD=1,28 MHz cade nel campo datasheet per **integer channel** (0,25–250 MHz), non nel campo **modulatori MASH** di ordine 1–4 (minimo 5 MHz). È quindi essenziale mantenere il progetto candidate in integer mode e confermare PFD_DLY_SEL, i registri, il filtro loop e il calibration assist con TICS Pro ed EVM. Il core VCO precedentemente stimato non va forzato senza dati di calibrazione.

## Simulazioni riproducibili e limiti

Eseguita una **simulazione numerica di 25.000 campioni** sul riferimento TCXO ipotizzato uniformemente da −2,5 a +2,5 ppm, con seme fisso 6402, campionando le 270 frequenze LO. Scarto assoluto del LO nel campione fino a **97.48 Hz**; massimo teorico degli scenari **97.5 Hz** a 39,000 MHz. **Questo non è il dato di targa del TCXO reale né una simulazione del rumore di fase**; la stabilità del filtro IF e la precisione RF complessiva non sono caratterizzate. Nessun modello SPICE vendor o spettro RF realizzato.

La macchina di stati software candidata richiede alimentazioni valide, riferimento presente, CE stabilizzata ≥1 ms, **profilo LMX fornito e approvato esternamente**, e lock-detect stabile per 3 ms prima di sbloccare l'audio RX. Perdita alimentazione/riferimento/lock o ingresso PA silenziano immediatamente RX nel modello. La TX è sempre falsa. Non sono stati calcolati né inventati registri binari LMX. Progetto di priorità logica: non verifica temporizzazioni del chip e non sostituisce un watchdog o interblocco hardware.

## Correzione d'integrazione alimentazione da risolvere

La V6.3 **aveva già previsto** un carico `PLL_LO` di 0,150 A nominali e 0,250 A inviluppo, attribuito al ramo `5V_RF`. La V6.4 propone un **LDO dedicato U402 TPS7A20 3V3_PLL**, alimentato dal 5V_RF e separato da 3V3_A, senza aggiungere corrente già conteggiata. LMX2572 assorbe all'incirca 82 mA tipici in uscita divisa e il budget di esempio aggiunge TCXO/buffer per circa 105–150 mA, **non ancora confermati dai part number**.

Nel modello termico prudenziale ideale per U402 con 5→3,3 V, RθJA ipotizzata **199,6 K/W** e ambiente 85°C si ottiene:

| Corrente ipotizzata | Potenza LDO | Tj ideale a 85°C | Stato |
|---|---:|---:|---|
| 105 mA | 0.1785 W | 120.6°C | Margine ridotto |
| 150 mA | 0.2550 W | 135.9°C | **Supera 125°C: BLOCCANTE** |

La resistenza termica scelta è volutamente conservativa e non associata a un layout approvato: il risultato **non è una misura** e non prova che ogni package TPS7A20 superi il limite. Impone però una revisione della dissipazione, package/rame, temperatura massima, corrente reale e possibile alternativa a minore perdita **prima di fissare la scheda**. Nessun 5V_RF viene trasportato sui pin digitali LMX o MCU.

## Test e regressione

- **60 test nuovi V6.4 PASS**, con controlli su 270 canali, integer-N, range VCO, FI/immagine, parità rispetto alla tabella storica, frequenza CH9, assenza TX, vincoli termici e coerenza pin STM32 V6.1. Test negativo su parametri fuori-range.
- Il test di supervisione comprende un **fuzzing riproducibile di 10.000 transizioni** con ingressi simulati (PA, LOCK, alimentazione, fault, retune), senza mai abilitare TX.
- **7 suite selezionate PASS** (V5.9, V6.0, due V6.1, V6.2, V6.3, V6.4). Non si dichiara una nuova esecuzione dell'intera storia V4.0–V5.8.
- Controlli integrità ZIP, manifest SHA-256 e estrazione indipendente sono nel rapporto di packaging.
- KiCad `kicad-cli`: **NOT_RUN_KICAD_MISSING**; ngspice **NOT_RUN_SPICE_MISSING**. TICS Pro non disponibile ed esecuzione nativa registri **NOT_RUN**.

## Attività aperte e vincoli NO FAB/NO TX

1. Confermare TCXO esatto, pin 10 AFC/GND e livello/accoppiamento OSCin.
2. Creare e validare 126 parole dei registri via TICS Pro su scheda reale; configurazione MUXout e VCO calibration; verificare PFD_DLY_SEL.
3. Simulare/filter loop CPOUT→VTUNE col profilo reale, stabilità, charge pump e Kvco e verificare spur a passi 1,28 MHz e 10 kHz, rumore di fase, lock time.
4. Progettare realmente filtro 36–39 MHz, matching differenziale/single-ended, terminazione RFoutB e percorso mixer con misure spettro e reiezione immagine.
5. Qualificare U402, eventuale LDO alternativo, stress termico e interferenze del buck V6.3 a 26–28 MHz.
6. Collegare nei futuri schemi KiCad MCU V6.1, supervisor V6.2, alimentazioni V6.3, RX originale e pin dei connettori. Eseguire ERC/DRC e simulazioni complete dopo tutte le fasi progettuali e test incrementali a ogni revisione.
7. **Nessuna abilitazione RF, nessun finale montato, nessuna produzione PCBWay** prima di validazione hardware e normativa.

## Allegati e fonti

- `01_Specifiche/V6.4/SCHEMA_FUNZIONALE_PLL_V6.4.md`; `ECO_ALIMENTAZIONE_E_INTEGRAZIONE_V6.4.md`;
- `02_Piano_Frequenze/V6.4/PIANO_PLL_LO_270_RX_V6.4.csv`;
- `03_Verifiche/V6.4/simula_pll_v64.py`, `RISULTATI_SIMULAZIONI_PLL_V6.4.json`, `test_pll_v64.py`, `REGRESSIONI_V6.4.json`;
- `08_Firmware_Prototipi/V6.4/pll_lo_guard_v64.py`; `07_Componenti/BOM_PLL_LO_V6.4.csv`.
- [Texas Instruments — LMX2572](https://www.ti.com/product/LMX2572) (frequency divider, VCO, fPFD e serial control).
- [Texas Instruments — TPS7A20](https://www.ti.com/product/TPS7A20) (LDO 300 mA, dissipazione e caratteristiche).

**Prossimo modulo V6.5: mixer RF e FI1 / piano filtri RX**, coerente con la nuova iniezione LO e reiezione immagine. Nessuna revisione storica viene sovrascritta senza snapshot esatto.
