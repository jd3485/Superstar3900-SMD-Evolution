# MT-01 — Manuale tecnico e degli schemi

**Stato: struttura, da redigere con gli schemi reali.**

1. Identificazione hardware: codice PCB, revisione, firmware e opzioni.
2. Specifiche elettriche nominali e limiti ambientali, con misure certificate o validate.
3. Diagramma generale: blocchi RF, FI, PLL, audio, ATU, controllo, alimentazione.
4. Schemi elettrici gerarchici *esportati dalla revisione KiCad esatta*.
5. Funzione dettagliata di ogni blocco e calcoli/dimensionamenti essenziali.
6. Connettori: vista, numerazione pin, tensioni, segnali e precauzioni.
7. Elenco componenti con riferimenti/valori/package/datasheet e sostituti qualificati.
8. Punti di misura e forme d'onda/tensioni attese, con condizioni di misura.
9. Logica 270 frequenze, CH9, ALFA, TX interlock e gestione guasti.
10. Protezioni, troubleshooting con diagrammi decisionali.
11. PCB: stackup e vincoli RF, piani di massa e schermature.
12. Dati di identificazione e cronologia revisioni.

Nessuno schema effettivo è presente alla versione V0.1.1: le relative sezioni resteranno aperte fino alla progettazione.


## Nota tecnica V0.2: guida alla futura sezione PLL
Sintetizzatore proposto ADF4351, 3,3V, LO 36,310..39,000MHz (fVCO 2,32384..2,496GHz), filtro loop da definire, riferimento TCXO 12,8MHz, R20, uscita /64, feedback fondamentale, mute-until-lock e uscita LD da leggere anche in hardware. Driver 3-wire e buffer LO filtrato non ancora disegnati. Questo **non e uno schema elettrico**; per cifre registri e pinout fara fede il datasheet verificato.

## V0.4 - Filtro CP/VTUNE e LO (bozze)
C1=6.8nF CP-GND; R2=1.2k CP-intermedio; C2=120n intermedio-GND; R3=270ohm CP-VTUNE; C3=4.7n VTUNE-GND. Collegamenti preliminari nel CSV `04_KiCad/Bozze_pre_KiCad/PLL_Loop_Reti_V0.4.csv`. Non sono schemi elettrici completi validati.

## Modulo sintetizzatore - integrazione V0.6
Sono disponibili una pinmap completa a livello di studio `04_KiCad/Bozze_pre_KiCad/LMX2572_RHA_Pinmap_V0.6.csv` e una bozza funzionale SVG. Il filtro LMX2572 usa configurazione TI Fig.179 con CPout(12) e Vtune(35). **Non e' uno schematico elettrico KiCad certificato**, e molti pin opzionali non sono ancora terminati.


## Modulo PLL V0.8
Schema incompleto: U1, bypass locali, link e filtro d'anello in bozza.
Collegamenti e valori: `01_Specifiche/LMX2572_Decoupling_Design_V0.8.md`.
Verifiche obbligatorie: KiCad ERC, netlist, layout, prove di alimentazione/PLL.

## V0.9 - modulo LDO e riferimento
Schema provvisorio: file `04_KiCad/Sorgenti_Modulo_PLL_V0.9/S3900E_PLL_V0_9_LDO_TCXO_DRAFT.kicad_sch`. U2/U3 TPS7A2033PDBVR; Y1 TXC 7N 12.8MHz. Vedi `01_Specifiche/Alimentazione_TCXO_V0.9.md` per pin e limiti. Attenzione: non e uno schema di produzione.


## Aggiornamento V1.1 - protezione ausiliaria
La rete `PWR_13V8_AUX_RAW` passa per F200 e U200 TPS26600 prima di alimentare il buck V1.0. Le soglie sono indicate nel report di calcolo; lo schema fa esplicita distinzione tra `EFUSE_RTN` e `GND_MAIN`. Nessun PCB ancora validato.


## V1.2 - reti di alimentazione
Contratto tre fogli in `04_KiCad/Integrazione_Alimentazioni_V1.2`; non ancora gerarchici. U200 eFuse -> TPS54202 -> due TPS7A20. RTN diverso GND_MAIN. D200 DNP.

## V1.4 - Interfaccia AUX e controllo geometrici
Nel progetto `04_KiCad/Gerarchico_Alimentazioni_V1.4/S3900E_AUX_POWER_V1_4.kicad_sch` il componente **J100** (simbolo di ingresso 2 poli senza footprint assegnato) esporta le reti `PWR_13V8_AUX_RAW` e `GND_MAIN`. Non dimensiona la corrente del futuro finale RF e non sostituisce la definizione del connettore meccanico. Sei reti di disaccoppiamento PLL sono state esplicitate con segmenti di filo divisi nel punto dell'etichetta.

Verifica riproducibile: `03_Verifiche/test_connettivita_geometrica_v14.py` verifica geometricamente simboli, pin, etichette, no-connect e gerarchia. **Questo controllo non e un KiCad ERC**. I footprint J100/F200 e il pin 10 Y1 restano bloccanti. Fonte Y1: TXC 7N 10-pad, pin 10 `AFC or GND` secondo la variante.


## Aggiornamento V1.5
Interfaccia seriale J101 / LMX2572: vedi `01_Specifiche/Interfaccia_SPI_LMX2572_V1.5.md`; SRC KiCad V1.5. Fino a ERC non validata.


## V1.5.1 - Blocco audio digitale da progettare
VOX/Roger Beep/Echo e toni codificati: predisporre moduli AUDIO_CTRL, MIC_DSP, SUBAUDIO_FM, SQUELCH_CODE. Nessuna pinmap hardware o connessione KiCad implementata per queste funzioni.

## V1.6 - Architettura codec e MCU (non schema esecutivo)

Candidato STM32G474RE + TLV320AIC3204, interfacce I2S/I2C e SPI PLL. Per il codec AVDD/DVDD circa 1.8V, mai 3.3V diretti. Schema elettrico e pin-map ancora non generati; vedere `01_Specifiche/Architettura_MCU_CODEC_V1.6.md`.

## Nota tecnica V2.4 - Preselettore di studio
Descrizione e risultati: `01_Specifiche/Preselettore_Bassa_Perdita_V2.4.md`. Nessun filtro approvato e nessuno schema elettrico definitivo.
