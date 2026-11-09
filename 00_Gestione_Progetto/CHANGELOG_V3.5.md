# Changelog Superstar 3900 SMD Evolution V3.5

- **37% invariato**: i progressi di layout non sostituiscono DRC o un coupon misurato.
- 15 componenti invariati; nuova footprint candidate U101 derived from ADI Fig17 (3 pin + exposed paddle tied to GND).
- R201/R202 ruotate in configurazione shunt rispetto alla traccia RF e riposizionate.
- Collegamenti pilota F.Cu su tutte le reti non-GND (2-8); ground zones ancora non riempite.
- Rame 35 um considerato in un modello a prima approssimazione, W~0.280 mm per 50 Ohm su stack-up ipotizzato. NO controlled impedance approval.
- SOT-89 e SMA ancora da confermare meccanicamente (diametro Ø2.05 nello SMA non interpretato come foro).
- Test Python e verifica intersezioni geometriche; nessun KiCad ERC/DRC, Gerber e VNA.
- ZIP cumulativo e PDF tecnico aggiornati, preservando lo storico.
