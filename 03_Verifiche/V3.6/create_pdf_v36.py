#!/usr/bin/env python3
"""Create V3.6 compact dossier from verified audit; ReportLab, no fabrication claim."""
from pathlib import Path
import json
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Table,TableStyle,Image,PageBreak,KeepTogether
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
from reportlab.lib.colors import HexColor,white
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'Superstar3900_Dossier_Tecnico_V3.6.pdf'
AUDIT=json.loads((Path(__file__).parent/'Rapporto_Audit_Indipendente_V3.6.json').read_text())
FONT='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
FONT_B='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
if Path(FONT).exists():
    pdfmetrics.registerFont(TTFont('DV',FONT));pdfmetrics.registerFont(TTFont('DV-Bold',FONT_B))
    pdfmetrics.registerFontFamily('DV',normal='DV',bold='DV-Bold',italic='DV',boldItalic='DV-Bold')
    normal,bold='DV','DV-Bold'
else: normal,bold='Helvetica','Helvetica-Bold'
NAVY=HexColor('#14263A');MUTED=HexColor('#55677C');TEAL=HexColor('#007E7D');GRAY=HexColor('#EAF0F5');ORANGE=HexColor('#B54C2E')
doc=SimpleDocTemplate(str(OUT),pagesize=A4,rightMargin=43,leftMargin=43,topMargin=52,bottomMargin=54,title='Superstar 3900 SMD Evolution V3.6 - Studio RX GND',author='Progetto S3900E',subject='Revisione V3.6, audit elettrico statico, RX only')
styles=getSampleStyleSheet()
styles.add(ParagraphStyle(name='Main36',parent=styles['Title'],fontName=bold,fontSize=21,leading=27,textColor=NAVY,spaceAfter=12,alignment=TA_LEFT))
styles.add(ParagraphStyle(name='H36',parent=styles['Heading2'],fontName=bold,fontSize=13,leading=18,textColor=TEAL,spaceBefore=15,spaceAfter=7))
styles.add(ParagraphStyle(name='Body36',parent=styles['BodyText'],fontName=normal,fontSize=9,leading=14,textColor=NAVY,spaceAfter=8))
styles.add(ParagraphStyle(name='Small36',parent=styles['BodyText'],fontName=normal,fontSize=8,leading=12,textColor=MUTED,spaceAfter=5))
styles.add(ParagraphStyle(name='Warn36',parent=styles['BodyText'],fontName=bold,fontSize=9,leading=14,textColor=ORANGE,spaceBefore=7,spaceAfter=8))
P=lambda x,style='Body36': Paragraph(x,styles[style])

def mk_table(data,widths=None,header=True):
    table=Table([[P(str(k),'Small36') for k in row] for row in data],colWidths=widths,repeatRows=1 if header else 0,hAlign='LEFT')
    commands=[('VALIGN',(0,0),(-1,-1),'MIDDLE'),('LEFTPADDING',(0,0),(-1,-1),8),('RIGHTPADDING',(0,0),(-1,-1),8),('TOPPADDING',(0,0),(-1,-1),8),('BOTTOMPADDING',(0,0),(-1,-1),7),('LINEBELOW',(0,-1),(-1,-1),0.5,HexColor('#C9D6DE'))]
    if header:commands += [('BACKGROUND',(0,0),(-1,0),NAVY),('TEXTCOLOR',(0,0),(-1,0),white)]
    for i in range(1 if header else 0,len(data)):
        if i%2==1:commands.append(('BACKGROUND',(0,i),(-1,i),HexColor('#F3F7F9')))
    table.setStyle(TableStyle(commands))
    return table

def foot(canvas, doc):
    canvas.saveState();w,h=A4
    canvas.setStrokeColor(HexColor('#D6E1E9'));canvas.line(43,42,w-43,42)
    canvas.setFillColor(MUTED);canvas.setFont(normal,7.5)
    canvas.drawString(43,29,'S3900E V3.6 • Studio tecnico RX da 50 Ω • NON PER FABBRICAZIONE')
    canvas.drawRightString(w-43,29,f'Pag. {doc.page}')
    canvas.restoreState()

story=[]
story += [P('Superstar 3900 SMD Evolution','Main36'),P('Dossier tecnico — Revisione V3.6 | 07.11.2026','Small36'),
          P('Studio delle masse e dei ritorni RF della scheda sperimentale a 50 Ω. Il lavoro riguarda un modulo RX separato dal trasmettitore; non è un progetto di produzione.','Body36')]
story.append(mk_table([
 ['Footprint','Piste F.Cu','Via GND','Zone GND'],
 ['15','43','64','4, non riempite']
],widths=[124]*4))
story.append(Spacer(1,9))
img=ROOT/'04_KiCad/Modulo_RX_Test_50ohm_V3.6/Anteprima_Ritorni_Massa_V3.6.png'
from PIL import Image as PILImage
im=PILImage.open(img);w,h=im.size
maxw=505;maxh=283;scale=min(maxw/w,maxh/h)
story.append(Image(str(img),width=w*scale,height=h*scale))
story.append(P('Anteprima generata dalla geometria della PCB: sono visibili i ritorni di massa aggiunti e i via di stitching. Non è un rendering KiCad né un piano di rame già riempito.','Small36'))
story.append(P('RISULTATO STATICO: 24 contatti GND con via locale; 31 associazioni pin-rete coerenti; 0 cortocircuiti modellati; distanza minima tra reti in 2D 0,45 mm.','Body36'))
story.append(P('BLOCCO PRODUZIONE: footprint SMA non certificato, zone non riempite, DRC KiCad nativo assente e nessuna misura VNA. NON inviare a PCBWay.','Warn36'))
story.append(PageBreak())
story.append(P('Interventi eseguiti','Main36'))
story.append(P('1 | Ritorni di massa','H36'))
story.append(P('La V3.5 conteneva tre zone GND non riempite e quattro via. In V3.6 sono stati aggiunti 20 collegamenti GND top-layer verso 20 via locali (16 terminali di massa dei quattro SMA provvisori, quattro terminali dei condensatori/ingresso alimentazione). Un ulteriore insieme di 40 via di stitching è stato disposto in modo parametrico ai lati dei percorsi RF. Totale: 64 via.'))
story.append(P('È stata aggiunta la zona GND anche a In2.Cu. Le quattro zone F.Cu, In1.Cu, In2.Cu e B.Cu rimangono tutte <b>non riempite</b>: il collegamento globale della massa resta da confermare mediante il comando nativo di refill.'))
story.append(P('2 | Riconciliazione schema ↔ PCB','H36'))
story.append(P('Corretto il numero delle piazzole dell’induttore simmetrico L101 senza cambiare i suoi collegamenti fisici: pin 1 = +5V_BENCH; pin 2 = RF_BIAS_OUT. La V3.5 non coincideva con la tabella reti dello schema V3.1. Ora tutte le 31 assegnazioni di riferimento combaciano (considerati gli alias dei nomi delle reti).'))
story.append(P('3 | Audit geometrico indipendente','H36'))
story.append(mk_table([
 ['Verifica','Risultato'],
 ['Reti alimentazione/segnale 2–8','7 su 7 con continuità geometrica'],
 ['Contatti di massa','24/24 toccano un collegamento verso via locale'],
 ['Interferenze tra reti, rame F.Cu','0 nel modello semplificato (soglia 0,20 mm)'],
 ['Distanza minima rame fra reti','0,45 mm, solo 2D'],
 ['Controlli regressione','Test inclusi; rilevano guasti iniettati'],
 ],widths=[244,252]))
story.append(Spacer(1,11))
story.append(P('Limiti: le piazzole roundrect sono approssimate come rettangoli; il controllo non comprende solder mask, pasta saldante, ingombro del corpo connettore, zone riempite, interferenza elettromagnetica, resistenza termica, ERC/DRC nativi o apertura ufficiale del file in KiCad.','Small36'))
story.append(PageBreak())
story.append(P('Bloccanti e piano di qualifica','Main36'))
story.append(mk_table([
 ['Priorità','Condizione per procedere'],
 ['SMA / Ø2,05 mm','Verificare CAD/3D e foratura/copper del CONSMA002-SMD. Il cerchio presente nel footprint è ancora segnaposto.'],
 ['ADL5535 / termica','Confermare land pattern Fig. 17, geometria paddle e stencil.'],
 ['PCBWay / impedenza','Definire stack-up ordinato; ricalcolare piste 50 Ω con spessore rame e maschera.'],
 ['KiCad nativo','Aprire e sincronizzare schema/PCB, refill GND; eseguire ERC + DRC fino a rimozione errori.'],
 ['Prototipo / test','Con alimentatore 5 V limitato, effettuare ispezione, S11/S21 con VNA, stabilità e prove di rumore.'],
 ],widths=[124,372]))
story.append(Spacer(1,13))
story.append(P('Sequenza consigliata di collaudo','H36'))
story.append(P('Con modulo isolato da TX: 1) controllo visivo e ohmetrico non alimentato; 2) alimentazione stabilizzata 5 V con limite di corrente indicativo 200 mA e monitoraggio temperatura; 3) analisi S11/S21 dell’attenuatore passivo; 4) S11/S21 dell’amplificatore con VNA a bassa potenza iniziale; 5) verifica oscillazioni e spurie; 6) figura di rumore e intermodulazione solo dopo l’identificazione di livelli sicuri per gli strumenti. Nessuna di queste misure è stata ancora eseguita.'))
story.append(P('Fonti e riferimenti','H36'))
story.append(P('Analog Devices, ADL5535 Rev. A, Fig. 16 e 17: https://www.analog.com/media/en/technical-documentation/data-sheets/adl5535.pdf','Small36'))
story.append(P('TE Connectivity / Linx, CONSMA002-SMD Rev D; PCBWay, catalogo stack-up a quattro strati (nessuno stack-up selezionato per un ordine).','Small36'))
story.append(P('Prossima fase: verificare CAD/3D SMA e impronta ADL5535, eseguire il DRC KiCad effettivo e la ricarica delle zone.','Body36'))
story.append(P('AVANZAMENTO STIMATO DELL’INTERO PROGETTO: 37% (invariato). Questi sono progressi di studio, non hardware pronto per costruzione.','Warn36'))
doc.build(story,onFirstPage=foot,onLaterPages=foot)
print(OUT,OUT.stat().st_size)
