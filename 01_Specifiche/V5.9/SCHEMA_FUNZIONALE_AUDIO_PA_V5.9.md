# V5.9 — Progetto funzionale audio / PA, per completamento circuitale successivo

## 1. Percorsi audio separati

```text
MIC -> bias/AFE -> CODEC ADC_L -> SAI STM32 DSP -> CODEC DAC_L -> volume/mute -> ampli -> speaker RADIO
   |                                        |                         \-> speaker PA (solo se PA attiva)
   |                                        \-> CODEC DAC_R -> buffer/mute HW -> TX MOD FI (bloccato)
AM/FM/USB/LSB/CW demod -> selettore AF 5:1 -> filtro/buffer -> CODEC ADC_R -> DSP -> DAC_L
```

La scelta ADC_L MIC / ADC_R RX è obbligatoria a livello di contratto; lo schema V2.1 esistente è mantenuto. La selezione 5:1 è la **nuova sezione da progettare**, non un componente già collocato su PCB.

## 2. Componenti da scegliere con criteri vincolanti

| Sottosezione | Topologia candidata | Vincoli per schema definitivo |
|---|---|---|
| AF 5:1 | Mux 8:1 analogico o due stadi equivalenti | Alimentazione compatibile con livelli AC/DC, break-before-make, Ron/THD, iniezione carica, isolamento |
| Buffer ADC_R | Amplificatore RRIO o differenziale | Tensione di modo comune codec, headroom, THD, impedenza e filtro anti-alias |
| MIC AFE | Polarizzazione e protezione, HPF | Impedenza microfono, noise floor, alimentazione/ESD connettore |
| DAC_L -> Speaker | Mute anti-pop, volume e ampli audio | 8Ω da verificare, potenza/THD+N, dissipazione, corto/termica |
| Speaker PA | Uscita dedicata isolata | PA non deve attivare RF; anti-feedback e anti-pop; connessione schermata |
| DAC_R -> TX MOD | Buffer e doppio mute | Nessun segnale al modulatore senza consenso indipendente; percorso TX ancora aperto |
| Clock seriale | MCLK 12,288 MHz, codec master BCLK/WCLK | Layout clock, startup, SAI/DMA e registri TI da progettare |

## 3. Matrice priorità audio

1. Assenza POWER_GOOD o cambio di modo: uscite mute.
2. PA attiva: MIC -> DAC_L -> altoparlante esterno, DAC_R mute, RF inibita HW. Anche con PTT.
3. Richiesta TX non autorizzata: DAC_L mute, DAC_R mute e speaker mute; il modello **non può mai autorizzare TX**.
4. RX ordinaria: demod selezionato -> ADC_R -> DAC_L -> speaker radio.
5. CH9 forza demodulazione AM, salvo priorità PA, ma non costituisce permesso TX.

## 4. Verifiche progettuali rinviate alla fase prevista

Selezione e schema componente mux, dimensionamento filtro/buffer, THD, saturazione AFE, SPL e anti-pop, registri codec e temporizzazioni DMA; solo dopo progettazione complessiva test SPICE/audio, ERC/DRC e hardware. Questi valori **non sono simulati** nella V5.9.
