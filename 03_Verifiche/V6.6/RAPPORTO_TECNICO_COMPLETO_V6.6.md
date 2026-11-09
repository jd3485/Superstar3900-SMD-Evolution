# Superstar 3900 SMD Evolution — Rapporto tecnico V6.6

**9 novembre 2026 — F501: preselettore RF 50Ω RX-only. Progetto ancora in sviluppo. NO FAB / NO TX.**

## Nuovo circuito candidato

Questa revisione trasforma il BPF ideale V6.5 in una **rete LC a tre risonatori** modellabile mediante parametri fisici a 50Ω: due induttori serie da 2,0µH e due gruppi da 17,5pF, ramo centrale verso massa da 22nH in parallelo a 1591pF. I sei condensatori sono suddivisi nei valori candidati 16pF+1,5pF per i gruppi serie e 1500pF+91pF per lo shunt. **3 induttori, 6 condensatori**, due interfacce coassiali: BOM completa per la topologia *ma senza MPN induttori con Q/SRF verificati*.

La sintesi teorica N=3 Butterworth 50Ω f1=25MHz/f2=29MHz porta a 1,98944µH, 17,5619pF, 21,9524nH, 1591,55pF. Gli arrotondamenti spiegano il disallineamento residuo. Vedi schema e netlist in `01_Specifiche/V6.6/`.

## Simulazioni effettivamente eseguite (Python, rete di componenti ideali/perdenti)

Con QL=60, QC=400, SRF serie 90MHz, SRF shunt 350MHz, C_FEED ingresso–uscita 0,05pF (**tutti ASSUNTI, nessun produttore reale**):

- 270/270 frequenze RX 25,615–28,305MHz e 270 immagini 47,005–49,695MHz.
- Perdita RX minima 3.307dB, massima **5.593dB**.
- Attenuazione minima immagine **52.834dB** e reiezione relativa minima **47.956dB**.
- **Return loss peggiore 6.179dB**: NON supera obiettivo interno provvisorio di 10dB sull'intera banda.
- Feedthrough ipotetico 0pF -> attenuazione immagine minima 61.73dB; 0,1pF -> 48.53dB; 0,5pF -> 35.88dB; 1pF -> 30.01dB.
- **4.000** scenari di stress con L ±5%, C ±2%, QL 30–110, QC 300–700, SRF serie 55–150MHz e C_FEED 0–0,5pF: **46.83%** hanno massima perdita RX >6dB, **71.95%** hanno reiezione relativa <40dB e **96.85%** hanno RL minimo <10dB. Sono variazioni arbitrariamente distribuite per stress e non probabilità di fabbricazione.
- Valutazione S11/S21 passiva in rete matriciale Y, modellazione ESR Q e winding C in funzione di SRF, nessun campo EM/layout reale. Il file `.cir` per ngspice è **preparato ma ngspice NON eseguito**.

**Conclusione circuito discreto**: studio valido come topologia riproducibile, **non accettato per produzione né per prestazioni garantite**. Criticità: SRF e Q di 2µH a 27MHz, mismatch, perdite, feedthrough del PCB, dipendenza dai modelli.

## Alternativa SMD preferenziale: Mini-Circuits SXBP-27R5+

Il datasheet pubblica porta **50Ω**, passband 24–31MHz, 1,3dB perdita tipica/2,5dB massima a 25°C; VSWR tipico1,4 max1,7; stopband alta 39–900MHz, attenuazione **minima 20dB** (non 50–53dB garantiti), pin1 ingresso/pin8 uscita/pin2–7 GND, case HF1139 di circa 18,8×11,18mm. Tutte le 270 frequenze utili ricadono nella banda e le 270 immagini nella stopband garantita. Il **20dB minimo vendor** potrebbe essere insufficiente per il futuro budget blockers: non considerare F501 già approvato.

Riferimento primario Mini-Circuits: https://www.minicircuits.com/pdfs/SXBP-27R5%2B.pdf , confronto sul prodotto https://www.minicircuits.com/WebStore/dashboard.html?model=SXBP-27R5%2B . Il precedente mixer ADE-1+ resta candidato 50Ω con LO +7dBm; il filtro non risolve il driver LO né la dinamica RF.

## Test/regressioni e archivio

**50 test V6.6 superati**, inclusi controllo frequenze, LC, 2-porte, passività, immagini, bypass, casi peggiori e sicurezza TX. **8 suite selezionate V5.9–V6.6** superate (V6.1 include due file); non è riesecuzione di tutte le suite storiche. Risultati test dettagliati in `03_Verifiche/V6.6/REGRESSIONI_SELEZIONATE_V6.6.json`. Storico V6.5 preservato integralmente; i documenti attivi modificati sono duplicati byte-per-byte sotto `09_Archivi_Precedenti/Snapshot_Integrali_V6.5/`.

## Blocchi aperti / prossima V6.7

1. Fornire part numbers Q/SRF certi o preferire il modulo schermato SXBP con footprint originale vendor, validare portata e temperature, non inventare test bench.
2. Determinare posizione filtraggio vs LNA ADL5535 e protezioni RX, calcolare budget di guadagno/rumore/blocchi, verificare selettività integrata; idealmente preselector prima della parte amplificatrice, ma compatibilità con PCB V5.x da revisionare.
3. Qualificare S2P/prestazioni a 47–50MHz e misura VNA, schermatura e capacità ingresso-uscita, matching dinamico mixer; se il target di blocco richiede più di 20dB min vendor, riprogettare.
4. Chiudere driver LO +7dBm, FI 10,695MHz, IF AGC/demod e difetto termico PLL V6.4.
5. NESSUNA validazione KiCad/DRC/ERC o hardware è stata fatta in questa revisione. La progettazione completa proseguirà per moduli; la verifica complessiva con KiCad e simulazioni approfondite resta prevista alla fine, mantenendo le prove incrementali.

**NO FAB / NO TX.**
