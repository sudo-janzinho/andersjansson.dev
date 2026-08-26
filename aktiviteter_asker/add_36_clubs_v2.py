#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Lagger till 35 nya klubber i askeridrett.no med strikt UTF-8-verifiering."""
import sys, re, os, unicodedata

ROOT = r"C:\Users\janss\.openclaw\workspace\andersjansson-dev\aktiviteter_asker"
IDX = os.path.join(ROOT, 'index.html')

# ---------- STEG 1: ENCODING-SELFTEST ----------
TESTFILE = os.path.join(ROOT, '_encoding_test.html')
TESTSTR = "åäö ÅÄO ⛸️ ⚽ 🏀 🇳🇴 ø Ø æ Æ"
with open(TESTFILE, 'w', encoding='utf-8') as f:
    f.write(TESTSTR)
with open(TESTFILE, 'r', encoding='utf-8') as f:
    readback = f.read()
os.remove(TESTFILE)
if readback != TESTSTR:
    print("FEL: UTF-8 roundtrip misslyckades!")
    sys.exit(1)
print("[OK] UTF-8 encoding verifierad (åäö/ÅÄO/emoji/flags)")

# ---------- STEG 2: LÄS INDEX ----------
with open(IDX, 'rb') as f:
    raw = f.read()
try:
    idx = raw.decode('utf-8')
except UnicodeDecodeError as e:
    print("FEL: index.html är inte giltig UTF-8:", e)
    sys.exit(1)
if 'åäö' not in unicodedata.normalize('NFC', idx) and 'ø' not in idx:
    print("INFO: index.html innehåller eventuellt inte vanliga norska bokstäver – fortsätter ändå")

# ---------- STEG 3: DATA ----------
# (name, slug, activity, url, desc, label)
C = [
    ("Advania Norge Bedriftsidrettslag","advania-norge-bedriftsidrettslag","bedriftsidrett","http://www.advania.no/","Bedriftsidrett – aktivitetstilbud for ansatte.","Nettside"),
    ("Ak Fryktløs","ak-fryktlos","fallsjermhopping","http://www.fryktlos.no","Fallskjermhopping – adrenalin og mestring i luften.","Nettside"),
    ("Askerbøringene IL","askerboringene-il","fleridrett","http://www.askerboringene.no","Fleridrettslag – varierte aktiviteter for alle.","Nettside"),
    ("Asker Cykleklubb","asker-cykleklubb-2","sykling","http://asker-ck.no/","Sykling – landevei og terrengsykling.","Nettside"),
    ("Asker Helsesportlag","asker-helsesportlag","helsesport","http://www.askerhelsesportlag.no","Helsesport – aktivitet og folkehelse.","Nettside"),
    ("Asker Kunstløp Klubb Akk","asker-kunstlop-klubb-akk-2","kunstløp","http://www.akk.no","Kunstløp – eleganse, balanse og teknikk på is.","Nettside"),
    ("Asker Miniracing Club","asker-miniracing-club","motorsport","http://www.amrc.no","Miniracing – motorsport for barn og unge.","Nettside"),
    ("Asker Modellklubb","asker-modellklubb","modellflyging","http://askermodellklubb.no","Modellflyging – bygg og fly radiostyrte modeller.","Nettside"),
    ("Asker Skyteklubb","asker-skyteklubb-2","skyting","http://www.askerskyteklubb.no","Skyting – presisjon og konsentrasjon.","Nettside"),
    ("Asker Trekkhundklubb","asker-trekkhundklubb","trekkhund","http://asker-trekkhundklubb.webnode.com/","Trekkhund – hundesport og samarbeid.","Nettside"),
    ("Fekteklubben Frie Duellister","fekteklubben-frie-duellister","fekting","http://www.frieduellister.no","Fekting – elegant kampsport med hurtighet.","Nettside"),
    ("Hard Intensiv Trening (HIT)","hard-intensiv-trening-hit","trening","http://www.hitrening.no","HIT – høyintensiv trening og styrke.","Nettside"),
    ("Holmenparken Idrettslag","holmenparken-idrettslag-2","fleridrett","http://www.holmenparken.no","Idrettslag – lokale aktiviteter i Holmenparken.","Nettside"),
    ("Hurum Croquet Klubb","hurum-croquet-klubb","croquet","http://hurumcroquet.no","Croquet – presisjonsport i hagen.","Nettside"),
    ("Norsk If-Båt Klubb","norsk-if-bat-klubb","båt","http://www.ifklubben.no","IF-båt – seiling og båtliv.","Nettside"),
    ("Red Crown BK","red-crown-bk","bowling","http://klubber.bowling.no/red_crown_bk/","Bowling – spennende lagspill med ball.","Nettside"),
    ("Røyken Cykleklubb","royken-cykleklubb","sykling","http://Cykleklubb.no","Sykling i Røyken – landevei og terreng.","Nettside"),
    ("Røyken Og Hurum Modellflyklubb","royken-og-hurum-modellflyklubb","modellflyging","http://www.rhmfk.org","Modellflyging – radiostyrte fly i Røyken/Hurum.","Nettside"),
    ("Røyken Orienteringslag","royken-orienteringslag","orientering","http://www.roykenolag.no","Orientering – kart, kompass och terreng.","Nettside"),
    ("Røyken Sportsdykkerklubb","royken-sportsdykkerklubb","dykking","http://www.rsdk.no","Sportsdykking – undervannseventyr.","Nettside"),
    ("Sunyata Aikido Dojo","sunyata-aikido-dojo","aikido","http://www.sunyata.no","Aikido – japansk kampsport med flyt.","Nettside"),
    ("Veteranenes Fallskjermklubb","veteranenes-fallskjermklubb","fallsjermhopping","http://www.fallskjermveteranene.com","Fallskaermhopping for veteraner.","Nettside"),
    ("Vingtor RC Club","vingtor-rc-club","modellflyging","http://www.vingtor.org/","RC-modeller – fly, bil og båt.","Nettside"),
    ("Asker Fleridrettslag","asker-fleridrettslag","fleridrett","https://facebook.com/askerfleridrettslag/","Fleridrett – varierte aktiviteter for alle.","Facebook"),
    ("Frisk Superlag","frisk-superlag","fleridrett","https://facebook.com/Friskasker/","Superlag – aktivitet for alle.","Facebook"),
    ("Hagahogget Lømlag","hagahogget-lomlag","fleridrett","https://facebook.com/hagahogget/","Lømlag – fotball og aktivitet.","Facebook"),
    ("NMK Asker","nmk-asker","motorsport","https://www.facebook.com/people/NMK-Asker/100038813173792/","Motorsport – racing og bilcross i Asker.","Facebook"),
    ("Nordlys Cricketklubb Asker","nordlys-cricketklubb-asker","cricket","https://facebook.com/p/Nordlys-Cricketklubb-Asker-61559490254915/","Cricket – lagspill som vokser i Norge.","Facebook"),
    ("Oslofjordens Friluftsråd","oslofjordens-friluftsrad","friluftsliv","https://facebook.com/oslofjf/","Friluftsliv – turer og natur rundt Oslofjorden.","Facebook"),
    ("Slemmestad Brettklubb","slemmestad-brettklubb","brettsport","https://facebook.com/groups/500551278484246/","Brettsport – surf og SUP i Slemmestad.","Facebook"),
    ("Slemmestad Kajakklubb","slemmestad-kajakklubb","kajakk","https://facebook.com/slemmestadkk/","Kajakk – padling på Oslofjorden.","Facebook"),
    ("Spuvi","spuvi","fleridrett","https://facebook.com/p/Spuvi-100057414521143/","Spuvi – aktiviteter og sport.","Facebook"),
    ("Team Cyan Øst","team-cyan-ost","sykling","https://facebook.com/teamcyansykkel/","Sykkel og triatlon – Team Cyan Øst.","Facebook"),
    ("Tofte Idrettslag","tofte-idrettslag","fleridrett","https://facebook.com/pages/Tofte%20Idrettslag/313269792927246/","Idrettslag i Tofte – flere aktiviteter.","Facebook"),
    ("Warya Idrettsklubb","warya-idrettsklubb","fotball","https://nb-no.facebook.com/Waryaik/","Fotball – Warya idrettsklubb.","Facebook"),
]
print("[OK] Antal klubber:", len(C))

# ---------- STEG 4: SKRIV UNDERSIDOR ----------
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

created = []
for name, slug, activity, url, desc, label in C:
    path = os.path.join(ROOT, slug + '.html')
    # Verifiera att alla tecken är skrivbara som UTF-8
    content = TMPL.format(name=name, activity=activity, label=label, url=url, desc=desc)
    content.encode('utf-8')  # kastar fel om ogiltig
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(content)
    # Roundtrip-koll
    with open(path, 'r', encoding='utf-8') as f:
        if f.read() != content:
            print("FEL: roundtrip misslyckades för", slug); sys.exit(1)
    created.append(slug)
print("[OK] Skapade", len(created), "undersidor med verifierad UTF-8")

# ---------- STEG 5: UPPDATERA INDEX ----------
CARD = """    <div class="card clickable" data-name="{lowname}" data-activity="{activity}" data-address="asker" data-desc="{desc}">
      <a class="card-link" href="{slug}.html"><div class="card-body">
        <h3>{name}</h3>
        <div class="contact"><div><strong>{label}:</strong> <a class="url-link" href="{url}" target="_blank" rel="noopener">{url}</a></div></div>
        <p class="desc">{desc}</p>
      <a class="cta" href="{slug}.html">Mer info &rarr;</a>
      </div>
    </div>
"""

cards = ""
for name, slug, activity, url, desc, label in C:
    cards += CARD.format(lowname=name.lower(), name=name, activity=activity, label=label, url=url, desc=desc, slug=slug)

# Dublettskydd
first_slug = C[0][1] + '.html'
if first_slug in idx:
    print("FEL: korten finns redan i index.html – avbryter för att undvika dubbletter"); sys.exit(1)

marker = '\n    <footer>'
if marker not in idx:
    print("FEL: hittar inte grid-slutet före <footer> i index.html"); sys.exit(1)

idx = idx.replace(marker, cards + marker)

# Uppdatera titelräknaren
m = re.search(r'Fritidsaktiviteter i Asker – (\d+) tilbud', idx)
if m:
    new = int(m.group(1)) + len(C)
    idx = idx.replace(m.group(0), f'Fritidsaktiviteter i Asker – {new} tilbud')
    print("[OK] Räknare:", m.group(1), "->", new)

# Skriv index.html som UTF-8, bevara befintligt newline-stil (CRLF)
idx.encode('utf-8')
with open(IDX, 'w', encoding='utf-8', newline='') as f:
    f.write(idx)

# Roundtrip-koll av index.html
with open(IDX, 'r', encoding='utf-8') as f:
    if f.read() != idx:
        print("FEL: index.html roundtrip misslyckades"); sys.exit(1)

# Kontrollera att norska tecken överlevt
with open(IDX, 'r', encoding='utf-8') as f:
    content = f.read()
    if 'ø' not in content and 'å' not in content and 'æ' not in content:
        print("FEL: norska tecken försvann i index.html"); sys.exit(1)

print("[OK] index.html uppdaterad och verifierad")

# ---------- STEG 6: SLUTVERIFIERING ----------
ok = True
for slug in created:
    p = os.path.join(ROOT, slug + '.html')
    with open(p, 'rb') as f:
        try: f.read().decode('utf-8')
        except UnicodeDecodeError: print("FEL: ogiltig UTF-8 i", slug); ok = False
with open(IDX, 'rb') as f:
    try: f.read().decode('utf-8')
    except UnicodeDecodeError: print("FEL: ogiltig UTF-8 i index.html"); ok = False
if not ok: sys.exit(1)
print("[OK] Alla filer är giltig UTF-8. KLART – redo att commita.")
