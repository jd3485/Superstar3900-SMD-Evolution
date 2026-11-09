# Audio analogico - scelta V2.0

## Modifica concreta

Nel sorgente KiCad modificabile V2.0, **C227 = 100 nF** invece del precedente 1 uF. C229 resta **1 uF**.

- MIC TX: C227=100 nF, R207=1 kohm, C228=4.7 nF, input CODEC IN1_L (pin 13). Con Rin assunta 20 kohm, polo passaalto circa 79,6 Hz. Il filtro voce deve attenuare rumori di movimento e DC senza tagliare sensibilmente la banda parlata.
- FM discriminatore: C229=1 uF, R208=1 kohm, C230=10 nF, input CODEC IN2_L (pin 15). Con Rin assunta 20 kohm, polo passaalto circa 8 Hz. Serve preservare la porzione subaudio CTCSS/DCS.
- Entrambi i passabasso sono **un singolo stadio RC indicativo**; non sono sufficienti da soli a garantire un filtraggio anti-alias per Fs=48 kHz. Contiamo sul filtraggio ADC interno solo quando avremo verificato configurazione e prestazioni.

## Preamplificatore esterno

Non progettato in V2.0: il codec contiene un PGA per il microfono. Se servira' maggiore guadagno per un microfono dinamico, valuteremo un OPA2320 SMD su 3.3 V analogici (candidato, NON presente nello schema e nella BOM) con controllo dell'offset e del rumore. Per microfoni electret serviranno rete MICBIAS e verifica corrente; non e' opportuno assumere caratteristiche del microfono storico senza misure.

## Rischi / condizioni bloccanti

1. Confermare configurazione reale input ADC (impedenza 10k/20k/40k) e sua eventuale modifica tra preset.
2. Definire livelli, impedenze, CTCSS/DCS e segnale in uscita dal vero discriminatore RF.
3. Validare protezioni ESD, RF ingressi, sovramodulazione, saturazione, isolamento dal trasmettitore.
4. ERC nativo KiCad e verifica dei footprint, SPICE/AC con modelli piu realistici.
5. Nessuna validazione audio o RF hardware e' stata eseguita.

Documentazione TI: https://www.ti.com/product/TLV320AIC3204 ; https://www.ti.com/product/OPA2320
