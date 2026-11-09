# V1.2 - risultati e limiti

| Operazione | Esito | Interpretazione |
|---|---|---|
| Richiamo file V1.1 e ZIP | PASS | archivo disponibile |
| Fuse 451 1.5A candidato esistente | PASS documentale | produttore/part number e package verificati |
| Footprint fuse V1.1 1206 | ERRORE CORRETTO | schemi studio V1.2 ora `CUSTOM ... NON VALIDATO` |
| SMBJ18CA candidato 18V 600W | PASS documentale | ancora DNP, surge non dimostrato |
| TCXO 7N pin 10 | AMBIGUITA CONFERMATA | AFC oppure GND, part specifica da ottenere |
| Reti interfaccia fra 3 file | PASS statico | corrispondenza nomi, NON gerarchia elettrica |
| Vecchi test Python | 8/8 PASS | leggere Log_Test_V1.2.json, non equivale a circuito |
| KiCad ERC, netlist gerarchica | NON ESEGUITI | kicad-cli assente |
| SPICE, EMI, surge, hardware | NON ESEGUITI | progettazione preliminare |

Fonte F200: https://www.littelfuse.com/assetdocs/fuse-451-and-453-datasheet?assetguid=533cd5cc-956c-4243-867f-6ab5a62f6ba1
Fonte TCXO: https://txccrystal.com/images/pdf/7n.pdf
Fonte D200: https://www.diodes.com/part/view/SMBJ18CA
