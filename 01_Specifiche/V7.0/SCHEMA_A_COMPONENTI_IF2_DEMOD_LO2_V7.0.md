# V7.0 — schema a componenti CANDIDATO, NON schematico KiCad/ERC

## Derivazione da V6.9 e V6.8
Le nuove parti sono un overlay sulla V6.9, **non** correzioni silenziose ai file passati. `D991`, `B991`, `B992` erano prototipi/placeholder: **DNP** quando si usa la nuova catena AM/FM. F823/F824 da V6.8 sono **DNP**. Non aggiungere in parallelo l'uscita vecchia e nuova. Nomi delle interfacce e pin sono nel CSV; molte parti J/B precedenti restano senza MPN.

## AM — U7101 AD8307ARZ SOIC8
- Pin dal datasheet ADI: INM1, COM2, OFS3 NC, OUT4, INT5 NC, ENB6, VPS7, INP8. 3V3 filtrata, C7103 100n + C7104 1µ; entrada 455k via R7101=910Ω e C7101=10n, INM cap C7102=10n verso massa senza cortocircuitare il bias DC del chip. Circa 910Ω+1.1kΩ di resistenza equivalente d'ingresso **nel modello**, non considerare la capacità/parassiti insignificanti senza prova.
- ENB6 = AM_DETECT_EN tenuto LOW da R7102=100k finché J7102 non riceve un consenso hardware RX **realmente definito**. Q7101 è un'opzione non collegata all'abilitazione definitiva: DNP per non invertire inavvertitamente il consenso.
- OUT4 via R7103=1k/C7105=10n (~15.9kHz) e accoppiamento C7111=1µ verso U7104A non invertente polarizzato a VREF=1.65V, guadagno ~2 con R7112/R7113 10k. U7104A: SOIC8 1=OUTA 2=INA− 3=INA+ 4=GND 5=INB+ 6=INB− 7=OUTB 8=VCC. J7103 AM audio via C7114, R7117=100k a massa. L'uscita è **logaritmica, non lineare**: firmware opzionale stima la risposta inversa, richiede calibrazione reale.

## FM — U7102 TLV3201AIDBVR e U7103 CD74HC4046APWR
- U7102 pin 1=OUT 2=GND 3=IN+ 4=IN− 5=VCC; ingresso filtrato 455k via C7106 10n e R7105 47k VREF, ingresso invertente 1.65V. Serve amplitude IF sufficiente, e verifica dell'isteresi a segnali deboli.
- U7103 pin esatti: 1=PCPOUT NC, 2=PC1OUT, 3=COMPIN, 4=VCOOUT, 5=INH, 6=C1A, 7=C1B, 8=GND, 9=VCOIN, 10=DEMOUT, 11=R1, 12=R2 NC, 13=PC2OUT NC, 14=SIGIN, 15=PC3OUT NC, 16=VCC. PC1OUT→R7107 10k→VCOIN9, C7109=10n a massa. VCOOUT4→COMPIN3; 455k comparatore U7102→SIGIN14. R7106 10k VCO R1→massa e C7108 100p tra pin6/7 sono **VALORI DI PARTENZA DA TARARE**: non consentono dichiarazione center 455kHz senza calibrazione reale. R7108=100k DEMOUT10→GND secondo datasheet. INH5 pullup R7109 10k = PLL spento su circuito scollegato; Q7102 2N7002 abilita solo con HW_RX_SAFE vero, interfaccia HARDWARE da concludere.
- DEMOUT10 via C7112=1µ→U7104B non invertente a 1.65V, R7115=10k/R7116=39k => gain4.9, C7115 1µ verso uscita FM/audio V6.0. I 20mVpp di modello possono essere adeguati alla scala codec solo dopo misura e controllo AGC. CD74HC4046A a 3.3V VCO ammesso, ma fcentro e K_VCO non garantiti.

## LO2 a +7dBm — U7121 GALI-3+ con LPF 5 poli
- Si5351C CLK0 V6.9 J7121 → R7121=1.5k **per non sovraccaricare il CMOS**, C7121 100n DC block → GALI-3+ RF_IN1, GND2/4, RF_OUT+DC3. Alimentare da 5V tramite R7122=47Ω, bypass C7122/C7123 e choke L7121=4.7µH candidato con SRF da verificare. 35mA nominali, caduta 1.65V sul resistore, ~0.058W dissipati. Nessuna garanzia +7dBm a 10.24MHz: 22.4dB tipici sono dati datasheet **a 100MHz**.
- Out pin3 → C7124 100n → rete 50Ω LPF L7122=330n/C7125=360p/L7123=1.1µ/C7126=360p/L7124=330n → pad π 2dB R7123=430Ω/R7124=11.5Ω/R7125=430Ω → C7127 100n → J7122 e **solo dopo misura** U802 ADE-1+ LO pin6. Esigere Q/SRF dei tre induttori oltre la terza armonica 30.72MHz; back-annotation PCB e test spur indispensabili. LPF analogica calcolata con due porte 50Ω in simulazione numerica, non è s-parameter misurato.

## SSB/CW filtri realmente implementabili
- **V7.0 realizza FIR digitale post-rivelatore** sul codec 48kHz: coefficiente Q15 e codice testabile allegati. USB/LSB banda audio 300–2700 Hz, CW 500Hz nominali centrati 700Hz; ritardo del FIR dichiarato. NESSUNA pretesa di filtro stretto **a 455kHz** reale: F823/F824 DNP finché non è confermata una parte in produzione con matching 2kΩ. La selettività DSP non impedisce che un forte adiacente saturi l'AGC IF1 o il mixer IF2; filtri IF guard e protezione segnali forti ancora aperti.

## Sicurezza e integrazione
- PA, PTT, canale 9 e fault impostano mute; V6.2 resta blocco TX indipendente, RF TX **mai abilitata**. Le nuove uscite J7103 devono essere selezionate e condizionate prima del J605 V6.0; B991/B992 non si devono montare. Raccordare 3V3_A_IF e 5V_A_RF alla V6.3 con **nuovo bilancio**. Niente ERC, DRC, phase noise, hardware, fabbricazione o TX.
