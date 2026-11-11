# Superstar 3900 SMD — V7.18 engineering change order: TPS26600 OUT15/OUT16

**11 novembre 2026 · ECO verificato con KiCad 9 nativo, valido solo come modello elettrico CAD. NO FAB / NO TX.**

## Origine e motivazione

[Datasheet ufficiale TI TPS2660x, SLVSDG2G rev. G, p. 5](https://www.ti.com/lit/ds/symlink/tps2660.pdf), "Pin Functions": **OUT pin 15 e OUT pin 16 del TPS26600PWPT HTSSOP-16 sono entrambi terminali Power output di un unico eFuse**. La tabella comprende anche le corrispondenti piazzole 23 e 24 del package VQFN, che NON vanno confuse con quelle HTSSOP. La PCB deve ancora tenere entrambi i pin OUT sul medesimo nodo fisico previsto dal produttore; separarli sarebbe una falsa soluzione.

Nel simbolo embedded storico `S3900E:TPS26600_PWP` KiCad attribuisce **`power_out` sia al pin 15 sia al pin 16**, producendo un `pin_to_pin` tra due uscite che in realtà appartengono al **medesimo dispositivo di alimentazione**. La collisione è di classificazione CAD, **non un corto tra regolatori differenti**.

## Correzione strettamente limitata

La nuova copia versionata del foglio `04_KiCad/Gerarchico_Alimentazioni_V7.18_PINMODEL_NOT_FOR_FAB/01_EFUSE_AUX.kicad_sch` modifica esattamente un attributo del simbolo incorporato:
- U200, OUT15: **`power_out` mantenuto**;
- U200, OUT16: **`power_out` → `passive`** *solo nella disciplina ERC*, mentre funzione fisica, nome OUT, numero del pin, posizione, footprint, net, connessione tra pin 15/16 e protezione reverse-input restano invariati;
- Il foglio alimentazioni, il buck, il PLL/TCXO e le librerie storiche restano byte-identici; anche la PCB RX originaria e il progetto V7.17 non sono alterati.

Una nuova copia del **master KiCad completo a 7 fogli** in `04_KiCad/Assemblaggio_RX_Power_V7.18_POWER_PINMODEL_NOT_FOR_FAB/` punta soltanto al nuovo AUX. Non introduce fili o pin gerarchici. Il nome base del file .kicad_sch/.kicad_pro resta quello usato per gli UUID/annotazioni dei fogli, nella cartella esplicitamente versionata V7.18.

## Gate nativo misurato

La pipeline `.github/workflows/v718_efuse_pll_native.yml` esegue **un vero KiCad 9**: esporta entrambe le netlist gerarchiche, esegue ERC sull'intera gerarchia di 7 fogli, confronta **tutte** le coppie rete–ref–pin, e verifica che il delta ERC sia **esattamente un `pin_to_pin` rimosso** senza decrementi di warning o soppressioni generiche.

Esito della [CI 42963880128](https://github.com/jd3485/Superstar3900-SMD-Evolution/actions/runs/42963880128) **success**:

| Controllo | Baseline V7.17 | Candidato V7.18 |
|---|---:|---:|
| Errori ERC root | **43** | **42** |
| Warning ERC root | 340 | 340 |
| Errori `pin_to_pin` | 1 | **0** |
| Nomi di rete | 99 | **99 identici** |
| Ogni membership ref/pin | baseline | **identica**, zero differenze |
| Reti e interfacce intermodulo approvate | 0 | 0 |
| Interfacce OPEN/HOLD | 15 | 15 |

I 42 errori rimasti sono **26 label aperte +16 problemi elettrici/fili**. Nessuna modifica è stata apportata a sorgenti di alimentazione reali, ad assorbimenti o topologie 5V/3V3/GND.

## In sospeso e vincoli di sicurezza

Il secondo studio V7.18 usa KiCad nativo su **cloni temporanei** per diagnosticare R2/R3 e l'anello PLL. La presenza di un output DRC/ ERC più favorevole su un clone non autorizza alcuna topologia: pin-to-net e risposta del filtro devono seguire la [documentazione TI LMX2572 (SNAS740B)](https://www.ti.com/lit/ds/symlink/lmx2572.pdf). In particolare pin 5 SYNC, 28 SysRefReq, 30 RampClk, 32 RampDir e 35 VTUNE non vanno fissati arbitrariamente.

Restano: ingressi di alimentazione non pilotati, separazione eFuse RTN↔GND_MAIN, rail 5V/3V3, ritorno GND_RF e filtro PLL reale, 26 label non terminate, 15 interfacce OPEN/HOLD, SG48 e TX HOLD, qualifica SMA/destra 180°, ERC/DRC completo e PCB globale non esistente.

**Nessun componente o hardware collaudato. NO FAB / NO GERBER / NO PCBWAY / NO TX.**
