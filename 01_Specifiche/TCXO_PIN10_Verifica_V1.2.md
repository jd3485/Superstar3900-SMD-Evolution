# TXC 7N 12.8 MHz: verifica pin 10 - V1.2

Fonte serie originale TXC: https://txccrystal.com/images/pdf/7n.pdf

Il pinout GENERICO 7N a 10 pad indica: 4 GND, 5 OUT, 8 Tri-State/Enable, 9 VCC, **10 AFC oppure GND**. Le piazzole 1,2,3,6,7 sono NC nella tabella di serie.

Il codice scelto `7N-12.800MBP-T` e' attivo e commercializzato come CMOS 3.3 V / 10 pad, ma la tavola DI SERIE non determina da sola se il pin 10 di questa specifica variante sia AFC oppure GND. **La connessione elettrica del pin 10 resta BLOCCATA.**

L'attuale bozza PLL usa la net simbolica `TCXO_PIN10_AFC_OR_GND_TBD`, da NON alimentare e da NON connettere a massa senza conferma TXC. Va chiesta specifica d'ordine, drawing per singolo MPN e conferma del pin 10. Il footprint preciso 7.0x5.0mm va disegnato da land pattern ufficiale e controllato con KiCad; il placeholder non e' fabbricabile.

Nota tecnica: la stabilita' termica +/-0.28 ppm NON equivale alla accuratezza iniziale complessiva. Il datasheet di serie indica tolleranza iniziale +/-2ppm e invecchiamento +/-1ppm/anno (massimi indicati); non dichiarare quindi la radio precisa a +/-0.28ppm senza calibrazione e budget completo.
