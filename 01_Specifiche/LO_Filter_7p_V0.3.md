# SY01: filtro passa-basso LO a 7 poli - studio numerico V0.3

**Stato: sola rete ideale/distribuita approssimata, componenti non selezionati.**

Proposta: Butterworth 7 poli, R_s=R_l=50ohm, f_c=44MHz, struttura serie L / shunt C / serie L / shunt C / serie L / shunt C / serie L. Portante LO: 36,310-39,000MHz. Le designazioni teoriche sono L1, C2, L3, C4, L5, C6, L7, non riflettono il futuro codice sulla scheda.

| Posizione | Tipo | Valore analitico (non valore commerciale) |
|---|---|---|
|L1|induttore serie|80,489 nH|
|C2|capacita shunt|90,210 pF|
|L3|induttore serie|325,895 nH|
|C4|capacita shunt|144,686 pF|
|L5|induttore serie|325,895 nH|
|C6|capacita shunt|90,210 pF|
|L7|induttore serie|80,489 nH|

g_k=2sin[(2k-1)pi/(2n)]; L_serie=Z0*g/omega_c; C_shunt=g/(Z0*omega_c). Cascata ABCD, S21=2/(A+B/Z0+C*Z0+D) per porte 50ohm. In script anche modello Q_ind=60 con resistenza serie R=wL/Q (semplificazione) ed ESR_C=0,07ohm. **Nessuna misura EM, nessuna SPICE eseguita.**

Un filtro LPF non sopprime spurie vicino alla frequenza fondamentale, inclusi riferimenti PLL a +/-640kHz, e il modello a L/C concentrati non garantisce alcuna attenuazione a 2,4GHz. Il buffer, filtri addizionali e schermatura si progettano separatamente. Verificare self-resonant frequency e Q di ogni induttore commerciale prima di finalizzare.

### File eseguibili
`03_Verifiche/lo_filter_analysis.py` produce un report JSON, CSV e grafico PNG, con sweep e Monte Carlo riproducibile. `04_KiCad/Bozze_pre_KiCad/LO_LPF_7p_ngspice_draft.cir` e' una bozza per ngspice, non eseguita/validata qui.
