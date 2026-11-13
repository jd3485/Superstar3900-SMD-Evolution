# V7.39 — Verifica del limite assoluto VOUT–VIN TPS7A20 durante il power-down

Data: 13 novembre 2026. Repository: `jd3485/Superstar3900-SMD-Evolution`. Baseline `main` V7.38 (PR #41 integrata, squash `91e4f9d7867bb1fdcd18d19a752460e73d38cd5d`). CAD attivo derivante da V7.36 a sette fogli, 134 componenti / 101 reti, 33 footprint mancanti, ERC 36 errori + 221 avvisi. **Nessuna ECO CAD in V7.39.**

## 1. Nuovo vincolo fondamentale tratto dalla fonte TI

**TPS7A20**, datasheet SBVS338H (July 2024), §5.1 *Absolute Maximum Ratings*, pagina stampata 5, https://www.ti.com/lit/ds/symlink/tps7a20.pdf : tensione **VOUT max = min(6.5 V, VIN + 0.3 V)** rispetto alla GND locale. Questo è un valore assoluto di stress, NON un margine operativo normale. In §6.3.7, pagina 26, il vendor avverte che il collasso di VIN con C_OUT carico può determinare corrente inversa dannosa; limitarla al **5% della nominale 300mA**, quindi **15mA per un periodo breve**. Non interpretare i 15mA come una corrente continuativa ammessa e non equiparare la violazione di tensione al valore della corrente: sono vincoli indipendenti da analizzare insieme.

Altrimenti, se VIN cade mentre VOUT resta sopra VIN+0.3V, si **entra nella zona di stress assoluto del componente**. Questo scenario è **possibile in linea di principio**, non dimostra che avvenga nel nostro circuito e non autorizza diodi/clamp arbitrari.

## 2. Origine e capacità nominale verificata dei tre nodi

Dalla sorgente nativa `04_KiCad/Modulo_MCU_CODEC_V7.36_C6231_MURATA_GRM15_REVIEW_NOT_FOR_FAB/S3900E_MCU_CODEC_AFE_V7_12_REANNOTATED_NOT_FOR_FAB.kicad_sch`, i pin 1 IN di U6205/U6206 sono su `5V_DIGITAL_FILTERED`; U6205 pin5 OUT su `3V3_CODEC_IO`; U6206 pin5 OUT su `3V3_CODEC_LDOIN`; il pin3 EN di U6206 è sul supervisore `CODEC_LDOIN_EN_SUPERVISED` (U6207). La verifica fonte-label è ripetibile mediante `test_tps7a20_powerdown_absmax_v739.py`.

| Nodo | Capacità nominali collegate a GND nel modulo | Somma |
| --- | --- | ---: |
| `5V_DIGITAL_FILTERED` | C6215=1µF, C6219=10µF, C6220=100nF, C6221=1µF, C6223=1µF, C6225=1µF | **14.1µF** |
| `3V3_CODEC_IO` | C6201=100nF, C6224=1µF, C6231=100nF | **1.2µF** |
| `3V3_CODEC_LDOIN` | C6207=100nF, C6208=10µF, C6226=1µF | **11.1µF** |

**NON sono le capacità totali dell'intero progetto**, ma soltanto quelle nominali note sulla schematic MCU/CODEC. Nessun MLCC è ancora qualificato con Ceff worst-case di DC bias, T, aging o tolleranze. Il ramo da 5V alimenta molti altri circuiti, quindi il dato 14.1µF non determina, da solo, quanto rapidamente collassi.

## 3. Screening di rampe indipendenti — non è SPICE fisico

Un test illustrativo definisce `VIN(t)=5exp(-t/τ_IN)` e `VOUT(t)=3.3exp(-t/τ_OUT)`, senza retroazione, diodi intrinseci, LDO, carichi o interazioni fra condensatori; valuta `VOUT(t)-VIN(t) > 0.3V` a ogni istante campionato. **Le costanti τ sono parametri inventati a scopo di stress-test, non misure o specifiche dei componenti.** Esempi:
- `τ_IN=0.2ms, τ_OUT=5ms`: compare una finestra matematica di superamento di 0.3V; a 1ms `VIN≈0.034V`, `VOUT≈2.70V`, differenza **≈2.67V**. Una coppia di tensioni del genere, *se realizzata fisicamente*, sarebbe fuori dal limite assoluto TI.
- `τ_IN=5ms, τ_OUT=5ms`: differenza sempre negativa poiché la tensione iniziale è 5V contro 3.3V; nessun superamento nel modello.
- `τ_IN=5ms, τ_OUT=0.2ms`: nessun superamento nel modello.

**Non usare questi esempi per dichiarare hardware sicuro, hardware difettoso o corrente inversa effettiva.** L'uscita e l'ingresso sono accoppiati attraverso il pass device del TPS7A20 e il resto del circuito; un'effettiva rampe indipendenti potrebbe essere impossibile o alterata dalla conduzione inversa. Questo test è un *generatore di casi critici*, non il modello del regolatore.

## 4. Prossima decisione e misure necessarie

1. Ricostruire full-board l'alimentazione **eFuse/13.8V → 5V_DIGITAL_FILTERED → U6205/U6206** e la suddivisione dei carichi, usando netlist KiCad9 completa e documentazione di buck/eFuse (in particolare ritorni e fault). Il 5V è condiviso: una protezione OUT→IN cambierebbe il comportamento anche degli altri rami.
2. Valutare **prova reale o modello produttore validato** con tracce sincronizzate `VIN(t)`, `VOUT_IO(t)`, `VOUT_LDOIN(t)`, `EN_U6206(t)`, `I_REVERSE_U6205(t)`, `I_REVERSE_U6206(t)`, ripetendo soft/hard shutdown, brownout rapido e slow, riaccensione e fault carico a più temperature.
3. Verificare separatamente `VOUT≤VIN+0.3V`, `I_REV≤15mA breve`, UVLO/active discharge, latenza supervisore e reset/ALDO codec. Determinare durata di stress e limiti dei clamp, inclusi potenziali *backfeed* e reverse-current.
4. **Solo dopo**, decidere se è necessario un circuito di protezione, cambiare LDO o rivedere i valori di C_OUT. Una ECO priva di percorso corrente e carico verificati rischia di peggiorare il brownout.

## 5. Gate e limiti attuali

`03_Verifiche/V7.39/test_tps7a20_powerdown_absmax_v739.py` controlla tramite sorgente KiCad i **12 condensatori** e le sei connessioni IN/EN/OUT di U6205 e U6206, il limite **VOUT–VIN ≤0.3V**, venti test standard Python, e rifiuta esplicitamente ogni signoff se mancano trace di tensioni/correnti validate. Nessuna modifica CAD: niente nuova ERC/netlist KiCad9 richiesta per la presente revisione informativa. **Non dichiarare PASS senza workflow effettivamente eseguito.**

Rimangono **NO FAB / NO GERBER / NO PCBWAY / NO TX**; 15 interfacce crossmodule OPEN/HOLD, SG48 HOLD, Y1 TCXO pin10 HOLD, power/eFuse/PLL/thermal da qualificare. PCB unica ancora incompleta, avanzamento storico ~10% stimato.
