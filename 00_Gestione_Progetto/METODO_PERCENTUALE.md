# Metodo dell'avanzamento

L'avanzamento e una STIMA, non un risultato di conformita e nemmeno una previsione di durata.
La scala e 0-100% con completamento raggiunto soltanto quando sono pronti
progetto fabbricabile, schemi, BOM, PCB, file PCBWay, firmware, collaudi di prototipo
e manuali richiesti. Ogni settore contribuisce con un peso fisso; la quota raggiunta
e soggettiva e prudenziale, con blocchi in attesa delle verifiche.

In V0.8: **18% arrotondato** (17,54% calcolato).
L'assenza di ERC KiCad, di PCB, di simulazioni RF affidabili e di misure reali
impedisce di considerare una parte consistente del progetto completata.

La stima e aggiornata dopo ciascuna revisione; l'incremento puo anche essere zero
o negativo se emergono errori e viene ritirata una scelta progettuale.

## V0.9
Avanzamento secondo stessi pesi: 18.89% arrotondato **19%**. Incremento rispetto a V0.8: +1 punto nominale. Solo stima documentale, non certificazione tecnica.

## V1.0
Stessi pesi fissi. Incremento dello stato PLL/riferimento/LO per definizione del core 5V (39% -> 46%), specifiche 75% -> 77%, manuali 5% -> 8%. Nessun credito di validazione hardware, ERC o layout. Avanzamento 20% arrotondato.


## V1.1
Pesi invariati; specifiche 80%, PLL/alimentazione 48%, TX/PA 1% (solo requisiti), manuali 10%. Totale **20.99%** stimato, 21% arrotondato. La percentuale puo scendere se emergono correzioni.


## V1.2
Stessi pesi della V1.1; specifiche 82%, PLL/alimentazione 52%, manuali 12%. Totale **21.83%** = 22% arrotondato. Nessun credito per simulazioni native o prototipo. La V1.2 e solo avanzamento documentale e controllo di interfaccia.
## V1.4
23% arrotondato, senza incremento: piccole correzioni funzionali e test statici aggiuntivi; nessun ERC KiCad, nessun PCB, nessun collaudo.

## V1.5
Stessi pesi fissi. SPI protocollo codificato e cinque pin esportati nel sottosistema gerarchico. Firmware 16%; PLL 59%; specifiche 83%; manuali 17%. Totale **23.58% stimato, arrotondato 24%**. Nessun avanzamento accreditato per ERC/DRC/PCB/prove reali.

## V1.5.1
Sole nuove specifiche e test di un modello logico, senza hardware completato. Percentuale riportata **24% stimato e invariato** rispetto a V1.5. L'ampliamento del perimetro rende il residuo di lavoro maggiore; la stima verra' ricalibrata al completamento dell'architettura audio/firmware.

## V1.6
Stessi pesi della V1.5: specifiche 86%, ricezione AF 5%, firmware 21%, manuali 19%; **24,61% stimato, arrotondato 25%** (+1 punto). Nessun credito attribuito a ERC, PCB, DRC, simulazione analogica o test reali.

## V2.3
31% stimato (+1 punto): chiarito il collo di bottiglia NF e il compromesso con IIP3, aggiunti 7 scenari riproducibili, test numerici e valutazione delle alternative. Nessun credito di PCB, ERC/DRC, filtro verificato, misure o conformita'. La stima puo' retrocedere se i filtri reali non rispetteranno i target.
