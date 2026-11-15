# V7.76 — eFuse TPS26600 / F200 / SW200 / TPS54202 native gate (NO FAB)

Baseline integrata al 15 novembre 2026: `main` `16052c33a1809ee097a6cf2b97b03f5c99c8b505`, master **V7.74** (7 sheet), ultima CI KiCad9 **43572358648**, 140 componenti /103 reti, **28 errori ERC +180 warning**. Nessuna modifica a schemi, footprint o PCB proposta in V7.76. Test `test_native_efuse_buck_coordination_v776.py` utilizza la *vera netlist gerarchica KiCad9 già prodotta* dal medesimo job V7.74; valida F200 U200 U100 R203 R204 SW200 e terra/RTN. Il risultato CI di V7.76 va verificato prima di dichiarare passato il test.

## Design input verificati sul CAD attuale

| Nodo / elemento | Design reale nel sorgente | Decisione e limite |
| --- | --- | --- |
| F200 | `1.5A 045101.5MRL CANDIDATO`; le due estremità sono su reti diverse e l'uscita è su U200.IN | **HOLD**: 1,5 A nominali NON sono corrente certa di fusione, né dimostrano curva tempo-corrente/I²t/fault energy né temperatura |
| U200 TPS26600PWPT | IN1/2 insieme; OUT15/16 verso U100 VIN3; RTN8 e PowerPAD17 insieme, separati da GND9 | Protezione contro inversione dipende da **non** ponticellare RTN/GND; servono layout termico, return e condizioni di guasto |
| R203 | `8k2 1%` ILIM→RTN | Datasheet TI TPS2660 SLVSDG2G §10.2.2.2 Eq.(9): `R_ILIM[kΩ]=12/I_LIM[A]` → nominale teorico **I_LIM=12/8.2=1,4634 A**. NON minimo/massimo garantito |
| R204 | `402k 1% MODE_LATCHOFF_CANDIDATE` verso RTN | **LATCH-OFF** richiede recovery indipendente dalla MCU downstream e dal suo 3,3V |
| SW200 | `KMR223NG ULC LFG (CANDIDATE)` pin1+4→U200.SH​DN7, pin2+3→GND_MAIN (U200.GND9) | Recovery manuale schema presente, **ma** accessibilità, debounce, ESD, livelli/fault e specifiche meccaniche ancora HOLD |
| D200 | `SMBJ18CA 18V CANDIDATA / DNP` | TVS NON POPOLATA: non attribuire protezione transitori alla BOM |
| TPS54202 | Fonte 5V da eFuse, rated 2A | Nessuna qualifica del consumo reale, Ceff, loop/load step e startup; rating 2A NON misura della radio |

## Verifica energetica condizionale (non certificazione di funzionamento)

La conversione ideale richiede `I_in = (5V * I_5V) / (Vin * efficienza)`. **Solo esempio teorico** con `I_5V=2A` e efficienze ipotetiche 70% / 80% /90%:
- `Vin 10,5V`: circa **1,361 / 1,190 /1,058 A**;
- `Vin 13,8V`: circa **1,035 /0,906 /0,805 A**;
- `Vin 17,0V`: circa **0,840 /0,735 /0,654 A**.

Questi nove casi sono un *screening di media potenza*; non includono spunto del buck, condensatori in uscita, fault/hiccup, ripple input, derating fuse, inefficienza in transitorio, limitazione in tolleranza del TPS26600, dissipazione e corrente di altre funzioni. Pur essendo 1,463 A e 1,5 A numericamente vicini, **NON si può inferire il corretto coordinamento** fra dispositivo elettronico e fusibile. Anche quando tutti i casi teorici risultassero sotto 1,463 A, NON ne segue alcuna qualifica.

Fonte normativa di componente: [TI TPS2660 SLVSDG2G](https://www.ti.com/lit/ds/symlink/tps2660.pdf) §§9.3.5.5, 9.3.5.7, 10.2.2.2, 10.4. Il manuale dice esplicitamente di non collegare RTN a GND, per non perdere la protezione inversione di polarità. La formula del limite è un'equazione nominale di progetto, non margine worst-case misurato.

## Azione tecnica successiva / acceptance

1. Decidere il **percorso fisico di recupero** eFuse (SW200 attualmente presente ma non qualificato, oppure power-cycle upstream con interruttore qualificato); verificarne circuitazione, livello SHDN, ESD, meccanica, condizioni di inversione e assenza di dipendenza dalla MCU.
2. Qualificare curva corrente/tempo di F200, limite min/max/tolleranza U200, Vin minimo e massimo del **sistema realmente consentito**, load startup, Ceff e termica con documentazione vendor. Il nominale `1.5 - 1.4634 = 0.0366 A` non è margine di protezione approvato.
3. Solo con prove sufficienti, implementare ECO reale in KiCad e confrontare **tutte le reti/pin** e ERC prima/dopo; non spegnere i sei `power_pin_not_driven` con PWR_FLAG o modifiche fasulle.
4. Successivamente spostarsi alla definizione PCB unica e alle impronte MPN-pad vere. **NO FAB / NO GERBER / NO TX**.

**Stato:** test V7.76 in attesa di CI sulla PR; schema V7.74 e 28 ERC errori restano inalterati. Questa verifica è significativa per scegliere il design corretto, ma non sostituisce la prossima ECO elettrica né una prova hardware.
