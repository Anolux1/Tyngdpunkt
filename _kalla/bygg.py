"""Bygger webbplatsen: varje sida = sidhuvud + innehåll + sidfot. Kör: python3 _kalla/bygg.py (från webb/).

Sidorna ligger i egna mappar (kaloribehov/index.html) så att adresserna blir korta: /kaloribehov/.
Alla länkar är relativa, så att samma filer fungerar både på GitHub Pages (under /Tyngdpunkt/) och på en egen domän.
Webbplatsen ska kunna bära fler appar: allmänt innehåll (kalkylatorer, artiklar) ligger överst, varje app i en egen mapp.
"""
import datetime
import html as H
import json
import re
from pathlib import Path

import markdown
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
# Appens läge styr knappen på alla sidor (seo-strategi.md, avsnitt 10). Byt till 'publicerad' när appen finns på
# Google Play – och kontrollera med Andreas att provperioden finns i den publicerade versionen (raden "30 dagar gratis").
APP_STATUS = 'test'
GROUP = 'https://groups.google.com/g/tyngdpunkt_app'
OPT_IN = 'https://play.google.com/apps/testing/se.tyngdpunkt.app'
PLAY = 'https://play.google.com/store/apps/details?id=se.tyngdpunkt.app'
DOMAIN = 'https://tyngdpunkt.se'
TODAY = datetime.date.today().isoformat()
SITEMAP = []  # (adress, ändringsdatum) för sitemap.xml
NAV = [('kaloribehov/', 'Kaloribehov'), ('proteinbehov/', 'Protein'), ('1rm/', '1RM'), ('artiklar/', 'Artiklar'), ('tyngdpunkt/', 'Appen')]


def clean_url(path):
    # Adressen som Cloudflare visar: utan index.html och utan .html.
    u = path.removesuffix('index.html').removesuffix('.html')
    return f'{DOMAIN}/{u}'


def page(path, title, desc, body, script='', on=None, kind='website', jsonld=None, lastmod=None, head=''):
    depth = path.count('/')
    r = '../' * depth
    url = clean_url(path)
    SITEMAP.append((url, lastmod or TODAY))
    ld = ''.join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in (jsonld or []))
    on_attr = ' class="on"'
    nav = ''.join(f'<a href="{r}{href}"{on_attr if href == on else ""}>{label}</a>' for href, label in NAV)
    html = f'''<!doctype html>
<html lang="sv"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
<meta name="description" content="{H.escape(desc)}">
<link rel="canonical" href="{url}">
<meta property="og:type" content="{kind}"><meta property="og:title" content="{H.escape(title)}"><meta property="og:description" content="{H.escape(desc)}">
<meta property="og:url" content="{url}"><meta property="og:locale" content="sv_SE"><meta property="og:site_name" content="Tyngdpunkt">
{head}{ld}
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
    if APP_STATUS == 'publicerad':
        btn, href, under = 'Ladda ner på Google Play', PLAY, '30 dagar gratis. Android, iPhone-versionen finns inte än.'
    else:
        btn, href, under = 'Bli testare', '{r}tyngdpunkt/testa/', 'Android. iPhone-versionen finns inte än.'
    return f'<div class="cta"><p>{text}</p><div><a class="btn" href="{href}">{btn}</a><div class="soon">{under}</div></div></div>'


# ---------- Artiklar ----------
# En Markdown-fil per artikel i _kalla/artiklar/<slug>.md (skrivs av marknadssessionen, godkänns av Andreas).
# Byggs bara om status är "godkand" och publiceringsdatumet har passerat; saknat status = utkast.
CALC = {'proteinbehov': ('proteinbehov/', 'Räkna ut ditt proteinbehov'), 'kaloribehov': ('kaloribehov/', 'Räkna ut ditt kaloribehov'),
        '1rm': ('1rm/', 'Räkna ut ditt 1RM')}


def front_matter(text):
    m = re.match(r'^---\n(.*?)\n---\n(.*)$', text, re.S)
    if not m:
        return {}, text
    meta = {}
    for line in m.group(1).splitlines():
        if ':' in line:
            k, v = line.split(':', 1)
            meta[k.strip()] = v.strip().strip('"')
    return meta, m.group(2)


def faq(md_body):
    # "## Vanliga frågor" med "### Fråga" och svaret under – blir FAQ-schema.
    m = re.search(r'^## Vanliga frågor\s*\n(.*?)(?=^## |\Z)', md_body, re.S | re.M)
    if not m:
        return []
    out = []
    for q, a in re.findall(r'^### (.+?)\n(.*?)(?=^### |\Z)', m.group(1), re.S | re.M):
        text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', a).strip()
        text = re.sub(r'[*_`]', '', text)
        if text:
            out.append({'@type': 'Question', 'name': q.strip(), 'acceptedAnswer': {'@type': 'Answer', 'text': text}})
    return out


ARTICLES = []
for f in sorted((ROOT / '_kalla' / 'artiklar').glob('*.md')) if (ROOT / '_kalla' / 'artiklar').exists() else []:
    meta, body = front_matter(f.read_text())
    if meta.get('status') != 'godkand' or meta.get('publicera', '9999') > TODAY:
        continue
    # Saknas en bild hoppas artikeln över helt (även i listorna) i stället för att publiceras trasig.
    refs = re.findall(r'!\[[^\]]*\]\((bilder/[^)\s]+)\)', body) + ([meta['bild']] if meta.get('bild') else [])
    missing = [x for x in refs if not (ROOT / '_kalla' / 'artiklar' / x).exists()]
    if missing:
        print(f'HOPPAR ÖVER {f.stem}: bild saknas: {", ".join(missing)}')
        continue
    ARTICLES.append({**meta, 'slug': f.stem, 'body': body})
ARTICLES.sort(key=lambda a: a['publicera'], reverse=True)

MONTHS = ['januari', 'februari', 'mars', 'april', 'maj', 'juni', 'juli', 'augusti', 'september', 'oktober', 'november', 'december']
sv_date = lambda d: f'{int(d[8:10])} {MONTHS[int(d[5:7]) - 1]} {d[:4]}'


def article_list(items, r='{r}'):
    return ''.join(f'<a class="tile" style="margin-bottom:10px" href="{r}artiklar/{a["slug"]}/"><b>{H.escape(a["titel"])}</b>'
                   f'<span>{H.escape(a.get("beskrivning", ""))}</span></a>' for a in items)


# "Läs mer" under en kalkylator: de senaste artiklarna som hör till den (fältet kalkylator), högst fem.
def related(calc):
    items = [a for a in ARTICLES if a.get('kalkylator') == calc][:5]
    return f'<h2>Läs mer</h2>{article_list(items)}' if items else ''


# ---------- Startsidan ----------
page('index.html', 'Kalkylatorer för träning och kost | Tyngdpunkt',
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
<p class="faq" style="color:var(--sub)">Svar på vanliga frågor om styrketräning och kost, med siffror och källor. <a href="{r}artiklar/">Alla artiklar</a></p>
''' + article_list(ARTICLES[:3]) + '''
<h2>Appen</h2>
''' + cta('<strong>Tyngdpunkt</strong> är träningslogg och matlogg i samma app. En gång i veckan går den igenom vikten, styrkan och hur väl du följt planen, och föreslår en sak att ändra.'))

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
''' + cta('<strong>Det här är en startgissning.</strong> Tyngdpunkt stämmer av den en gång i veckan mot hur din vikt faktiskt rör sig, och föreslår en ändring först när du följt planen och vikten ändå går fel.') + '''
<h2>Så räknar vi</h2>
<div class="faq">
 <p>Vilan räknas med Mifflin–St Jeor, en av de mest använda formlerna: 10 × vikt + 6,25 × längd − 5 × ålder, plus 5 för män och minus 161 för kvinnor. Den multipliceras med en faktor för hur ofta du tränar, från 1,2 om du inte tränar till 1,55 vid fem pass eller fler.</p>
 <p>Ett kilo kroppsfett motsvarar ungefär 7 700 kcal. En takt på 0,5 kg i veckan betyder därför 550 kcal mindre per dag (0,5 × 7 700 ÷ 7). Resultatet avrundas till närmaste 50 kcal.</p>
 <p><strong>Varför stämmer det inte för mig?</strong> Formeln är ett snitt för många människor. Väg dig några gånger i veckan i tre veckor och ät ungefär samma mängd. Går vikten ner, upp eller står den still vet du ditt verkliga behov.</p>
 <p><strong>Hur snabbt ska jag gå ner?</strong> För den som styrketränar och vill behålla musklerna brukar 0,5–1 % av kroppsvikten i veckan rekommenderas. För den som väger 85 kg är det ungefär 0,4–0,85 kg. En lugnare takt gör det lättare att behålla styrkan.</p>
 <p>Mer: <a href="{r}proteinbehov/">hur mycket protein du behöver</a> · <a href="{r}1rm/">räkna ut ditt 1RM</a></p>
 <p class="small">Källa för takten: <a href="https://pmc.ncbi.nlm.nih.gov/articles/PMC4033492/">Helms m.fl. (2014), Journal of the International Society of Sports Nutrition</a>.</p>
</div>
''' + related('kaloribehov'), script='kcalPage()', on='kaloribehov/')

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
''' + cta('<strong>Svårt att komma upp i det?</strong> Tyngdpunkt visar hur mycket protein du har kvar i dag och föreslår proteinrika varor bland det du brukar äta.') + '''
<h2>Så räknar vi</h2>
<div class="faq">
 <p>För den som styrketränar räknar vi med 2,2 g per kilo kroppsvikt när du går ner i fett, 2,0 g när du bygger muskler och 1,8 g när du ligger kvar. I den största sammanställningen planade effekten på muskelmassan ut vid ungefär 1,6 g per kilo, med ett osäkerhetsspann upp till 2,2 g. Vi räknar i den övre delen för att vara säkra. Under en deff talar mer för att ligga högt, eftersom det hjälper till att behålla musklerna när du äter mindre.</p>
 <p><strong>Varför målvikten?</strong> Under en deff med målvikt räknas proteinet på målvikten. Det räcker för att behålla musklerna och är lättare att nå för den som väger mycket: 98 kg × 2,2 g är 215 g, men 88 kg ger 195 g.</p>
 <p><strong>Måste jag dela upp det?</strong> Totalen per dag är det viktigaste. Att sprida proteinet över dagens måltider gör det lättare att komma upp i det.</p>
 <p>Mer: <a href="{r}kaloribehov/">räkna ut ditt kaloribehov</a> · <a href="{r}1rm/">räkna ut ditt 1RM</a></p>
 <p class="small">Källa: <a href="https://pmc.ncbi.nlm.nih.gov/articles/PMC5867436/">Morton m.fl. (2018), British Journal of Sports Medicine</a>.</p>
</div>
''' + related('proteinbehov'), script='protPage()', on='proteinbehov/')

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
 <p class="small">Formeln: Epley (1985).</p>
 <p>Mer: <a href="{r}kaloribehov/">räkna ut ditt kaloribehov</a> · <a href="{r}proteinbehov/">hur mycket protein du behöver</a></p>
</div>
''' + related('1rm'), script='rmPage()', on='1rm/')

# ---------- Artikelsidorna ----------
# Bilder: Markdown-bilder ![alt](bilder/<fil>) pekar på _kalla/artiklar/bilder/. Varje använd bild blir WebP i
# artikelns mapp (högst 1200 px bred, med bredd och höjd), och bilden i fältet bild blir dessutom en JPEG för delning
# (og:image – alla sociala tjänster läser inte WebP). Saknas en bild hoppas artikeln över i stället för att publiceras trasig.
IMG_SRC = ROOT / '_kalla' / 'artiklar'


def webp(src, out_dir):
    out = out_dir / (src.stem + '.webp')
    with Image.open(src) as im:
        im = im.convert('RGBA' if im.mode in ('RGBA', 'LA', 'P') else 'RGB')
        if im.width > 1200:
            im = im.resize((1200, round(im.height * 1200 / im.width)), Image.LANCZOS)
        im.save(out, 'WEBP', quality=82, method=6)
        return out.name, im.width, im.height


def share_jpeg(src, out_dir):
    out = out_dir / (src.stem + '-dela.jpg')
    with Image.open(src) as im:
        bg = Image.new('RGB', im.size, '#ffffff')
        bg.paste(im.convert('RGBA'), mask=im.convert('RGBA').split()[3])
        if bg.width > 1200:
            bg = bg.resize((1200, round(bg.height * 1200 / bg.width)), Image.LANCZOS)
        bg.save(out, 'JPEG', quality=85, optimize=True)
        return out.name, bg.width, bg.height


def article_images(a, out_dir):
    # Returnerar (ersättningar i HTML, delningsbild) eller None om en bild saknas.
    refs = re.findall(r'!\[[^\]]*\]\((bilder/[^)\s]+)\)', a['body'])
    if a.get('bild'):
        refs.append(a['bild'])
    missing = [x for x in refs if not (IMG_SRC / x).exists()]
    if missing:
        print(f'HOPPAR ÖVER {a["slug"]}: bild saknas: {", ".join(missing)}')
        return None
    out_dir.mkdir(parents=True, exist_ok=True)
    done = {x: webp(IMG_SRC / x, out_dir) for x in dict.fromkeys(refs)}
    share = share_jpeg(IMG_SRC / a['bild'], out_dir) if a.get('bild') else None
    return done, share


# Bildtext för foton (Wikimedia Commons, CC0/Public Domain): "Foto: <namn> / <källa>". foto_av kan vara "okänd",
# och foto_kalla kan vara en adress – då blir källan en länk med webbplatsens namn.
def photo_credit(a):
    who = a.get('foto_av', '').strip()
    who = '' if who.lower() in ('', 'okänd', 'okand', 'unknown') else H.escape(who)
    src = a.get('foto_kalla', '').strip()
    if src.startswith('http'):
        label = 'Wikimedia Commons' if 'wikimedia.org' in src or 'wikipedia.org' in src else re.sub(r'^https?://(www\.)?([^/]+).*$', r'\2', src)
        src = f'<a href="{H.escape(src)}">{label}</a>'
    else:
        src = H.escape(src)
    return 'Foto: ' + ' / '.join(x for x in (who or ('okänd fotograf' if src else ''), src) if x)


def place_images(html_text, done, a):
    # Byt <img alt="…" src="bilder/x.png"> mot WebP med mått i en figure; första bilden laddas direkt, resten lazy.
    count = [0]

    def figure(m):
        alt, src = m.group(1), m.group(2)
        name, w, h = done[src]
        lazy = '' if count[0] == 0 else ' loading="lazy"'
        count[0] += 1
        credit = ''
        if '-foto' in src and (a.get('foto_av') or a.get('foto_kalla')):
            credit = f'<figcaption>{photo_credit(a)}</figcaption>'
        return f'<figure><img src="{name}" alt="{alt}" width="{w}" height="{h}" decoding="async"{lazy}>{credit}</figure>'
    img = r'<img alt="([^"]*)" src="(bilder/[^"]+)"\s*/?>'
    html_text = re.sub(r'<p>\s*' + img + r'\s*</p>', figure, html_text)  # bild ensam i ett stycke
    return re.sub(img, figure, html_text)


for a in ARTICLES:
    # "## I appen" är artikelns egen mening om appen; den blir CTA-rutan och tas bort ur brödtexten.
    m = re.search(r'^## I appen\s*\n(.*?)(?=^## |\Z)', a['body'], re.S | re.M)
    app_text = markdown.markdown(m.group(1).strip())[3:-4] if m else None  # utan omslutande <p>
    a['body'] = (a['body'][:m.start()] + a['body'][m.end():]) if m else a['body']
    # CTA-rutan en gång, sist före "Vanliga frågor" (eller sist om avsnittet saknas).
    cta_box = cta(app_text) if app_text else ''
    if re.search(r'^## Vanliga frågor', a['body'], re.M):
        a['body'] = re.sub(r'^## Vanliga frågor', '<!--CTA-->\n\n## Vanliga frågor', a['body'], count=1, flags=re.M)
    else:
        a['body'] += '\n\n<!--CTA-->\n'
    md = markdown.Markdown(extensions=['tables', 'toc', 'sane_lists'])
    content = md.convert(a['body'])
    imgs = article_images(a, ROOT / 'artiklar' / a['slug'])
    if imgs is None:
        continue
    done, share = imgs
    content = place_images(content, done, a)
    calc = CALC.get(a.get('kalkylator', ''))
    # Kalkylatorrutan direkt efter det första svaret.
    calc_box = (f'<div class="card" style="box-shadow:none;border:1px solid var(--line)"><b>{calc[1]}</b>'
                f'<p class="small" style="margin:4px 0 8px">Kalkylatorn visar uträkningen steg för steg.</p>'
                f'<a class="btn" href="{{r}}{calc[0]}">Till kalkylatorn</a></div>') if calc else ''
    content = content.replace('</p>', '</p>' + calc_box, 1).replace('<!--CTA-->', cta_box)
    words = len(re.findall(r'\w+', a['body']))
    changed = a.get('uppdaterad') or a['publicera']
    others = [o for o in ARTICLES if o is not a][:3]
    url = f'{DOMAIN}/artiklar/{a["slug"]}/'
    head = ''
    if share:
        img_url = f'{url}{share[0]}'
        head = (f'<meta property="og:image" content="{img_url}"><meta property="og:image:width" content="{share[1]}">'
                f'<meta property="og:image:height" content="{share[2]}"><meta property="og:image:alt" content="{H.escape(a.get("bild_alt", ""))}">'
                f'<meta name="twitter:card" content="summary_large_image">\n')
    ld = [{'@context': 'https://schema.org', '@type': 'Article', 'headline': a['titel'], 'description': a.get('beskrivning', ''),
           **({'image': f'{url}{share[0]}'} if share else {}),
           'datePublished': a['publicera'], 'dateModified': changed, 'inLanguage': 'sv', 'mainEntityOfPage': url,
           'author': {'@type': 'Organization', 'name': 'Tyngdpunkt', 'url': DOMAIN},
           'publisher': {'@type': 'Organization', 'name': 'Tyngdpunkt', 'logo': {'@type': 'ImageObject', 'url': f'{DOMAIN}/assets/logo.svg'}}}]
    qa = faq(a['body'])
    if qa:
        ld.append({'@context': 'https://schema.org', '@type': 'FAQPage', 'mainEntity': qa})
    body = (f'<p class="small"><a href="{{r}}artiklar/">Artiklar</a> · {sv_date(a["publicera"])}'
            f'{f" · uppdaterad {sv_date(changed)}" if changed != a["publicera"] else ""} · {max(1, round(words / 200))} min läsning</p>'
            f'<article class="prose"><h1>{H.escape(a["titel"])}</h1>{content}</article>'
            + (f'<h2>Läs mer</h2>{article_list(others)}' if others else ''))
    page(f'artiklar/{a["slug"]}/index.html', a.get('seo_titel') or f'{a["titel"]} | Tyngdpunkt', a.get('beskrivning', ''), body,
         on='artiklar/', kind='article', jsonld=ld, lastmod=changed, head=head)

page('artiklar/index.html', 'Artiklar om träning och kost | Tyngdpunkt',
     'Artiklar om styrketräning, kost, kaloribehov och protein – på svenska, med siffror och uträkningar.', '''
<h1>Artiklar</h1>
<p class="lead">Svar på vanliga frågor om styrketräning och kost. Med siffror, uträkningar och källor.</p>
''' + (article_list(ARTICLES) if ARTICLES else '''<div class="card"><p style="margin:0">Den första artikeln kommer den 7 november. Under tiden kan du räkna på ditt
<a href="{r}kaloribehov/">kaloribehov</a>, ditt <a href="{r}proteinbehov/">proteinbehov</a> eller ditt <a href="{r}1rm/">1RM</a>.</p></div>'''), on='artiklar/')

# ---------- Appen ----------
page('tyngdpunkt/index.html', 'Tyngdpunkt – träningslogg och matlogg i samma app',
     'Tyngdpunkt är träningslogg och matlogg i samma app, på svenska. Varje vecka går appen igenom vikten, styrkan och hur väl du följt planen.', '''
<div class="bar"></div>
<h1>Tyngdpunkt</h1>
<p class="lead">Träningslogg och matlogg i samma app, på svenska.</p>
<div class="card">
<p style="margin-top:0">Du loggar passen och maten och väger dig. En gång i veckan går appen igenom vikten, styrkan i varje övning och hur väl du följde planen, och föreslår en sak att ändra. Uträkningen syns, och inget ändras förrän du har godkänt det.</p>
<p>Programmen ökar vikt och reps efter hur passen gick. Maten hittar du i Livsmedelsverkets databas och bland cirka 19 000 svenska märkesvaror, eller genom att skanna streckkoden.</p>
<p style="margin-bottom:0">All data stannar i telefonen, och det finns inget konto. 30 dagar gratis med allt, utan kort. Därefter 99 kr i månaden eller 699 kr om året.</p>
</div>
''' + cta('<strong>Appen är i test på Google Play.</strong> Har du en Android-telefon kan du testa den redan nu.') + '''
<p><a href="hjalp.html">Hjälp och kontakt</a> · <a href="integritet.html">Integritetspolicy</a></p>
''', on='tyngdpunkt/')

# Bli testare: appen är i stängt test, och alla knappar "Bli testare" leder hit.
page('tyngdpunkt/testa/index.html', 'Bli testare av Tyngdpunkt | Tyngdpunkt',
     'Testa träningsappen Tyngdpunkt gratis på Android innan den kommer ut på Google Play. Så går du med i testet, steg för steg.', f'''
<h1>Bli testare</h1>
<p class="lead">Tyngdpunkt är i test på Google Play, och appen finns bara för Android än så länge. Testa gratis och säg vad som saknas.</p>
<div class="card">
<h2 style="margin-top:0">Så går det till</h2>
<ol>
<li><b>Gå med i testgruppen</b> med det Google-konto som du använder i Play Butik: <a href="{GROUP}">groups.google.com/g/tyngdpunkt_app</a></li>
<li><b>Öppna testlänken</b> på din Android-telefon och tryck <b>Bli testare</b>: <a href="{OPT_IN}">play.google.com/apps/testing/se.tyngdpunkt.app</a></li>
<li><b>Ladda ner Tyngdpunkt</b> från Google Play som vanligt: <a href="{PLAY}">Tyngdpunkt i Play Butik</a></li>
</ol>
<p style="margin-bottom:0">Det räcker inte att gå med i gruppen, så gör alla tre stegen. Under testet kostar ingenting, och allt i appen är öppet.</p>
</div>
<p><a class="btn" href="{GROUP}">Gå med i testgruppen</a></p>
<p>Hittar du ett fel eller saknar något? Mejla <a href="mailto:kontakt@tyngdpunkt.se">kontakt@tyngdpunkt.se</a>.</p>
''', on='tyngdpunkt/')

# Integritetspolicy och hjälp: innehållet hämtas från _kalla/, så att texten bara finns på ett ställe.
for name, title, desc in [('integritet', 'Integritetspolicy – Tyngdpunkt', 'Integritetspolicy för appen Tyngdpunkt: all data stannar i telefonen.'),
                          ('hjalp', 'Hjälp och kontakt – Tyngdpunkt', 'Hjälp och kontakt för appen Tyngdpunkt.')]:
    page(f'tyngdpunkt/{name}.html', title, desc, '<div class="doc">' + (ROOT / '_kalla' / f'{name}.html').read_text() + '</div>', on='tyngdpunkt/')

# Gamla adresser: integritetspolicyn är angiven i Play Console som /integritet.html.
redirect('integritet.html', 'tyngdpunkt/integritet.html')
redirect('support.html', 'tyngdpunkt/hjalp.html')
# Sidan som visas när en adress inte finns (Cloudflare: not_found_handling = 404-page). Inte med i sitemap.
page('404.html', 'Sidan finns inte | Tyngdpunkt', 'Sidan finns inte.', '''
<h1>Sidan finns inte</h1>
<p class="lead">Adressen kan ha ändrats. Börja på <a href="/">startsidan</a> eller gå direkt till en kalkylator:
<a href="/kaloribehov/">kaloribehov</a>, <a href="/proteinbehov/">protein</a> eller <a href="/1rm/">1RM</a>.</p>
''')
SITEMAP[:] = [x for x in SITEMAP if not x[0].endswith('/404')]
# 404-sidan visas på vilken adress som helst, så dess relativa länkar måste utgå från roten.
(ROOT / '404.html').write_text((ROOT / '404.html').read_text().replace('<head>', '<head><base href="/">', 1))

# Sitemap och robots.txt: alla sidor utom de gamla omdirigeringarna.
(ROOT / 'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
                                  + ''.join(f'<url><loc>{u}</loc><lastmod>{d}</lastmod></url>\n' for u, d in SITEMAP) + '</urlset>\n')
(ROOT / 'robots.txt').write_text(f'User-agent: *\nAllow: /\nSitemap: {DOMAIN}/sitemap.xml\n')
print(f'Byggt: {len(SITEMAP)} sidor, {len(ARTICLES)} publicerade artiklar.')
