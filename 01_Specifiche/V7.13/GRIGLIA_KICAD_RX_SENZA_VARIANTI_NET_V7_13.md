# V7.13 — allineamento KiCad RX 50 mil con parità elettrica dimostrata

**10 novembre 2026 — CAD nativo / NON fabbricabile / NO FAB / NO TX.**

## Modifica concreta
Il precedente schema RX standalone V7.12 aveva **46 warning `endpoint_off_grid`** rilevati da KiCad 9. È stata creata una nuova copia versionata:

`04_KiCad/Modulo_RX_Test_50ohm_V7.13_GRID_REPAIR_NOT_FOR_FAB/S3900E_RX_STANDALONE_V7_13_GRID_NOT_FOR_FAB.kicad_sch`

**154 coordinate di posizionamento** (simboli, proprietà, estremi dei 31 fili, ancoraggi delle 31 etichette e grafica) allineate alla griglia `50 mil=1,27 mm` con spostamento massimo di **0,635 mm per asse**. Le primitive `lib_symbols`, i pin, gli UUID, la nomenclatura componenti, i valori e gli identificativi delle reti originali non sono stati cambiati. Rispettata la posizione reciproca del terminale rispetto al simbolo; nessuna pista o nuova connessione progettata.

La nuova gerarchia `04_KiCad/Assemblaggio_RX_Power_V7.13_GRID_REPAIR_NOT_FOR_FAB/S3900E_RX_POWER_INTEGRATION_V7_13_GRID_NOT_FOR_FAB.kicad_sch` punta agli **stessi** AUX V1.5, MCU V7.12 e al RX V7.13, con tre percorsi `Sheetfile` verificati nell'albero repository. Un primo tentativo usava per errore un percorso MCU V7.13 **inesistente** (netlist incompleta a 58 reti): corretto e dotato di gate che controlla l'esistenza di tutti i fogli, più confronto elettrico completo prima del merge. Il problema non riguardava il circuito reale, ma era un difetto CAD che ha fatto FALLIRE la CI iniziale; è stato corretto e riprovato.

La copia `.kicad_pcb` RX V7.13 è **identica** in rame, vie e footprint alla V7.12; solo il nome del progetto viene aggiornato. La nuova `sym-lib-table` collega la libreria sperimentale `S3900E.kicad_sym` preesistente, mentre `fp-lib-table` mantiene le tre librerie di footprint storiche; **i 15 avvisi di libreria simboli e i 15 di link footprint permangono**. Le tabelle non validano i footprint SMA/LNA.

## Gate elettrico indipendente su sorgente KiCad
La CI esporta **due vere netlist KiCad9**: gerarchia V7.12 e V7.13. `03_Verifiche/V7.13/verifica_integrita_netlist_v713.py` compara **ogni nome di rete** e l'insieme preciso di **ogni coppia (reference,pin)** per rete, non soltanto numero di componenti. Risultato **99 reti prima, 99 dopo, 0 differenze nelle membership**. Il gate interrompe la build in caso di mancanza di un foglio, perdita/aggiunta di una net o qualsiasi cambio involontario.

ERC nativo standalone RX: da **76 warning (46 off-grid +15 lib symbol +15 footprint)** a **30 warning (0 off-grid +15 lib symbol +15 footprint)**, sempre **0 errori**. Root integrato: da **43 errori +416 warning** a **43 errori +370 warning**, per un totale **459→413 rilievi**. Non è ERC pulito; i 43 errori root restano bloccanti.

DRC nativo coupon RX **immutato**: **85 violazioni** (70 `via_dangling`, 15 `lib_footprint_issues`) e **63 `unconnected_items`** ulteriori. I fori da 0,30 mm V7.11 rimangono. Non vi è un PCB della radio, un piano massa fisico qualificato, né una prova di adattamento RF.

## Decisione
Integrare solo come **revisione CAD verificata**, mantenendo tutti i **15 confini inter-modulo OPEN/HOLD**, pinout FPGA SG48 HOLD, TX software permanentemente negato e tutto l'hardware TX DNP/OPEN. No KiCad ERC/DRC clean, Gerber, fabbricazione, trasmissione o prova radio.

**Prossima V7.14:** qualificare e correggere davvero librerie schematiche e footprint (15+15 RX, vendor pin/pad/termica ADL5535/SMA), poi analizzare connessioni RX `63 unconnected` e GND RF `70 dangling vias` tenendo conto del ritorno di corrente. Ridurre i 43 errori ERC root e qualificare le interfacce AUX/MCU/RX progressivamente; continuare DSP/firmware e regressioni.
