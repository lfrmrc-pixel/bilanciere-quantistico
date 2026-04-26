#!/usr/bin/env python3
"""
preprocess_deq.py — Converte capitoli Obsidian MD → LaTeX per Il Bilanciere Quantistico
Uso: python preprocess_deq.py
"""
import re
import subprocess
import sys
from pathlib import Path

VAULT = Path("C:/Users/Utente/Desktop/Claude Brain/Claude Brain/02 - PROGETTI/SCIENZE UMANE/GEOPOLITICA")
OUT   = Path("C:/Users/Utente/bilanciere-quantistico/chapters-it")

CHAPTERS = [
    ("DEQ-Cap01-Topografia.md",            "01-topografia.tex"),
    ("DEQ-Cap02-Geometria.md",             "02-geometria.tex"),
    ("DEQ-Cap03-Equazione-Unificata.md",   "03-equazione-unificata.tex"),
    ("DEQ-Cap04-Forma-Sistemica.md",       "04-forma-sistemica.tex"),
    ("DEQ-Cap05-Quattro-Variabili.md",     "05-quattro-variabili.tex"),
    ("DEQ-Cap06-Solitone-Musk.md",         "06-solitone-musk.tex"),
    ("DEQ-Cap07-Egemone-Decoerente.md",    "07-egemone-decoerente.tex"),
    ("DEQ-Cap08-Rigido-Sincronizzato.md",  "08-rigido-sincronizzato.tex"),
    ("DEQ-Cap09-Bilanciere-Brasile.md",    "09-bilanciere-brasile.tex"),
    ("DEQ-Cap10-Dashboard-SPC.md",         "10-dashboard-spc.tex"),
    ("DEQ-Cap11-Predizioni-Datate.md",     "11-predizioni-datate.tex"),
    ("DEQ-Cap12-Strategie-Antifragili.md", "12-strategie-antifragili.tex"),
    ("DEQ-Cap13-Conclusioni.md",           "13-conclusioni.tex"),
    ("DEQ-AppA-Derivazione-Formale.md",    "AppA-derivazione-formale.tex"),
    ("DEQ-AppB-Calibrazione-Sigma.md",     "AppB-calibrazione-sigma.tex"),
    ("DEQ-AppC-Protocolli-Misurazione.md", "AppC-protocolli-misurazione.tex"),
    ("DEQ-AppD-Dialogo-Tradizioni.md",     "AppD-dialogo-tradizioni.tex"),
]

# ─── Pre-processing (su Markdown) ─────────────────────────────────────────────

def strip_yaml(text):
    """Rimuove frontmatter YAML."""
    if text.startswith('---'):
        end = text.find('\n---', 3)
        if end != -1:
            return text[end + 4:].lstrip('\n')
    return text

def remove_footers(text):
    """Rimuove righe di footer Obsidian."""
    lines = text.split('\n')
    clean = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith('*Bozza di lavoro'):
            continue
        if stripped.startswith('*Collegato a:'):
            continue
        if stripped.startswith('*Successivo:'):
            continue
        clean.append(line)
    while clean and not clean[-1].strip():
        clean.pop()
    return '\n'.join(clean)

def convert_wikilinks(text):
    """[[link|alias]] → alias;  [[link]] → link."""
    text = re.sub(r'\[\[([^|\]]+)\|([^\]]+)\]\]', r'\2', text)
    text = re.sub(r'\[\[([^\]]+)\]\]',             r'\1', text)
    return text

def convert_emoji(text):
    """Converte marker epistemici in comandi LaTeX."""
    text = text.replace('✅', r'\Proved{}')
    text = text.replace('\U0001f535', r'\Hypoth{}')   # 🔵
    text = text.replace('\U0001f7e1', r'\Conj{}')     # 🟡
    text = text.replace('❌', r'\ToVerify{}')
    return text

def remove_cjk(text):
    """Rimuove caratteri CJK (Neijuan, Hexin) — la trascrizione è già nel testo."""
    text = text.replace('核心地位', '')
    text = text.replace('内卷', '')
    text = re.sub(r'[一-鿿㐀-䶿　-〿]+', '', text)
    return text

def clean_headings(text):
    """
    Rimuove prefissi ridondanti dai titoli markdown:
    - "# Capitolo N — Titolo" → "# Titolo"
    - "# Appendice X — Titolo" → "# Titolo"
    - "## 7.0 Sezione" → "## Sezione"
    - "## A.1 Sezione" → "## Sezione"
    """
    lines = text.split('\n')
    clean = []
    for line in lines:
        m = re.match(r'^(#+)\s+(?:Capitolo\s+\d+|Appendice\s+[A-Z])\s+[—–-]+\s+(.*)', line)
        if m:
            clean.append(f"{m.group(1)} {m.group(2)}")
            continue
        m = re.match(r'^(#+)\s+(?:[A-Z]\.)?(?:\d+\.)*\d+\s+(.*)', line)
        if m:
            clean.append(f"{m.group(1)} {m.group(2)}")
            continue
        clean.append(line)
    return '\n'.join(clean)

def preprocess_md(md_text):
    text = strip_yaml(md_text)
    text = remove_footers(text)
    text = convert_wikilinks(text)
    text = convert_emoji(text)
    text = remove_cjk(text)
    text = clean_headings(text)
    return text

# ─── Conversione pandoc ────────────────────────────────────────────────────────

def md_to_latex(md_text):
    """Usa pandoc per convertire MD → LaTeX (solo body, senza preamble)."""
    result = subprocess.run(
        [
            'pandoc',
            '--from=markdown+tex_math_dollars+raw_tex',
            '--to=latex',
            '--top-level-division=chapter',
            '--no-highlight',
            '-',
        ],
        input=md_text,
        capture_output=True,
        text=True,
        encoding='utf-8',
    )
    if result.returncode != 0:
        print(f"  [ERRORE PANDOC] {result.stderr[:500]}", file=sys.stderr)
    return result.stdout

# ─── Post-processing (su LaTeX) ───────────────────────────────────────────────

def remove_hrules(tex):
    """Rimuove righe orizzontali decorative generate da ---."""
    tex = re.sub(r'\\begin\{center\}\\rule\{[^}]+\}\{[^}]+\}\\end\{center\}', '', tex)
    return tex

def fix_tables(tex):
    """Wrappa ogni ambiente tabular/longtable in {\\small ...}."""
    tex = re.sub(
        r'(\\begin\{(?:longtable|tabular)\*?\})',
        r'{\\small\1',
        tex
    )
    tex = re.sub(
        r'(\\end\{(?:longtable|tabular)\*?\})',
        r'\1}',
        tex
    )
    return tex

# Forme bare (dentro math) e forme testo (fuori math) per i caratteri unicode
_MATH_FORMS = {
    '°': r'^\circ',
    '²': r'^2',
    '¹': r'^1',
    '→': r'\to',
    '⇒': r'\Rightarrow',
    '↔': r'\leftrightarrow',
    '≠': r'\neq',
    'Π': r'\Pi',
    'Φ': r'\Phi',
    'Ω': r'\Omega',
    '×': r'\times',
    '≥': r'\geq',
    '≤': r'\leq',
    '≈': r'\approx',
    '−': r'-',
}
_TEXT_FORMS = {
    '°': r'$^\circ$',
    '²': r'$^2$',
    '¹': r'$^1$',
    '→': r'$\to$',
    '⇒': r'$\Rightarrow$',
    '↔': r'$\leftrightarrow$',
    '≠': r'$\neq$',
    'Π': r'$\Pi$',
    'Φ': r'$\Phi$',
    'Ω': r'$\Omega$',
    '×': r'$\times$',
    '≥': r'$\geq$',
    '≤': r'$\leq$',
    '≈': r'$\approx$',
    '−': r'--',
    '§': r'\S{}',
}

# Pattern che riconosce ambienti math nel LaTeX generato da pandoc
_MATH_PATTERN = re.compile(
    r'(\\\[[\s\S]*?\\\]'      # \[...\]  display math
    r'|\$\$[\s\S]*?\$\$'      # $$...$$ display math
    r'|\\\([\s\S]*?\\\)'      # \(...\) inline math
    r'|\$[^\$\n]+?\$)'        # $...$ inline math
)

def convert_unicode_latex_smart(tex):
    """
    Converte caratteri Unicode non-T1 nel LaTeX generato da pandoc.
    Rispetta math/testo: dentro ambienti math usa forme bare, fuori usa $...$.
    """
    parts = _MATH_PATTERN.split(tex)
    result = []
    for i, part in enumerate(parts):
        in_math = (i % 2 == 1)
        forms = _MATH_FORMS if in_math else _TEXT_FORMS
        for char, latex_form in forms.items():
            part = part.replace(char, latex_form)
        result.append(part)
    return ''.join(result)

def fix_long_chapter_titles(tex):
    """Avvisa per titoli capitolo > 50 caratteri."""
    for m in re.finditer(r'\\chapter\{([^}]{50,})\}', tex):
        print(f"  [AVVISO] Titolo lungo ({len(m.group(1))} car): {m.group(1)[:60]}...")
    return tex

def postprocess_latex(tex):
    tex = remove_hrules(tex)
    tex = fix_tables(tex)
    tex = convert_unicode_latex_smart(tex)
    tex = fix_long_chapter_titles(tex)
    return tex

# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    errors = []
    for md_file, tex_file in CHAPTERS:
        src = VAULT / md_file
        dst = OUT / tex_file
        if not src.exists():
            print(f"[MANCANTE] {md_file}")
            errors.append(md_file)
            continue
        print(f"Elaboro {md_file} ...", end=' ', flush=True)
        md = src.read_text(encoding='utf-8')
        md = preprocess_md(md)
        tex = md_to_latex(md)
        tex = postprocess_latex(tex)
        dst.write_text(tex, encoding='utf-8')
        print(f"-> {tex_file} ({len(tex):,} chars)")

    if errors:
        print(f"\n[ERRORI] File mancanti: {errors}")
    else:
        print("\n[OK] Tutti i file convertiti.")

if __name__ == '__main__':
    main()
