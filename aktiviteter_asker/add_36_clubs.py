#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Genererar 36 nya undersidor och uppdaterar index.html for askeridrett.no"""
import io, sys, re, os, shutil
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT = r"C:\Users\janss\.openclaw\workspace\andersjansson-dev\aktiviteter_asker"
IDX = os.path.join(ROOT, 'index.html')

# Rensa tidigare misslyckade försök (radera befintliga nya undersidor)
to_clean = ["advania-norge-bedriftsidrettslag","ak-fryktlos","askerboringene-il","asker-cykleklubb-2","asker-helsesportlag","asker-kunstlop-klubb-akk-2","asker-miniracing-club","asker-modellklubb","asker-skyteklubb-2","asker-trekkhundklubb","fekteklubben-frie-duellister","hard-intensiv-trening-hit","holmenparken-idrettslag-2","hurum-croquet-klubb","norsk-if-bat-klubb","red-crown-bk","royken-cykleklubb","royken-og-hurum-modellflyklubb","royken-orienteringslag","royken-sportsdykkerklubb","sunyata-aikido-dojo","veteranenes-fallskjermklubb","vingtor-rc-club","asker-fleridrettslag","frisk-superlag","hagahogget-lomlag","nmk-asker","nordlys-cricketklubb-asker","oslofjordens-friluftsrad","slemmestad-brettklubb","slemmestad-kajakklubb","spuvi","team-cyan-ost","tofte-idrettslag","warya-idrettsklubb"]
for s in to_clean:
    p = os.path.join(ROOT, s + '.html')
    if os.path.exists(p):
        os.remove(p)
print("Rensade", len(to_clean), "potentiella filer")

# (name, slug, activity, url, desc, is_fb)
CLUBS = [
    ("Advania Norge Bedriftsidrettslag","advania-norge-bedriftsidrettslag","bedriftsidrett","http://www.advania.no/","Bedriftsidrett – aktivitetstilbud for ansatte.",0),
    ("Ak Fryktløs","ak-fryktlos","fallsjermhopping","http://www.fryktlos.no","Fallskjermhopping – adrenalin og mestring i luften.",0),
    ("Askerbøringene IL","askerboringene-il","fleridrett","http://www.askerboringene.no","Fleridrettslag – varierte aktiviteter for alle.",0),
    ("Asker Cykleklubb","asker-cykleklubb-2","sykling","http://asker-ck.no/","Sykling – landevei og terrengsykling.",0),
    ("Asker Helsesportlag","asker-helsesportlag","helsesport","http://www.askerhelsesportlag.no","Helsesport – aktivitet og folkehelse.",0),
    ("Asker Kunstløp Klubb Akk","asker-kunstlop-klubb-akk-2","kunstløp","http://www.akk.no","Kunstløp – eleganse, balanse og teknikk på is.",0),
    ("Asker Miniracing Club","asker-miniracing-club","motorsport","http://www.amrc.no","Miniracing – motorsport for barn og unge.",0),
    ("Asker Modellklubb","asker-modellklubb","modellflyging","http://askermodellklubb.no","Modellflyging – bygg og fly radiostyrte modeller.",0),
    ("Asker Skyteklubb","asker-skyteklubb-2","skyting","http://www.askerskyteklubb.no","Skyting – presisjon og konsentrasjon.",0),
    ("Asker Trekkhundklubb","asker-trekkhundklubb","trekkhund","http://asker-trekkhundklubb.webnode.com/","Trekkhund – hundesport og samarbeid.",0),
    ("Fekteklubben Frie Duellister","fekteklubben-frie-duellister","fekting","http://www.frieduellister.no","Fekting – elegant kampsport med hurtighet.",0),
    ("Hard Intensiv Trening (HIT)","hard-intensiv-trening-hit","trening","http://www.hitrening.no","HIT – høyintensiv trening og styrke.",0),
    ("Holmenparken Idrettslag","holmenparken-idrettslag-2","fleridrett","http://www.holmenparken.no","Idrettslag – lokale aktiviteter i Holmenparken.",0),
    ("Hurum Croquet Klubb","hurum-croquet-klubb","croquet","http://hurumcroquet.no","Croquet – presisjonsport i hagen.",0),
    ("Norsk If-Båt Klubb","norsk-if-bat-klubb","båt","http://www.ifklubben.no","IF-båt – seiling og båtliv.",0),
    ("Red Crown BK","red-crown-bk","bowling","http://klubber.bowling.no/red_crown_bk/","Bowling – spennende lagspill med ball.",0),
    ("Røyken Cykleklubb","royken-cykleklubb","sykling","http://Cykleklubb.no","Sykling i Røyken – landevei og terreng.",0),
    ("Røyken Og Hurum Modellflyklubb","royken-og-hurum-modellflyklubb","modellflyging","http://www.rhmfk.org","Modellflyging – radiostyrte fly i Røyken/Hurum.",0),
    ("Røyken Orienteringslag","royken-orienteringslag","orientering","http://www.roykenolag.no","Orientering – kart, kompass og terreng.",0),
    ("Røyken Sportsdykkerklubb","royken-sportsdykkerklubb","dykking","http://www.rsdk.no","Sportsdykking – undervannseventyr.",0),
    ("Sunyata Aikido Dojo","sunyata-aikido-dojo","aikido","http://www.sunyata.no","Aikido – japansk kampsport med flyt.",0),
    ("Veteranenes Fallskjermklubb","veteranenes-fallskjermklubb","fallsjermhopping","http://www.fallskjermveteranene.com","Fallskaermhopping for veteraner.",0),
    ("Vingtor RC Club","vingtor-rc-club","modellflyging","http://www.vingtor.org/","RC-modeller – fly, bil og båt.",0),
    ("Asker Fleridrettslag","asker-fleridrettslag","fleridrett","https://facebook.com/askerfleridrettslag/","Fleridrett – varierte aktiviteter for alle.",1),
    ("Frisk Superlag","frisk-superlag","fleridrett","https://facebook.com/Friskasker/","Superlag – aktivitet for alle.",1),
    ("Hagahogget Lømlag","hagahogget-lomlag","fleridrett","https://facebook.com/hagahogget/","Lømlag – fotball og aktivitet.",1),
    ("NMK Asker","nmk-asker","motorsport","https://www.facebook.com/people/NMK-Asker/100038813173792/","Motorsport – racing og bilcross i Asker.",1),
    ("Nordlys Cricketklubb Asker","nordlys-cricketklubb-asker","cricket","https://facebook.com/p/Nordlys-Cricketklubb-Asker-61559490254915/","Cricket – lagspill som vokser i Norge.",1),
    ("Oslofjordens Friluftsråd","oslofjordens-friluftsrad","friluftsliv","https://facebook.com/oslofjf/","Friluftsliv – turer og natur rundt Oslofjorden.",1),
    ("Slemmestad Brettklubb","slemmestad-brettklubb","brettsport","https://facebook.com/groups/500551278484246/","Brettsport – surf og SUP i Slemmestad.",1),
    ("Slemmestad Kajakklubb","slemmestad-kajakklubb","kajakk","https://facebook.com/slemmestadkk/","Kajakk – padling på Oslofjorden.",1),
    ("Spuvi","spuvi","fleridrett","https://facebook.com/p/Spuvi-100057414521143/","Spuvi – aktiviteter og sport.",1),
    ("Team Cyan Øst","team-cyan-ost","sykling","https://facebook.com/teamcyansykkel/","Sykkel og triatlon – Team Cyan Øst.",1),
    ("Tofte Idrettslag","tofte-idrettslag","fleridrett","https://facebook.com/pages/Tofte%20Idrettslag/313269792927246/","Idrettslag i Tofte – flere aktiviteter.",1),
    ("Warya Idrettsklubb","warya-idrettsklubb","fotball","https://nb-no.facebook.com/Waryaik/","Fotball – Warya idrettsklubb.",1),
]

TMPL = """<!doctype html>
<html lang="nb">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{name} | Fritidsaktiviteter i Asker</title>
<style>
  :root {{ --blue: #1a5fb4; --light: #f4f6f9; }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: 'Segoe UI', system-ui, sans-serif; background: var(--light); color: #222; }}
  header {{ background: var(--blue); color: #fff; padding: 2rem 1rem 1.5rem; text-align: center; }}
  header h1 {{ font-size: 1.6rem; margin-bottom: .3rem; }}
  header p {{ opacity: .9; font-size: .95rem; }}
  .container {{ max-width: 800px; margin: 2rem auto; padding: 0 1rem; }}
  .card {{ background: #fff; border-radius: 10px; box-shadow: 0 1px 4px rgba(0,0,0,.08); padding: 1.5rem; }}
  .icon {{ margin-bottom: 1rem; }}
  .card h2 {{ font-size: 1.3rem; color: var(--blue); margin-bottom: .4rem; }}
  .activity-title {{ font-size: 1rem; font-weight: 700; color: #333; margin-bottom: 1rem; }}
  .contact {{ font-size: .95rem; line-height: 1.8; }}
  .contact a {{ color: var(--blue); text-decoration: none; }}
  .contact a:hover {{ text-decoration: underline; }}
  .desc {{ font-size: .9rem; color: #555; margin-top: 1rem; line-height: 1.6; }}
  .back {{ display: inline-block; margin-top: 1.5rem; color: var(--blue); text-decoration: none; font-weight: 600; }}
  .back:hover {{ text-decoration: underline; }}
  footer {{ text-align: center; padding: 1.5rem; color: #888; font-size: .8rem; }}
  .contact .url-link {{ display: inline-block; max-width: 100%; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; vertical-align: bottom; }}
</style>
</head>
<body>
<header>
  <h1>Fritidsaktiviteter i Asker</h1>
  <p>{name}</p>
</header>
<div class="container">
  <div class="card">
<h2>{name}</h2>
        <h4 class="activity-title">{activity}</h4>
        <div class="contact"><div><strong>{label}:</strong> <a class="url-link" href="{url}" target="_blank" rel="noopener">{url}</a></div></div>
        <p class="desc">{desc}</p>
  </div>
  <a class="back" href="index.html">&larr; Tilbake til alle aktiviteter</a>
</div>
<footer>Fritidsaktiviteter i Asker</footer>
</body>
</html>
"""

CARD = """    <div class="card clickable" data-name="{lowname}" data-activity="{activity}" data-address="asker" data-desc="{desc}">
      <a class="card-link" href="{slug}.html"><div class="card-body">
        <h3>{name}</h3>
        <div class="contact"><div><strong>{label}:</strong> <a class="url-link" href="{url}" target="_blank" rel="noopener">{url}</a></div></div>
        <p class="desc">{desc}</p>
      <a class="cta" href="{slug}.html">Mer info &rarr;</a>
      </div>
    </div>
"""

created = 0
for name, slug, activity, url, desc, is_fb in CLUBS:
    path = os.path.join(ROOT, slug + '.html')
    label = "Facebook" if is_fb else "Nettside"
    if os.path.exists(path):
        print("SKIP (exists):", slug)
        continue
    with open(path, 'w', encoding='utf-8') as f:
        f.write(TMPL.format(name=name, activity=activity, label=label, url=url, desc=desc))
    created += 1

print("Undersidor skapade:", created)

# Update index.html
with open(IDX, 'r', encoding='utf-8') as f:
    idx = f.read()

if any('advania-norge-bedriftsidrettslag.html' in idx for _ in [0]):
    print("index.html verkar redan innehålla nya kort – avbryter för att undvika dubbletter.")
    sys.exit(1)

cards = ""
for name, slug, activity, url, desc, is_fb in CLUBS:
    label = "Facebook" if is_fb else "Nettside"
    cards += CARD.format(lowname=name.lower(), name=name, activity=activity, label=label, url=url, desc=desc, slug=slug)

# Insert before closing </div> of grid
marker = '<footer>'
if marker in idx:
    idx = idx.replace(marker, cards + marker)
else:
    print("Hittar inte grid-slutet i index.html")
    sys.exit(1)

# Update count in title
m = re.search(r'Fritidsaktiviteter i Asker – (\d+) tilbud', idx)
if m:
    new = int(m.group(1)) + created
    idx = idx.replace(m.group(0), f'Fritidsaktiviteter i Asker – {new} tilbud')
    print("Räknare uppdaterad till:", new)

with open(IDX, 'w', encoding='utf-8') as f:
    f.write(idx)
print("index.html uppdaterad.")
