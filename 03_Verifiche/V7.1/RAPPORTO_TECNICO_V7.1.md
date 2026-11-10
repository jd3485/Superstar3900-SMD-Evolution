# Superstar 3900 SMD Evolution — rapporto tecnico V7.1 (candidato, SOLO STUDIO)

**Data: 10 novembre 2026 · Branch feature/v7.1-tx-if-fail-closed · NON FAB / NON TX.**

## Ambito
Overlay modulatore TX / FI2 455 kHz e due conversioni candidate a 10.695MHz e banda di canale 25.615–28.305MHz. Integrati: specifica del percorso, BOM DNP, netlist 22 righe pin-to-net, ECO, modulo Python di sole forme d'onda mono-tono offline e unit test. Nessuna sorgente precedente, schema KiCad o PCB modificato.

## Risultati realmente eseguiti

| Verifica | Esito e metodo | Limite |
|---|---|---|
| Test locali Python stdlib del nuovo modello | **6 PASS / 2 SKIP / 0 FAIL**, comando `python3 -m unittest discover -s 03_Verifiche/V7.1 -p 'test_*.py' -v` sul sottoinsieme locale (otto metodi) | Due skip perché BOM/netlist e piano V6.4 non erano nel checkout locale di prova, NON contano come PASS |
| Confronto CSV completo V6.4 letto dal repository GitHub | **270/270** righe, di cui **30 ALFA**, LO1 e immagine aritmetica coerenti | Controllo aritmetico JavaScript separato; non hardware |
| Prove frequenza/modo per 270 × 5 | **1.350/1.350 PASS**; AM/FM centro, USB/LSB 1kHz e CW 700Hz, LO alto e inversione sideband | Non prova reiezione di banda laterale su parlato |
| BOM/Netlist V7.1 letti dal branch GitHub | **9/9** righe BOM DNP; **22/22** righe netlist DNP; pin 1..6 esatti sui due ADE-1+ | Coerenza di file e mapping documentale, NON ERC nativo |
| Matrice 64 combinazioni dei consensi di controllo | **64/64** RF permission False, eseguite dai test Python | L'isolamento fisico resta un vincolo DNP di progetto, non è misurato su un circuito |
| CI GitHub Actions su checkout integrale | **8 PASS / 0 SKIP / 0 FAIL**, run 42791419516, job 129745528771, esito `success` e log verificati | Esecuzione software soltanto, non valida l'hardware |
| Regressione storica completa V5.9..V7.0 | **NON ESEGUITA** in questa revisione | Il rapporto V7.0 riferiva 616 test storici, non ripetuti qui |

Calcoli di riferimento: IF1 alta =10.240+0.455=**10.695MHz**; prodotto spur IF1 basso=10.240−0.455=**9.785MHz**; immagini RF per gli estremi **47.005–49.695MHz**. Per fRF=27.065MHz con tono 1kHz: USB RF desiderata 27.066MHz generata da IF2=454kHz, LSB 27.064MHz generata da IF2=456kHz. Si tratta di selezione algebrica dei prodotti di mixer, non di una misura di spettro.

## NON ESEGUITO (NO CLAIM)
Schematico KiCad nativo, ERC/DRC, schemi di produzione, simulazioni circuitali ngspice/LTspice su IC reali, S-parameters/EM, bilancio livelli LO e IF, ripple/armoniche RF, taratura modulazione, spettri audio e portanti con hardware, EMC, termica, test di interblocco fisico e qualsiasi collaudo in TX. Nessuna connessione PA o antenna.

## Criticità e prossime decisioni
1. **Generazione IF2 completa non progettata:** servono DUC/DAC, anti-alias, Hilbert/IQ per speech SSB, FM lineare, limiter e carrier AM. Il riferimento numerico mono-tono non sostituisce firmware STM32 reale.
2. **F7201/F7202 senza MPN, qualità, impedenza, pinout o caratterizzazione**; non è provata la soppressione di 9.785 MHz, delle immagini 47..50 MHz, delle spur LO o della sideband opposta.
3. **LO1/LO2 TX senza distribuzione o autorizzazione**. Nessun LO disponibile con livello +7dBm TX certificato; l'analisi GALI-3+ V7.0 non dimostra 10.24 MHz TX.
4. **Sicurezza:** mixer U7201/U7202 e collegamenti R7201–R7205 DNP; RF_MIX_OUTPUT_NO_CONNECT isolato, R7205 lato opposto non instradato. TX_ENABLE_HARD e J801 DNI V6.2 restano incompleti; manca analisi indipendente guasti e isolamento antenna.
5. **Legacy:** problemi RX V6.7 immagine, alimentazioni/termica PLL V6.4, IF/AGC, filtri 455k e schema KiCad persistono. Nessun filtro RX è implicitamente autorizzato come filtro TX.

**Verdetto: V7.1 STUDIO DOCUMENTALE / NUMERICO. NON pronto per fabbricazione né trasmissione.** Le seguenti fasi devono completare architettura di modulazione IF2, modelli di filtraggio e potenze prima di concepire collegamenti RF.
