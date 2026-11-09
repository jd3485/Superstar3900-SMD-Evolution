# Registro V1.5

PASS: test software SPI 24 bit, validazione delle interfacce, suite di regressione preesistenti (log dedicati).
NON ESEGUITO: ERC/netlist nativi KiCad (`kicad-cli` assente), breadboard / misure RF, certificazione TX.
NOTA: un audit su etichette e connettivita geometrica NON sostituisce netlist elettrica KiCad.
BLOCCANTE: TCXO pin10 AFC/GND e footprint; HOST MCU; pin CE e MUXout; vari cablaggi di alimentazione e filtri.
Il driver Python crea frame e non fornisce configurazioni radio funzionanti.
