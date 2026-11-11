# V7.23 — test effettivo KiCad9 PCBNEW per tre librerie vendor (HOLD)

Data 11 novembre 2026. Baseline **V7.22 integrata**, [PR #23](https://github.com/jd3485/Superstar3900-SMD-Evolution/pull/23), [run 42997229515 tentativo 2 SUCCESS](https://github.com/jd3485/Superstar3900-SMD-Evolution/actions/runs/42997229515), 334 Python PASS e 132 componenti/100 reti, ERC 36/340 invariato.

## Motivo della revisione
I 16 test sui footprint V7.22 verificano i testi, le quote S-expression e i pad numerati tramite Python/regex, **non** che i tre file siano accettati dal vero parser/libmodello KiCad. Test V7.23 obbliga all'uso di **`pcbnew.FootprintLoad`** (KiCad9 libreria C++) e legge i veri oggetti pad, layer rame, mask e paste, dimensioni e coordinate. Fallisce se un file è malformato o un pad viene ignorato, e se TI RHB EP33 non ha le quattro aperture pasta non-rame corrette.

**Nessun nuovo footprint o net viene assegnato** a U6201–U6206. Tre librerie CAD V7.22 restano `HOLD`; il test è *native footprint load + land example numerical gate*, NON certificazione fisica vendor, stencil di produzione, DRC sulla PCB integrata o autorità di fabbricazione. Non scrive alcuna PCB, nessun gerber o file produttivo.

## Consumo Actions sotto controllo
L'utente ha sbloccato un budget Actions a pagamento. La CI V7.23 è **un workflow singolo su push nel solo ramo V7.23, senza evento pull_request**; test focalizzato invece di rieseguire le 334 regressioni già certificate sullo stesso master invariato. Runtime ridotto, concurrency `cancel-in-progress`. Se i check falliscono correggere soltanto dopo lettura dei veri log; non aggirare gate. I 334 test sono prove storiche V7.22, non conteggiare come nuovamente eseguiti in V7.23.

## Gate successivi
Verificare footprint-to-symbol pad 1–64,1–33,1–5 con vendor; assemblaggio solder mask/paste e tolleranze, PVT termico TPS7A20; solo poi eventuale assegnazione. Restano 48 footprint mancanti, 15 RX/MCU/AUX cross-domain OPEN/HOLD, 36/340 ERC già noti, PCB unica inesistente. **NO FAB / NO GERBER / NO PCBWAY / NO TX**, SG48 HOLD.
