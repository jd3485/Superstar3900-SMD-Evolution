# Preselettore RF - qualificazione induttori e confronto a pari Q (V2.6)

**Stato: STUDIO, NON APPROVATO PER PCBWAY.** Ambito RX 25,615-28,305 MHz, 6 bande, 270 posizioni. Trasmissione fuori dai canali CB autorizzati non abilitata.

## Cosa cambia rispetto alla V2.5

Il confronto precedente utilizzava Q=90 per i sei filtri e Q=60 per il filtro unico. **Era un confronto con assunzioni non omogenee**. La V2.6 ripete entrambe le risposte con Q uguale a 20, 30, 45, 60, 90; i numeri NON sono valori misurati. Conserviamo la stessa topologia precedente (senza circuiti parassiti, accoppiamenti fra rami, leakage, adattamento reale tra LNA e mixer). Le perdite di 0,2 dB/relè e 0,7 dB/switch restano assunzioni, **non certificazioni @27 MHz**.

## Catalogo produttore: Coilcraft 0805CS

I seguenti dati sono riportati dal produttore a 25 °C, senza inferire il Q a 27 MHz.

| Famiglia/codice candidato | L | SRF tipica | Q minimo dichiarato (a 250 MHz) | DCR massima |
|---|---:|---:|---:|---:|
| 0805CS-181XJRC | 180 nH | 920 MHz | 50 | 0,64 Ω |
| 0805CS-221XJRC | 220 nH | 820 MHz | 50 | 0,70 Ω |
| 0805CS-241XJRC | 240 nH | 770 MHz | 44 | 1,00 Ω |
| 0805CS-271XJRC | 270 nH | 730 MHz | 48 | 1,00 Ω |

Fonte ufficiale: https://www.coilcraft.com/en-us/products/rf/ceramic-core-chip-inductors/0805-%282012%29/0805cs/

**Punto critico:** le SRF sono molto sopra i 50 MHz, ma *non* equivalgono a basse perdite garantite a 27 MHz. Il Q a 27 MHz è **non noto**: Q(250MHz) e DCR non forniscono la resistenza RF AC a 27 MHz. I valori di induttanza di catalogo sono nominalmente misurati a 100 MHz, non a 27 MHz; il comportamento effettivo va verificato con S-parameters opportunamente de-embedded oppure VNA.

## Risultati a pari Q

| Q ipotizzato | Filtro unico prima dell'LNA | Banco senza switch | Banco + 2 relè teorici | Banco + 2 SOI teorici |
|---:|---:|---:|---:|---:|
| 20 | 4.22 dB | 3.63 dB | 4.03 dB | 5.03 dB |
| 30 | 2.92 dB | 2.46 dB | 2.86 dB | 3.86 dB |
| 45 | 2.05 dB | 1.67 dB | 2.07 dB | 3.07 dB |
| 60 | 1.61 dB | 1.27 dB | 1.67 dB | 2.67 dB |
| 90 | 1.18 dB | 0.87 dB | 1.27 dB | 2.27 dB |


Il filtro unico include HP5+LP9 prima dell'LNA; il banco è solo BPF pre-LNA con LP7 dopo l'LNA. **Le due architetture non hanno uguale selettività prima del primo amplificatore**, quindi il confronto di perdita non basta per decidere. A Q=45, il BPF del banco respinge da solo circa 26,6 dB delle immagini, contro 59,4 dB del filtro unico; il contributo LP7 dopo LNA è ancora da verificare come cascata reale. L'isolamento dei rami e il leakage dei selettori possono limitare la reiezione anche se un foglio di calcolo somma 60+ dB.

## Valori commerciali: prova NON ottimizzata

Le sei L ideali V2.5 variano circa tra 191 e 209 nH. Per mostrare l'effetto dei valori commerciali, sono state sostituite tutte le L con 180, 220 o 240 nH **senza ritoccare i condensatori**. Lo studio non rappresenta una BOM ottimizzata e non dimostra che i pezzi siano inadatti. La differenza di risposta richiede una nuova sintesi e regolazioni dei condensatori C0G/NP0.

## Decisione tecnica

1. NON approvare né i sei filtri né il filtro unico come schema RF finale.
2. Richiedere la curva Q e modello S-parameter dei codici L esatti da 20 a 60 MHz, con definizione della fixture; preferire misurare un campione su test board RF con VNA calibrato.
3. Scegliere il circuito con perdite e reiezione **misurate** a 25,615, 28,305 MHz e 47,005-49,695 MHz, poi valutarne NF e IIP3 con LNA e mixer reali.
4. Preparare uno schema RF pilota a 50 ohm con piste e riferimento massa definiti, isolamento RX durante TX, e punti di misura per calibrazione.
5. Non inviare nulla a PCBWay senza KiCad ERC/DRC, simulazione SPICE realmente eseguita, BOM/footprint qualificati, analisi termiche e prove strumentali RX/TX.

## File riproducibili

- `03_Verifiche/V2.6/source_analysis_v26.py` rigenera i numeri a partire dai moduli V2.4 e V2.5.
- `03_Verifiche/V2.6/test_v26.py` controlla i dataset e gli avvertimenti su Q.
- `03_Verifiche/V2.6/*.csv`, `*.png` e `Risultati_V2.6.json` contengono i risultati matematici e i grafici.

Le sorgenti di proprietà dei produttori non sono copiate nel pacchetto: sono forniti gli URL.
