"""Kopierar godkända artiklar från _kalla/artiklar/ till _kalla/godkanda/, som ligger i repot.

Kör: python3 _kalla/synka.py (från webb/). Körs av publiceringsjobbet på Andreas dator.
GitHub-jobbet (.github/workflows/publicera.yml) bygger sedan sajten varje morgon och publicerar de godkända artiklar
vars datum har kommit – utan att datorn behöver vara på. Utkast kopieras aldrig: de ska inte till det publika repot.
En artikel som inte längre är godkänd tas bort ur godkanda/.
"""
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / '_kalla' / 'artiklar'
DST = ROOT / '_kalla' / 'godkanda'


def status(text):
    m = re.search(r'^status:\s*(.+)$', text.split('\n---', 1)[0], re.M)
    return m.group(1).strip().strip('"') if m else ''


def images(text):
    refs = re.findall(r'!\[[^\]]*\]\((bilder/[^)\s]+)\)', text)
    m = re.search(r'^bild:\s*(\S+)', text, re.M)
    return dict.fromkeys(refs + ([m.group(1)] if m else []))


def copy(src, dst):
    if dst.exists() and dst.read_bytes() == src.read_bytes():
        return False
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    return True


changed = []
for f in sorted(SRC.glob('*.md')) if SRC.exists() else []:
    text = f.read_text()
    out = DST / f.name
    if status(text) != 'godkand':
        if out.exists():
            out.unlink()
            changed.append(f'tog bort {f.stem} (inte längre godkänd)')
        continue
    imgs = [x for x in images(text) if (SRC / x).exists()]
    new = [x for x in imgs if copy(SRC / x, DST / x)]
    if copy(f, out) or new:
        changed.append(f'kopierade {f.stem}' + (f' + {len(new)} bild(er)' if new else ''))

# Bilder som ingen kopierad artikel längre pekar på tas bort.
used = {x for f in DST.glob('*.md') for x in images(f.read_text())}
for img in sorted((DST / 'bilder').glob('*')) if (DST / 'bilder').exists() else []:
    if f'bilder/{img.name}' not in used:
        img.unlink()
        changed.append(f'tog bort bilden {img.name}')

print('\n'.join(changed) if changed else 'Inga ändringar i godkända artiklar.')
