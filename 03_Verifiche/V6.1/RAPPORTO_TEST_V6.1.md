# Report esecuzione test V6.1

- Verifiche statiche **55/55** superate: pin STM32 e MCP23017, collisioni, priorità, piano 270 posizioni e 10.000 combinazioni pseudocasuali TX OFF.
- Integrazione con audio V6.0: **5/5**.
- Simulazione sintetica rimbalzi: **2.000 scenari** (durate 0–15 ms, campione 5 ms), primo stato stabile su nuova banda da 15 a 30 ms; nessun TX in tutti i casi. Non rappresenta un encoder/meccanismo fisico misurato.
- ODE RC SciPy `solve_ivp` integrata e confrontata con analitica: errore massimo 6e-11 V (solo modello ideale). Sweep random 10.000 combinazioni tolleranze: LOW ratio massimo 0.0237 V/V, HIGH sopra soglia entro 1.998 ms; non equivale a SPICE con parassiti reali.
- Regressioni precedenti V4.0–V6.0: 2/21 suite riuscite, 19 non rieseguite nell'ultimo pacchetto per limiti di risorse, 0 fallite; dettagli JSON allegato.
- **Nessun ERC/DRC nativo né firmware compilato né hardware validato.** Fabbricazione bloccata e RF TX sempre OFF.
