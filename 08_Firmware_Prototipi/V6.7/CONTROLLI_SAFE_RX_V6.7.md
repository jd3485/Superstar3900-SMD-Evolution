# Safety interface RX front end V6.7

L'architettura RX NON comanda la trasmissione. Qualsiasi stato PA, PTT, power-good mancato, PLL unlock, fault oppure reset deve considerare l'RF RX in stato *non garantito* finché non esisterà un interblocco hardware della reale antenna e del rail ADL5535. Il solo flag MCU non protegge un LNA da energia RF. La sequenza futura andrà verificata con relè antenna (break-before-make e isolamento misurato), detector e gate analogico. **Nessun codice qui attiva TX.**
