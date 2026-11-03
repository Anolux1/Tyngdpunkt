"""Bygger webbplatsen: varje sida = sidhuvud + innehåll + sidfot. Kör: python3 _kalla/bygg.py (från webb/).

Sidorna ligger i egna mappar (kaloribehov/index.html) så att adresserna blir korta: /kaloribehov/.
Alla länkar är relativa, så att samma filer fungerar både på GitHub Pages (under /Tyngdpunkt/) och på en egen domän.
Webbplatsen ska kunna bära fler appar: allmänt innehåll (kalkylatorer, artiklar) ligger överst, varje app i en egen mapp.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GROUP = 'https://groups.google.com/g/tyngdpunkt_app'
NAV = [('kaloribehov/', 'Kaloribehov'), ('proteinbehov/', 'Protein'), ('1rm/', '1RM'), ('artiklar/', 'Artiklar'), ('tyngdpunkt/', 'Appen')]


def page(path, title, desc, body, script='', on=None):
    depth = path.count('/')
    r = '../' * depth
    on_attr = ' class="on"'
    nav = ''.join(f'<a href="{r}{href}"{on_attr if href == on else ""}>{label}</a>' for href, label in NAV)
    html = f'''<!doctype html>
<html lang="sv"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="icon" href="{r}assets/logo.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{r}assets/style.css">
</head><body>
<header><div class="in"><a class="brand" href="{r}index.html"><img src="{r}assets/logo.svg" alt="">Tyngdpunkt</a><nav>{nav}</nav></div></header>
<main>
{body.replace('{r}', r)}
</main>
<footer><nav><a href="{r}kaloribehov/">Kaloribehov</a><a href="{r}proteinbehov/">Protein</a><a href="{r}1rm/">1RM</a><a href="{r}artiklar/">Artiklar</a><a href="{r}tyngdpunkt/hjalp.html">Hjälp och kontakt</a><a href="{r}tyngdpunkt/integritet.html">Integritetspolicy</a></nav>
Kalkylatorerna ger uppskattningar, inte medicinska råd. Livsmedelsdata: Livsmedelsverkets livsmedelsdatabas.</footer>
{f"<script src='{r}assets/kalkyl.js'></script><script>{script}</script>" if script else ''}
</body></html>
'''
    out = ROOT / path
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html)


def redirect(path, to):
    (ROOT / path).write_text(f'<!doctype html><html lang="sv"><head><meta charset="utf-8"><meta http-equiv="refresh" content="0; url={to}">'
                             f'<link rel="canonical" href="{to}"><title>Flyttad</title></head><body><a href="{to}">Sidan har flyttat hit.</a></body></html>\n')


# Appen finns i stängt test: knappen leder till testgruppen tills den är publicerad på Google Play.
def cta(text):
    return (f'<div class="cta"><p>{text}</p><div><a class="btn" href="{GROUP}">Testa appen</a>'
            '<div class="soon">Kommer snart på Google Play (Android)</div></div></div>')


# ---------- Startsidan ----------
page('index.html', 'Kalkylatorer för träning och kost – Tyngdpunkt',
     'Räkna ut kaloribehov, proteinbehov och 1RM på svenska, med uträkningen synlig. Från Tyngdpunkt.', '''
<div class="bar"></div>
<h1>Räkna på träning och kost</h1>
<p class="lead">Kalkylatorer på svenska som visar hur de räknar. Samma formler som i träningsappen Tyngdpunkt.</p>
<div class="tiles">
 <a class="tile" href="{r}kaloribehov/"><b>Kaloribehov</b><span>Hur mycket du ska äta för att gå ner, bygga muskler eller ligga kvar.</span></a>
 <a class="tile" href="{r}proteinbehov/"><b>Proteinbehov</b><span>Gram protein per dag när du styrketränar, och vad det motsvarar i mat.</span></a>
 <a class="tile" href="{r}1rm/"><b>1RM</b><span>Ditt uppskattade max ur ett vanligt set, utan att testa.</span></a>
</div>
<h2>Artiklar</h2>
<p class="faq" style="color:var(--sub)">Svar på det man undrar när man tränar och vill äta rätt. <a href="{r}artiklar/">Till artiklarna</a></p>
<h2>Appen</h2>
''' + cta('<strong>Tyngdpunkt</strong> är träningslogg och matlogg i samma app. Varje vecka går den igenom vikten, styrkan och hur väl du följt planen, och föreslår en sak att ändra.'))

# ---------- Kaloribehov ----------
page('kaloribehov/index.html', 'Räkna ut ditt kaloribehov – kalkylator | Tyngdpunkt',
     'Kalkylator för kaloribehov: hur mycket du gör av med per dag och hur mycket du ska äta för att gå ner i vikt eller bygga muskler. Uträkningen visas steg för steg.', '''
<h1>Räkna ut ditt kaloribehov</h1>
<p class="lead">Hur mycket du gör av med på en dag, och hur mycket du ska äta för att gå ner i fett, bygga muskler eller ligga kvar.</p>
<div class="card"><div class="grid">
 <div><label>Kön</label><div class="seg" id="sex"><button class="on" data-v="man">Man</button><button data-v="kvinna">Kvinna</button></div></div>
 <div><label for="age">Ålder</label><input id="age" type="number" inputmode="numeric" value="35"></div>
 <div><label for="h">Längd (cm)</label><input id="h" type="number" inputmode="numeric" value="180"></div>
 <div><label for="w">Vikt (kg)</label><input id="w" type="number" inputmode="decimal" value="85"></div>
 <div><label for="days">Träningspass per vecka</label><select id="days"><option>0</option><option>1</option><option>2</option><option selected>3</option><option>4</option><option>5</option><option>6</option></select></div>
 <div><label for="goal">Mål</label><select id="goal"><option value="fett">Gå ner i fett</option><option value="muskler">Bygga muskler</option><option value="underhalla">Ligga kvar</option></select></div>
 <div id="paceBox"><label for="pace">Takt (kg per vecka)</label><select id="pace"></select></div>
</div></div>
<div class="card"><div class="res">
 <div><div class="k">Ät per dag</div><span class="big" id="kTarget">–</span> <span class="unit">kcal</span></div>
 <div><div class="k">Du gör av med</div><span class="big mid" id="kTdee">–</span> <span class="unit">kcal</span></div>
</div><div class="calc" id="kCalc"></div></div>
''' + cta('<strong>Det här är en startgissning.</strong> Tyngdpunkt räknar om den varje vecka utifrån hur din vikt faktiskt rör sig, och ser samtidigt om du blir starkare.') + '''
<h2>Så räknar vi</h2>
<div class="faq">
 <p>Vilan räknas med Mifflin–St Jeor, den vanligaste formeln: 10 × vikt + 6,25 × längd − 5 × ålder, plus 5 för män och minus 161 för kvinnor. Den multipliceras med en faktor för hur ofta du tränar, från 1,4 vid två pass i veckan eller färre till 1,55 vid fem eller fler.</p>
 <p>Ett kilo kroppsfett motsvarar ungefär 7 700 kcal. En takt på 0,5 kg i veckan betyder därför 550 kcal mindre per dag (0,5 × 7 700 ÷ 7). Resultatet avrundas till närmaste 50 kcal.</p>
 <p><strong>Varför stämmer det inte för mig?</strong> Formeln är ett snitt för många människor. Väg dig några gånger i veckan i tre veckor och ät ungefär samma mängd. Går vikten ner, upp eller står den still vet du ditt verkliga behov.</p>
 <p><strong>Hur snabbt ska jag gå ner?</strong> 0,25–0,5 kg i veckan brukar vara lagom för den som styrketränar och vill behålla musklerna. Snabbare går, men styrkan sjunker oftare.</p>
 <p>Mer: <a href="{r}proteinbehov/">hur mycket protein du behöver</a> · <a href="{r}1rm/">räkna ut ditt 1RM</a></p>
</div>
''', script='kcalPage()', on='kaloribehov/')

# ---------- Protein ----------
page('proteinbehov/index.html', 'Hur mycket protein behöver jag? Kalkylator | Tyngdpunkt',
     'Räkna ut ditt proteinbehov per dag när du styrketränar, och se hur mycket protein det är i vanlig svensk mat enligt Livsmedelsverket.', '''
<h1>Hur mycket protein behöver jag?</h1>
<p class="lead">Proteinbehovet per dag när du styrketränar, beroende på om du vill gå ner i fett, bygga muskler eller ligga kvar.</p>
<div class="card"><div class="grid">
 <div><label for="pw">Vikt (kg)</label><input id="pw" type="number" inputmode="decimal" value="85"></div>
 <div><label for="pg">Mål</label><select id="pg"><option value="fett">Gå ner i fett</option><option value="muskler" selected>Bygga muskler</option><option value="underhalla">Ligga kvar</option></select></div>
 <div id="pgwBox"><label for="pgw">Målvikt (kg, valfritt)</label><input id="pgw" type="number" inputmode="decimal" placeholder="t.ex. 78"></div>
 <div><label for="pm">Måltider per dag</label><select id="pm"><option>3</option><option selected>4</option><option>5</option></select></div>
</div></div>
<div class="card"><div class="res">
 <div><div class="k">Protein per dag</div><span class="big" id="pT">–</span> <span class="unit">g</span></div>
 <div><div class="k">Per måltid</div><span class="big mid" id="pM">–</span> <span class="unit">g</span></div>
</div><div class="calc" id="pCalc"></div></div>
<div class="card"><div class="k" style="margin-bottom:6px">Så mycket protein är det i vanlig svensk mat</div><table id="pFood"></table>
<p class="small" style="margin:8px 0 0">Källa: Livsmedelsverkets livsmedelsdatabas.</p></div>
''' + cta('<strong>Svårt att komma upp i det?</strong> Tyngdpunkt visar hur mycket protein du har kvar i dag och föreslår varor du redan brukar äta.') + '''
<h2>Så räknar vi</h2>
<div class="faq">
 <p>För den som styrketränar räknar vi med 2,2 g per kilo kroppsvikt när du går ner i fett, 2,0 g när du bygger muskler och 1,8 g när du ligger kvar. Mer protein under en deff hjälper till att behålla musklerna när du äter mindre.</p>
 <p><strong>Varför målvikten?</strong> Under en deff med målvikt räknas proteinet på målvikten. Det räcker för att behålla musklerna och är lättare att nå för den som väger mycket: 98 kg × 2,2 g är 215 g, men 88 kg ger 195 g.</p>
 <p><strong>Måste jag dela upp det?</strong> Totalen per dag är det viktigaste. Att sprida proteinet över dagens måltider gör det lättare att komma upp i det.</p>
 <p>Mer: <a href="{r}kaloribehov/">räkna ut ditt kaloribehov</a> · <a href="{r}1rm/">räkna ut ditt 1RM</a></p>
</div>
''', script='protPage()', on='proteinbehov/')

# ---------- 1RM ----------
page('1rm/index.html', '1RM-kalkylator – räkna ut ditt max | Tyngdpunkt',
     'Uppskatta ditt 1RM (one rep max) ur ett vanligt set med Epleys formel, och se vad du borde klara på 3, 5, 8 och 10 reps.', '''
<h1>Räkna ut ditt 1RM</h1>
<p class="lead">Uppskatta hur mycket du orkar lyfta en gång, utan att testa max. Skriv in ett set du har gjort.</p>
<div class="card"><div class="grid">
 <div><label for="rw">Vikt på stången (kg)</label><input id="rw" type="number" inputmode="decimal" value="100"></div>
 <div><label for="rr">Antal reps</label><input id="rr" type="number" inputmode="numeric" value="5"></div>
</div></div>
<div class="card"><div class="res"><div><div class="k">Uppskattat max (1RM)</div><span class="big" id="rmT">–</span> <span class="unit">kg</span></div></div>
<div class="calc" id="rmCalc"></div></div>
<div class="card"><div class="k" style="margin-bottom:6px">Vad du borde klara på fler reps</div><table id="rmTab"></table></div>
''' + cta('<strong>Slipp räkna själv.</strong> Tyngdpunkt följer ditt uppskattade max i varje övning och ökar vikt och reps när det är dags.') + '''
<h2>Så räknar vi</h2>
<div class="faq">
 <p>Vi använder Epleys formel: vikt × (1 + reps ÷ 30). 100 kg × 5 reps ger ungefär 116,5 kg. Tabellen räknar baklänges från ditt max till hur mycket du borde klara på fler reps.</p>
 <p><strong>Hur säkert är det?</strong> Uppskattningen är säkrast mellan 3 och 10 reps. Med fler reps spelar uthållighet större roll, och formeln blir mer osäker. Ta ett set som var tungt men med bra teknik.</p>
 <p><strong>Varför inte bara testa?</strong> Ett maxtest kräver uppvärmning, en spotter och en dag då du är pigg. Ett uppskattat max ur vanliga set går att följa vecka för vecka och visar om du blir starkare.</p>
 <p>Mer: <a href="{r}kaloribehov/">räkna ut ditt kaloribehov</a> · <a href="{r}proteinbehov/">hur mycket protein du behöver</a></p>
</div>
''', script='rmPage()', on='1rm/')

# ---------- Artiklar ----------
page('artiklar/index.html', 'Artiklar om träning och kost | Tyngdpunkt',
     'Artiklar om styrketräning, kost, kaloribehov och protein – på svenska, med siffror och uträkningar.', '''
<h1>Artiklar</h1>
<p class="lead">Svar på det man undrar när man styrketränar och vill äta rätt – med siffror och uträkningar, inte löften.</p>
<div class="card"><p style="margin:0">De första artiklarna kommer snart. Under tiden kan du räkna på ditt
<a href="{r}kaloribehov/">kaloribehov</a>, ditt <a href="{r}proteinbehov/">proteinbehov</a> eller ditt <a href="{r}1rm/">1RM</a>.</p></div>
''', on='artiklar/')

# ---------- Appen ----------
page('tyngdpunkt/index.html', 'Tyngdpunkt – träningslogg och matlogg i samma app',
     'Tyngdpunkt är träningslogg och matlogg i samma app, på svenska. Varje vecka går appen igenom vikten, styrkan och hur väl du följt planen.', '''
<div class="bar"></div>
<h1>Tyngdpunkt</h1>
<p class="lead">Träningslogg och matlogg i samma app, på svenska.</p>
<div class="card">
<p style="margin-top:0">Du loggar passen och maten och väger dig. En gång i veckan går appen igenom vikten, styrkan i varje övning och hur väl du följde planen, och föreslår en sak att ändra. Uträkningen syns, och inget ändras förrän du har godkänt det.</p>
<p>Programmen ökar vikt och reps efter hur passen gick. Maten hittar du i Livsmedelsverkets databas och bland cirka 19 000 svenska märkesvaror, eller genom att skanna streckkoden.</p>
<p style="margin-bottom:0">All data stannar i telefonen. 30 dagar gratis med allt, utan kort. Därefter 99 kr i månaden eller 699 kr om året.</p>
</div>
''' + cta('<strong>Appen är i test.</strong> Har du en Android-telefon kan du testa den redan nu genom att gå med i testgruppen.') + '''
<p><a href="hjalp.html">Hjälp och kontakt</a> · <a href="integritet.html">Integritetspolicy</a></p>
''', on='tyngdpunkt/')

# Integritetspolicy och hjälp: innehållet hämtas från _kalla/, så att texten bara finns på ett ställe.
for name, title, desc in [('integritet', 'Integritetspolicy – Tyngdpunkt', 'Integritetspolicy för appen Tyngdpunkt: all data stannar i telefonen.'),
                          ('hjalp', 'Hjälp och kontakt – Tyngdpunkt', 'Hjälp och kontakt för appen Tyngdpunkt.')]:
    page(f'tyngdpunkt/{name}.html', title, desc, '<div class="doc">' + (ROOT / '_kalla' / f'{name}.html').read_text() + '</div>', on='tyngdpunkt/')

# Gamla adresser: integritetspolicyn är angiven i Play Console som /integritet.html.
redirect('integritet.html', 'tyngdpunkt/integritet.html')
redirect('support.html', 'tyngdpunkt/hjalp.html')
print('Byggt.')
