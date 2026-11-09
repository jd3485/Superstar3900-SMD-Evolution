"""Superstar 3900 SMD Evolution - piano canali preliminare V0.1.
Tutte le frequenze sono rappresentate come interi in Hz.
TX abilitabile solo su banda D, 40 canali base, e previa conformità normativa.
"""

BAND_OFFSETS_HZ = {"A": -1_350_000, "B": -900_000, "C": -450_000, "D": 0, "E": 450_000, "F": 900_000}
# Frequenze ordinarie della banda D; CH23 e CH24 rispettano l'assegnazione storica non monotona.
D_NORMAL_KHZ = (
    26965,26975,26985,27005,27015,27025,27035,27055,27065,27075,
    27085,27105,27115,27125,27135,27155,27165,27175,27185,27205,
    27215,27225,27255,27235,27245,27265,27275,27285,27295,27305,
    27315,27325,27335,27345,27355,27365,27375,27385,27395,27405,
)
ALPHA_CHANNELS = frozenset({3,7,11,15,19})

def frequency_hz(band, channel, alpha=False, ch9=False):
    """Ritorna la portante desiderata (Hz), CH9 con priorità su tutti i comandi."""
    if ch9:
        return 27_065_000
    if band not in BAND_OFFSETS_HZ or not isinstance(channel, int) or not 1 <= channel <= 40:
        raise ValueError("Banda o canale non valido")
    hz = D_NORMAL_KHZ[channel - 1] * 1000 + BAND_OFFSETS_HZ[band]
    if alpha and channel in ALPHA_CHANNELS:
        hz += 10_000
    return hz

def tx_allowed(band, channel, alpha=False, ch9=False):
    """Solo controllo logico. Non sostituisce interblocco hardware né omologazione."""
    if ch9:
        return True
    return band == "D" and not (alpha and channel in ALPHA_CHANNELS) and isinstance(channel, int) and 1 <= channel <= 40

def rows():
    for band in BAND_OFFSETS_HZ:
        for ch in range(1,41):
            yield band, str(ch), False, frequency_hz(band,ch), tx_allowed(band,ch)
            if ch in ALPHA_CHANNELS:
                yield band, f"{ch}A", True, frequency_hz(band,ch,True), False
