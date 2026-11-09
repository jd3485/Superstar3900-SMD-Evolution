# Fonti dimensionali e regole di progettazione — V3.8

- TE Connectivity / Linx, CONSMA002-SMD-G Rev B, *recommended footprint*: https://www.mouser.com/datasheet/2/418/9/ENG_DS_CONSMA002_SMD_G_B-3238924.pdf
- Analog Devices, ADL5535 Rev A, figure 16 e 17: https://www.analog.com/media/en/technical-documentation/data-sheets/adl5535.pdf
- KiCad official footprint recommendations, pad paste coverage 50–80%: https://klc.kicad.org/footprint/f6/f6.3/
- KiCad custom copper pads documentation: https://github.com/KiCad/kicad-doc/blob/master/src/pcbnew/pcbnew_creating_editing_footprints.adoc
- PCBWay official 4-layer stackups: https://www.pcbway.com/multi-layer-laminated-structure.html

## Limite importante
Le piazzole SMA vengono *modellate come candidati sagomati*, non trascritte fedelmente dal disegno quotato. Controllo nativo DRC, CAD/3D, impedenza e processo di assemblaggio NON eseguiti.
