#!/usr/bin/env python3
"""Creates three-page V3.7 PDF dossier in standalone project root and /mnt/data."""
from pathlib import Path
from reportlab.platypus import SimpleDocTemplate,Paragraph,Table,TableStyle,Image,Spacer,PageBreak,KeepTogether
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT,TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'Superstar3900_Dossier_Tecnico_V3.7.pdf'
PREVIEW=ROOT/'04_KiCad/Modulo_RX_Test_50ohm_V3.7/Anteprima_Orientamento_SMA_V3.7.png'
fp='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
fb='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
pdfmetrics.registerFont(TTFont('DV',fp));pdfmetrics.registerFont(TTFont('DV-Bold',fb))
navy=colors.HexColor('#14344b');teal=colors.HexColor('#067a74');gray=colors.HexColor('#526273');pale=colors.HexColor('#eaf4f3')
styles={
 'title':ParagraphStyle('title',fontName='DV-Bold',fontSize=17,leading=21,textColor=navy,spaceAfter=7),
 'subtitle':ParagraphStyle('sub',fontName='DV',fontSize=9.4,leading=13.2,textColor=gray,spaceAfter=11),
 'section':ParagraphStyle('sec',fontName='DV-Bold',fontSize=11,leading=15,textColor=teal,spaceBefore=12,spaceAfter=6),
 'body':ParagraphStyle('body',fontName='DV',fontSize=8.55,leading=13,textColor=navy,spaceAfter=6),
 'small':ParagraphStyle('small',fontName='DV',fontSize=7.1,leading=10.5,textColor=navy,spaceAfter=4),
 'cell':ParagraphStyle('cell',fontName='DV',fontSize=7.5,leading=11,textColor=navy),
 'cellbold':ParagraphStyle('cellbold',fontName='DV-Bold',fontSize=7.5,leading=11,textColor=navy),
}
P=lambda txt,style='body':Paragraph(txt,styles[style]);elements=[]

def table(rows,widths):
    t=Table([[P(str(c),'cellbold' if j==0 else 'cell') for j,c in enumerate(row)] for row in rows],colWidths=widths,repeatRows=1,hAlign='LEFT')
    t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),pale),('LINEBELOW',(0,0),(-1,0),0.7,teal),('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,colors.HexColor('#f6f9fa')]),('BOTTOMPADDING',(0,0),(-1,-1),6),('TOPPADDING',(0,0),(-1,-1),6),('VALIGN',(0,0),(-1,-1),'TOP'),('LINEBELOW',(0,1),(-1,-1),0.3,colors.HexColor('#dde7ec'))]))
    return t

def footer(canvas,doc):
    canvas.setStrokeColor(colors.HexColor('#d0dddf'));canvas.line(17*mm,18*mm,193*mm,18*mm)
    canvas.setFont('DV',7);canvas.setFillColor(gray)
    canvas.drawString(17*mm,13*mm,'S3900E · V3.7 · studio NON approvato per la fabbricazione')
    canvas.drawRightString(193*mm,13*mm,f'Pag. {doc.page}')

elements += [P('Superstar 3900 SMD Evolution','title'),P('Dossier tecnico V3.7 • 7 novembre 2026 • Revisione dei footprint RF / 50 Ω','subtitle'),
    P('Esito principale','section'),
    P('La quota <b>Ø2,05 mm</b> del disegno TE/Linx CONSMA002-SMD, foglio 2 del documento rev. D, si riferisce al <b>land centrale del footprint SMD</b>: nel progetto rimane una piazzola di rame circolare, <b>senza foratura</b>. Il contorno completo di massa, tuttavia, non è ancora riprodotto fedelmente nel nostro footprint candidato.'),
    P('PCB aggiornata (anteprima dai dati KiCad, non rendering KiCad)','section')]
width=171*mm;img=Image(str(PREVIEW),width=width,height=width*(1221/2475))
elements+=[img,P('I connettori a sinistra (J101/J103) e a destra (J102/J104) hanno versi opposti indicati da frecce. La posizione rispetto al bordo non equivale a verifica meccanica in 3D.','small'),P('Dati del coupon sperimentale','section'),
 table([('Parametro','Valore / stato'),('Ingombro PCB','110 × 62 mm; 4 strati previsti'),('Componenti / reti','15 impronte; 8 reti elettriche'),('Rame modellato','43 segmenti, 64 via; 4 zone GND non riempite'),('Connettori','4 × CONSMA002-SMD (candidato non approvato)')],[54*mm,117*mm]),PageBreak()]

elements += [P('Confronto geometrico con i produttori','title'),P('Le quote qui sotto sono tratte dai disegni ufficiali; le corrispondenze non bastano ad approvare un footprint.','subtitle'),
 P('Connettore TE/Linx CONSMA002-SMD','section'),
 table([('Elemento','Confronto'),('Contatto centrale','Raccomandazione: land SMD Ø2,05 mm. PCB V3.7: pad 1 circolare Ø2,05, F.Cu/F.Mask/F.Paste, nessun foro.'),('Massa saldata','Il riferimento del produttore ha zone laterali sagomate; il candidato utilizza ancora quattro piazzole quadrate 1,5 × 1,5 mm. Geometria NON approvata.'),('Verso meccanico','J101/J103: 0° (verso sinistra assunto); J102/J104: 180° (verso destra assunto). Il verso effettivo richiede il modello 3D.'),('Distanza da bordo','I centri dei land sono a 8 mm dal bordo laterale; ingombro e interferenza del corpo metallico da controllare.')],[52*mm,119*mm]),
 P('Amplificatore Analog Devices ADL5535','section'),
 table([('Elemento','Confronto'),('Piazzola GND esposta','In V3.7: pad 2 da 1,80 × 3,48 mm, coerente dimensionalmente con Fig.17; metodo di saldatura ancora da verificare.'),('Tre terminali','Piazzole nominali 0,86 × 1,27 mm su centri x = -1,50 / 0 / +1,50 mm: solo verifica geometrica parziale.'),('Termica e solder paste','Occorre definire via termici, evitare il drenaggio dello stagno e validare apertura stencil con il fabbricante.')],[52*mm,119*mm]),
 P('Fonti','section'),
 P('TE/Linx CONSMA002-SMD rev. D, fogli 1–2: <link href="https://www.ic-components.cz/files/17/CONSMA002-SMD.pdf" color="#067a74">scheda dimensionale</link>. Analog Devices ADL5535 rev. A, Fig.16–17, p.11: <link href="https://www.analog.com/media/en/technical-documentation/data-sheets/adl5535.pdf" color="#067a74">datasheet ufficiale</link>.','small'),PageBreak()]

elements += [P('Audit e rilascio della scheda','title'),P('Verifiche software completate nella V3.7, con limiti esplicitati','subtitle'),
 table([('Controllo','Esito'),('Confronto pin–rete','31 associazioni coerenti con la tabella dello schema V3.1.'),('Connettività percorsi','7 reti non GND continue secondo modello geometrico indipendente.'),('Collegamenti a massa','24 contatti su 24 con un via GND locale attraverso rame esplicito.'),('Interferenze di rame, modello 2D','Nessuna violazione sotto la soglia esplorativa di 0,20 mm; distanza minima calcolata 0,45 mm.'),('Test negativi','Riconosciuti: pad SMA trasformato indebitamente in through-hole e orientamento destro mancante.'),('KiCad CLI nativo','NON DISPONIBILE. Installazione da repository non riuscita per assenza di rete.'),('Riempimento zone','NON ESEGUITO. Le quattro zone sono soltanto definite.'),('Misure RF e temperatura','NON ESEGUITE. Nessun collaudo fisico né simulazione EM/termica.')],[58*mm,113*mm]),
 P('Condizioni obbligatorie prima di ordinare','section'),
 P('1. Acquisire footprint ufficiale TE o ricostruirlo con geometrie conformi, poi verificare l’apertura del connettore rispetto al bordo con modello STEP. <b>Non praticare un foro da 2,05 mm senza prescrizione documentata.</b>'),
 P('2. Validare la geometria di saldatura e i via termici dell’ADL5535, comprese solder mask e paste.'),
 P('3. Aprire il file in KiCad; riempire i piani, eseguire DRC, verificare lo schema associato e correggere tutte le violazioni.'),
 P('4. Confermare stack-up e impedenza 50 Ω con PCBWay; poi provare S11/S21 e alimentazione su coupon RX separato dal TX.'),
 P('Comando KiCad documentato per DRC (da eseguire su macchina dotata di KiCad):','section'),
 P('<font name="DV">kicad-cli pcb drc -o DRC_V3.7.txt S3900E_RX_TEST_50R_V3_7_SMA_FOOTPRINT_REVIEW_NOT_FOR_FAB.kicad_pcb</font>','small'),
 P('Decisione V3.7: BLOCCO PRODUZIONE. Nessun Gerber generato e nessun ordine PCBWay autorizzato. Progetto complessivo stimato: 37% (invariato).','section')]
OUT.parent.mkdir(parents=True,exist_ok=True)
SimpleDocTemplate(str(OUT),pagesize=A4,rightMargin=18*mm,leftMargin=18*mm,topMargin=17*mm,bottomMargin=23*mm,title='Superstar3900 SMD Evolution Dossier V3.7',author='Progetto S3900E',pageCompression=1).build(elements,onFirstPage=footer,onLaterPages=footer)
import shutil
shutil.copy2(OUT,Path('/mnt/data/Superstar3900_Dossier_Tecnico_V3.7.pdf'))
print('Created',OUT,'size',OUT.stat().st_size)
