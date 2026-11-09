# Protezione ausiliaria: F200 e D200 - V1.2 (studio, DNP)

## Ambito
Questa revisione coinvolge solo l'elettronica ausiliaria a 5 V: RX/PLL digitale, non il finale RF o il PA. Sequenza prevista:
`13.8V_AUX_RAW -> F200 -> EFUSE_VIN [+ D200 TVS DNP] -> TPS26600 -> BUCK_VIN_PROTECTED -> TPS54202 -> 5V_RF_PREREGULATED -> LDO PLL/TCXO`.

## F200 candidato
- Littelfuse `045101.5MRL`, Nano2 451 rapido 1.5 A, 125 V DC/AC; R fredda tipica 0.063 ohm e I2t di fusione nominale 0.853 A2s.
- **Correzione critica:** precedente bozza definiva `Fuse_1206_3216Metric`, non compatibile dimensionalmente col package 451 di **6.10 x 2.69 mm**. Ora il file di studio usa `S3900E:LF_451_FOOTPRINT_NON_VALIDATO` e **non puo essere mandato in produzione**.
- Il potere d'interruzione (consultare curva e tensione applicata) e la corrente di cortocircuito disponibile dall'alimentatore/batteria devono essere verificati. La presenza di un eFuse da 1.46 A significa che un corto a valle NON deve essere ipotizzato capace di fondere F200; F200 e' una protezione di backup per guasti catastrofici; serve anche fusibile generale a monte dell'apparato.

## D200 candidato
- `SMBJ18CA` bidirezionale, VRWM=18 V, VBR=20.0-22.1 V, VC=29.2 V al picco di prova, 600 W solo per impulso specificato 10/1000us.
- Mantenuto **DNP (non montare)** fino a simulazione e prova surge; il Vclamp NON e' la soglia OVP dell'eFuse (circa 16.3 V) e non garantisce la sicurezza contro tutti i disturbi o con cavi lunghi.
- La TVS shunt puo' creare correnti impulsive che richiedono la verifica di I2t, potere di interruzione, layout e cablaggio. Non e' una protezione contro inversione di polarita'; quella e' affidata all'eFuse.

## Stima di corrente
La cartella `03_Verifiche/Stima_Corrente_Ausiliaria_V1.2.csv` contiene scenari VIN=10.5..16V, carico 5V=0.25..2A e rendimento *ipotizzato* 85%. Non sono misure ne' un rating dell'intero apparecchio.

## Rischi e prove obbligatorie
1. Modello surge IEC, tensioni e lunghezza cavo definiti; stress all'ingresso eFuse & TVS.
2. Inrush, thermal, esito corto, protezione continua e coordinamento con F200 e fusibile principale.
3. Cavi + massa: eFuse `EFUSE_RTN` resta separato da `GND_MAIN` secondo datasheet; impedire accidentalmente il corto nel layout.
4. Rendimento e EMI TPS54202, ripple alimentazioni PLL e noise floor RX misurati.
5. DNP fino all'approvazione di BOM, schemi e layout.

## Fonti
- https://www.littelfuse.com/assetdocs/fuse-451-and-453-datasheet?assetguid=533cd5cc-956c-4243-867f-6ab5a62f6ba1
- https://www.ti.com/lit/ds/symlink/tps2660.pdf
- https://www.diodes.com/part/view/SMBJ18CA
