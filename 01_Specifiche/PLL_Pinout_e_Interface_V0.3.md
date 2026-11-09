# Scheda tecnica di progetto: PLL S3900E-SY01, V0.3

**STATO: preliminare / non idoneo alla produzione**. Questo documento specifica reti e collegamenti funzionali a livello di pin, non costituisce ancora schema KiCad completo, né validazione di un circuito funzionante. I valori che non hanno analisi specifica sono marcati come *candidati*.

## Piano numerico confermato
- U1: ADF4351BCPZ, QFN/LFCSP-32 5x5 mm con pad centrale a massa.
- TCXO: 12,800,000 Hz, 3,3 V, MPN aperto; divisore di riferimento R=20; PFD=640,000 Hz.
- Retroazione dal VCO fondamentale 2,32384-2,496GHz; divisione uscita 64.
- N intero 3631...3900, FRAC=0, MOD=2. Il prescaler 8/9 accetta tali N. Band-select divider 8 (80 kHz, sotto 125 kHz) come ipotesi iniziale.
- LO alta RF+10,695 MHz: 36,310-39,000 MHz. Prima FI 10,695 MHz da confermare.
- CH9 = 27,065 MHz RF => 37,760 MHz LO, 2,416640 GHz VCO, N=3776. L'errore aritmetico e' 0Hz, NON la stabilita reale.

## Pinout verificato sul datasheet ADF4351 Rev.A pagina 7
| Pin | Simbolo | Rete proposta | Note implementative |
|---|---|---|---|
|1|CLK|PLL_CLK|Da MCU, eventuale resistore serie 33ohm da tarare|
|2|DATA|PLL_MOSI|Da MCU, resistore serie 33ohm candidato|
|3|LE|PLL_LE|Da MCU, resistore serie 33ohm candidato|
|4|CE|PLL_CE|100kohm pulldown = spento all'avvio, valore candidato|
|5|SW|NC|Solo se non si usa la funzione fast-lock; da confermare|
|6|VP|3V3_PLL|100nF+1uF vicini; VP deve avere stessa tensione AVDD|
|7|CPOUT|LOOP_CP|Al filtro d'anello, **dimensioni elettriche ancora aperte**|
|8|CPGND|GND_RF|Piano massa continuo|
|9|AGND|GND_RF|Piano massa continuo|
|10|AVDD|3V3_PLL|100nF vicino al pin, 1uF locale, valori candidati|
|11|AGNDVCO|GND_RF|Piano massa continuo|
|12|RFOUTA+|LO_A_P|Resistore 49.9ohm verso 3V3_PLL + condensatore AC 1nF candidato|
|13|RFOUTA-|LO_A_N_DUMMY|Terminazione simmetrica 49.9ohm verso 3V3 e AC 1nF + 49.9ohm a massa; da simulare/verificare|
|14|RFOUTB+|NC|Ausiliaria disabilitata nel firmware|
|15|RFOUTB-|NC|Ausiliaria disabilitata nel firmware|
|16|VVCO|3V3_PLL|100nF vicino al pin, 1uF locale|
|17|VVCO|3V3_PLL|100nF vicino al pin|
|18|AGNDVCO|GND_RF|Piano massa continuo|
|19|TEMP|TEMP_BYPASS|Condensatore verso massa **valore da selezionare dal riferimento hardware**|
|20|VTUNE|LOOP_VTUNE|Uscita filtro d'anello, senza commutazioni digitali vicine|
|21|AGNDVCO|GND_RF|Piano massa continuo|
|22|RSET|RSET_5K1|5.1kohm a massa secondo datasheet, 1% candidato|
|23|VCOM|VCOM_BYPASS|Condensatore a massa, valore da fissare|
|24|VREF|VREF_BYPASS|Condensatore a massa, valore da fissare|
|25|LD|PLL_LOCK|Monitor GPIO con timeout; da verificare tipo uscita/necessita pull-up|
|26|PDBRF|PLL_RF_ENABLE|100kohm pulldown: uscita muta all'avvio, candidato|
|27|DGND|GND_RF|Piano massa continuo|
|28|DVDD|3V3_PLL|100nF vicino al pin|
|29|REFIN|TCXO_REF_AC|Accoppiamento AC 1nF candidato, segnale entro livelli datasheet|
|30|MUXOUT|PLL_MUX|Test point/test mode; opzionale funzione LD|
|31|SDGND|GND_RF|Piano massa continuo|
|32|SDVDD|3V3_PLL|100nF vicino al pin|
|EP|EXPOSED PAD|GND_RF|Pad esposto collegato al piano GND, vincoli via/mask da datasheet|

**ATTENZIONE:** la rete del filtro di anello fra CP_OUT e VTUNE e' tuttora assente: non alimentare U1 con questa sola tabella.

## Interfaccia LO
L'uscita ADF4351 selezionabile sino a +5 dBm non e' sufficiente di per se' per la porta LO +7 dBm del mixer passivo ADE-1. Il filtro a sette poli simulato introduce perdita in banda anche senza accoppiamenti, quindi un **buffer/amplificatore 50ohm** con rete di regolazione sara' necessario. Il relativo MPN e il dimensionamento NON sono ancora approvati. Non dimenticare attenuazione del 2GHz di fuga, armoniche e compatibilita con la porta mixer.

## Alimentazione
Dal bus radio 13,8V serve un pre-regolatore a circa 5V, seguito da LDO RF a basso rumore 3,3V; ADP7156 e' candidato ma pinout/BOM e dissipazione vanno dimensionati. Non sostituire con il piccolo ADP150 sulla sola base della scheda di valutazione: il budget complessivo di corrente deve essere verificato. Masse: un singolo piano di riferimento RF continuo; separazione delle correnti digitali con placement, non tagli casuali sotto linee RF.

## Sequenza logica e protezioni
- Default CE=0, PDBRF=0; inizializzare registri R5, R4, R3, R2, R1, R0.
- Abilitare MUTE TILL LOCK; controllare LOCK con watchdog e timeout.
- Il firmware NON puo' essere l'unico interblocco TX: il circuito hardware PTT deve impedire TX su posizioni non ammesse, interdire TX in assenza LOCK o durante autotest, e ridurre/spegnere con ROS/temperatura/corrente anomali.

## Risorse ufficiali
- https://www.analog.com/media/en/technical-documentation/data-sheets/adf4351.pdf
- https://www.analog.com/media/en/technical-documentation/user-guides/ug-435.pdf
- https://www.analog.com/en/products/adp7156.html
- https://www.minicircuits.com/pdfs/ADE-1.pdf

## Impedimenti alla promozione di stato
Filtro PLL sintetizzato con ADIsimPLL o modello completo; simulazione phase noise e spurious; livello LO reale dopo filtro/buffer; clock TCXO e MPN; pinout del regolatore; simulazione di stabilita'; schema KiCad con ERC; BOM validata per montaggio; misure su PCB campione.
