#!/usr/bin/env python3
"""
translate_it_en.py — Traduzione semi-automatica IT→EN dei capitoli LaTeX DEQ²
Sostituisce terminologia tecnica e strutturale; il testo narrativo richiede revisione.

Uso:
    python translate_it_en.py 02-geometria.tex > chapters-en/02-geometry.tex
    python translate_it_en.py --all   # traduce tutti
"""

import re
import sys
from pathlib import Path

SRC = Path("C:/Users/Utente/bilanciere-quantistico/chapters-it")
DST = Path("C:/Users/Utente/bilanciere-quantistico/chapters-en")

# ─── Mappa file IT → EN ───────────────────────────────────────────────────────
FILE_MAP = {
    "02-geometria.tex":              "02-geometry.tex",
    "03-equazione-unificata.tex":    "03-unified-equation.tex",
    "04-forma-sistemica.tex":        "04-systemic-form.tex",
    "05-quattro-variabili.tex":      "05-four-variables.tex",
    "06-solitone-musk.tex":          "06-soliton-musk.tex",
    "07-egemone-decoerente.tex":     "07-decoherent-hegemon.tex",
    "08-rigido-sincronizzato.tex":   "08-rigid-synchronized.tex",
    "09-bilanciere-brasile.tex":     "09-quantum-balance-brazil.tex",
    "10-dashboard-spc.tex":         "10-spc-dashboard.tex",
    "11-predizioni-datate.tex":      "11-dated-predictions.tex",
    "12-strategie-antifragili.tex":  "12-antifragile-strategies.tex",
    "13-conclusioni.tex":            "13-conclusions.tex",
    "AppA-derivazione-formale.tex":  "AppA-formal-derivation.tex",
    "AppB-calibrazione-sigma.tex":   "AppB-sigma-calibration.tex",
    "AppC-protocolli-misurazione.tex": "AppC-measurement-protocols.tex",
    "AppD-dialogo-tradizioni.tex":   "AppD-dialogue-traditions.tex",
}

# ─── Dizionario terminologico (ordine importante: più specifico prima) ─────────
TERMS = [
    # ── Titoli di capitoli e appendici ──
    ("La Geometria: l'Apparato Macro",          "The Geometry: the Macro Apparatus"),
    ("L'Equazione Unificata:",                   "The Unified Equation:"),
    ("La Forma Sistemica:",                      "The Systemic Form:"),
    ("Le Quattro Variabili Strutturali in Quadro Coerente", "The Four Structural Variables in a Coherent Framework"),
    ("Il Solitone (Musk):",                      "The Soliton (Musk):"),
    ("L'Egemone Decoerente (USA):",              "The Decoherent Hegemon (USA):"),
    ("Il Rigido Sincronizzato (Cina):",          "The Rigid Synchronized (China):"),
    ("Il Bilanciere Quantistico (Brasile):",     "The Quantum Balance (Brazil):"),
    ("Scenari Quantizzati e Dashboard SPC-DEQ", "Quantized Scenarios and SPC-DEQ Dashboard"),
    ("Predizioni Rischiose Datate:",             "Risky Dated Predictions:"),
    ("Cosa Fare: Strategie Antifragili",         "What to Do: Antifragile Strategies"),
    ("Conclusioni e Ricerca Futura",             "Conclusions and Future Research"),
    ("Derivazione Formale Completa",             "Complete Formal Derivation"),
    ("Calibrazione Empirica di",                 "Empirical Calibration of"),
    ("Protocolli di Misurazione dei Parametri DEQ", "DEQ² Parameter Measurement Protocols"),
    ("Dialogo Testuale con le Tradizioni",       "Textual Dialogue with Traditions"),

    # ── Sezioni tipiche ──
    ("Argomento portante:",           "Core argument:"),
    ("Note Epistemiche di Chiusura Capitolo", "Closing Epistemic Notes"),
    ("Note Epistemiche di Chiusura",  "Closing Epistemic Notes"),
    ("Apertura della Parte",          "Opening of Part"),
    ("Sintesi del Capitolo",          "Chapter Summary"),
    ("Definizione Strutturale",       "Structural Definition"),
    ("Criteri DEQ",                   "DEQ Criteria"),

    # ── Termini DEQ² ──
    ("Egemone Decoerente",           "Decoherent Hegemon"),
    ("Rigido Sincronizzato",         "Rigid Synchronized"),
    ("Bilanciere Quantistico",       "Quantum Balance"),
    ("Solitone",                     "Soliton"),
    ("parametro d'ordine",           "order parameter"),
    ("transizione di fase",          "phase transition"),
    ("coerenza di fase",             "phase coherence"),
    ("soglia critica",               "critical threshold"),
    ("stato critico",                "critical state"),
    ("regime sub-critico",           "subcritical regime"),
    ("regime super-critico",         "supercritical regime"),
    ("decoerenza",                   "decoherence"),
    ("sincronizzazione",             "synchronization"),
    ("accoppiamento",                "coupling"),
    ("forza di accoppiamento",       "coupling strength"),
    ("campo medio",                  "mean field"),
    ("trasposizione di scala",       "scale transposition"),
    ("invarianza di scala",          "scale invariance"),
    ("microfondazione",              "micro-foundation"),
    ("microfondazioni",              "micro-foundations"),
    ("Folk Theorem Discorsivo",      "Discursive Folk Theorem"),
    ("Folk Theorem della Geometria", "Geometry Folk Theorem"),
    ("Folk Theorem",                 "Folk Theorem"),
    ("equilibrio separante bayesiano", "Bayesian separating equilibrium"),
    ("equilibrio di Nash perfetto nei sottogiochi", "subgame perfect Nash equilibrium"),
    ("equilibrio di Nash",           "Nash equilibrium"),
    ("ottimo paretiano",             "Pareto optimum"),
    ("Barbarie Tecnologica",         "Technological Barbarism"),
    ("fattore di erosione",          "erosion factor"),
    ("effetto boomerang",            "boomerang effect"),
    ("massa comunicativa",           "communicative mass"),
    ("qualità etica",                "ethical quality"),
    ("resistenza critica",           "critical resistance"),
    ("funzione predittiva",          "predictive function"),
    ("legge predittiva",             "predictive law"),
    ("legge micro fondamentale",     "fundamental micro law"),
    ("payoff istantaneo",            "instantaneous payoff"),
    ("frequenza naturale",           "natural frequency"),

    # ── Topografia ──
    ("Spazio Discorsivo",            "Discursive Space"),
    ("spazio discorsivo",            "discursive space"),
    ("Vettore Etico",                "Ethical Vector"),
    ("vettore etico",                "ethical vector"),
    ("coerenza formale",             "formal coherence"),
    ("precisione tecnica",           "technical precision"),
    ("complessità dialettica",       "dialectical complexity"),
    ("amplificazione algoritmica",   "algorithmic amplification"),
    ("saturazione",                  "saturation"),
    ("impatto atteso",               "expected impact"),
    ("resistenza nulla",             "zero resistance"),
    ("propaganda efficace",          "effective propaganda"),
    ("propaganda inerte",            "inert propaganda"),
    ("agire comunicativo habermasiano", "Habermasian communicative action"),
    ("Scuola di Francoforte",        "Frankfurt School"),
    ("industria culturale",          "culture industry"),
    ("colonizzazione del mondo della vita", "colonization of the lifeworld"),
    ("rendimenti decrescenti",       "diminishing returns"),

    # ── Geometria ──
    ("coesione interna",             "internal cohesion"),
    ("capacità materiale",           "material capacity"),
    ("legittimità etico-discorsiva", "ethical-discursive legitimacy"),
    ("fattore di sconto",            "discount factor"),
    ("orizzonte temporale",          "time horizon"),
    ("proiezione sull'asse dialettico", "projection on the dialectical axis"),
    ("volatilità stocastica",        "stochastic volatility"),
    ("coefficiente di disimpegno morale", "moral disengagement coefficient"),
    ("biforcazione",                 "bifurcation"),
    ("punto di biforcazione",        "bifurcation point"),
    ("stabilità strutturale",        "structural stability"),
    ("collasso",                     "collapse"),
    ("collasso sistemico",           "systemic collapse"),
    ("transizione egemonica",        "hegemonic transition"),
    ("ciclo egemonico",              "hegemonic cycle"),

    # ── Kuramoto ──
    ("parametro d'ordine complesso", "complex order parameter"),
    ("riduzione di campo medio",     "mean-field reduction"),
    ("fase oscillante",              "oscillating phase"),
    ("sincronizzazione parziale",    "partial synchronization"),
    ("sincronizzazione piena",       "full synchronization"),
    ("decoerenza completa",          "full decoherence"),
    ("operatore di trasposizione",   "transposition operator"),
    ("grandezza locale",             "local quantity"),
    ("quantità sistemica derivata",  "derived systemic quantity"),

    # ── Antifragilità ──
    ("convessità positiva",          "positive convexity"),
    ("concavità negativa",           "negative concavity"),
    ("fragilità",                    "fragility"),
    ("antifragilità",                "antifragility"),
    ("antifragile",                  "antifragile"),
    ("robusto",                      "robust"),
    ("resiliente",                   "resilient"),
    ("resilienza",                   "resilience"),
    ("indice di antifragilità",      "antifragility index"),
    ("risposta a sigma",             "response to sigma"),
    ("involuzione",                  "involution"),
    ("Neijuan",                      "Neijuan"),
    ("elite overproduction",         "elite overproduction"),
    ("pressione demografica",        "demographic pressure"),

    # ── Attori ──
    ("Egemone Decoerente",           "Decoherent Hegemon"),
    ("Rigido Sincronizzato",         "Rigid Synchronized"),
    ("Bilanciere Quantistico",       "Quantum Balance"),
    ("Estado Logístico",             "Estado Logístico"),
    ("Phi-engine",                   "Phi-engine"),
    ("motore di coerenza",           "coherence engine"),
    ("iper-estensione",              "hyper-extension"),
    ("polarizzazione affettiva",     "affective polarization"),
    ("legittimità",                  "legitimacy"),
    ("rete di coordinamento",        "coordination network"),

    # ── Predizioni ──
    ("predizione rischiosa",         "risky prediction"),
    ("predizioni rischiose",         "risky predictions"),
    ("predizione datata",            "dated prediction"),
    ("soglia numerica",              "numerical threshold"),
    ("fonte dati pubblica",          "public data source"),
    ("falsificazione",               "falsification"),
    ("falsificabilità",              "falsifiability"),
    ("pre-registrazione",            "pre-registration"),
    ("aggiornamento bayesiano",      "Bayesian updating"),
    ("probabilità soggettiva",       "subjective probability"),
    ("correzione locale",            "local correction"),
    ("riformulazione strutturale",   "structural reformulation"),
    ("aggiustamento parametrico",    "parametric adjustment"),
    ("strutturale",                  "structural"),
    ("locale",                       "local"),
    ("condizionale",                 "conditional"),
    ("pendente",                     "pending"),

    # ── Dashboard SPC ──
    ("Dashboard SPC-DEQ",            "SPC-DEQ Dashboard"),
    ("pannello bivariato",           "bivariate panel"),
    ("pannello aggregato",           "aggregate panel"),
    ("regola WE-DEQ",                "WE-DEQ rule"),
    ("causa speciale",               "special cause"),
    ("fuori-limite",                 "out-of-control"),
    ("indice di capacità",           "capability index"),
    ("limiti di controllo",          "control limits"),
    ("limite superiore",             "upper limit"),
    ("limite inferiore",             "lower limit"),

    # ── Struttura libro ──
    ("Parte I",   "Part I"),
    ("Parte II",  "Part II"),
    ("Parte III", "Part III"),
    ("Parte IV",  "Part IV"),
    ("Parte V",   "Part V"),
    ("Cap. 1",  "Ch.~1"),
    ("Cap. 2",  "Ch.~2"),
    ("Cap. 3",  "Ch.~3"),
    ("Cap. 4",  "Ch.~4"),
    ("Cap. 5",  "Ch.~5"),
    ("Cap. 6",  "Ch.~6"),
    ("Cap. 7",  "Ch.~7"),
    ("Cap. 8",  "Ch.~8"),
    ("Cap. 9",  "Ch.~9"),
    ("Cap. 10", "Ch.~10"),
    ("Cap. 11", "Ch.~11"),
    ("Cap. 12", "Ch.~12"),
    ("Cap. 13", "Ch.~13"),
    ("App. A",  "App.~A"),
    ("App. B",  "App.~B"),
    ("App. C",  "App.~C"),
    ("App. D",  "App.~D"),
    ("capitolo", "chapter"),
    ("Capitolo", "Chapter"),
    ("appendice", "appendix"),
    ("Appendice", "Appendix"),
    ("tabella",  "table"),
    ("Tabella",  "Table"),
    ("figura",   "figure"),
    ("sezione",  "section"),
    ("il lettore", "the reader"),
    ("nel testo",  "in the text"),

    # ── Parole connettive italiane ──
    ("dove:",    "where:"),
    ("dove ",    "where "),
    ("quindi",   "therefore"),
    ("dunque",   "therefore"),
    ("dunque:",  "therefore:"),
    ("pertanto", "thus"),
    ("inoltre",  "moreover"),
    ("tuttavia", "however"),
    ("invece",   "instead"),
    ("mentre",   "while"),
    ("poiché",   "since"),
    ("perché",   "because"),
    ("sebbene",  "although"),
    ("nonostante", "despite"),
    ("ovvero",   "that is"),
    ("ossia",    "namely"),
    ("cioè",     "i.e.,"),
    ("ad esempio", "for example"),
    ("per esempio", "for example"),
    ("in particolare", "in particular"),
    ("in generale", "in general"),
    ("in sintesi", "in summary"),
    ("in conclusione", "in conclusion"),
    ("si noti che", "note that"),
    ("si osserva che", "observe that"),
    ("è possibile", "it is possible"),
    ("è necessario", "it is necessary"),
    ("è sufficiente", "it is sufficient"),
    ("è facile", "it is easy"),
    ("è importante", "it is important"),
    ("abbiamo",  "we have"),
    ("otteniamo", "we obtain"),
    ("deriva",   "follows"),
    ("segue",    "follows"),
    ("si dimostra", "it can be shown"),
    ("si può",   "one can"),
    ("da cui",   "from which"),
    ("per cui",  "for which"),
    ("il quale", "which"),
    ("la quale", "which"),
    ("i quali",  "which"),
    ("le quali", "which"),
    ("tale che", "such that"),
    ("così",     "thus"),
    ("così che", "so that"),
    ("allora",   "then"),
    ("infine",   "finally"),
    ("prima",    "first"),
    ("poi",      "then"),
    ("quindi",   "then"),
    ("dopo",     "after"),
    ("prima di", "before"),
    ("dopo di",  "after"),
    ("tramite",  "through"),
    ("mediante", "through"),
    ("attraverso", "through"),
    ("rispetto a", "with respect to"),
    ("relativamente a", "relative to"),
    ("in termini di", "in terms of"),
    ("in funzione di", "as a function of"),
    ("a partire da", "starting from"),
    ("a causa di", "due to"),
    ("grazie a",  "thanks to"),
    ("in presenza di", "in the presence of"),
    ("in assenza di", "in the absence of"),
    ("in modo che", "such that"),
    ("al fine di", "in order to"),
    ("allo scopo di", "with the aim of"),
    ("al contrario", "on the contrary"),
    ("d'altra parte", "on the other hand"),
    ("da un lato", "on one hand"),
    ("dall'altro", "on the other"),
    ("sia...sia", "both...and"),
    ("né...né",  "neither...nor"),
    ("non solo...ma anche", "not only...but also"),
    ("tanto...quanto", "as much...as"),

    # ── Epistemic labels ──
    ("Affermazione",  "Claim"),
    ("affermazione",  "claim"),
    ("Riferimento",   "Reference"),
    ("riferimento",   "reference"),
    ("Status",        "Status"),
    ("definizione operativa", "operational definition"),
    ("stima empirica su corpus", "empirical estimate on corpus"),
    ("giustificata teoricamente", "theoretically justified"),
    ("derivato dai payoff", "derived from payoffs"),
    ("verificato",    "verified"),
    ("ipotesi strutturale", "structural hypothesis"),
    ("ipotesi operativa", "working hypothesis"),
    ("derivazione coerente", "coherent derivation"),
    ("aggregazione completa", "complete aggregation"),
    ("classificazione completa", "complete classification"),
    ("analisi strutturale", "structural analysis"),
    ("protocollo operativo", "operational protocol"),
    ("metodologia",   "methodology"),

    # ── Termini paese ──
    ("gli Stati Uniti", "the United States"),
    ("Stati Uniti",  "United States"),
    ("USA",          "USA"),
    ("Cina",         "China"),
    ("cinese",       "Chinese"),
    ("brasiliano",   "Brazilian"),
    ("brasiliana",   "Brazilian"),
    ("Brasile",      "Brazil"),
    ("Europa",       "Europe"),
    ("europeo",      "European"),
    ("europei",      "European"),
    ("Russia",       "Russia"),
    ("russo",        "Russian"),
    ("India",        "India"),
    ("indiano",      "Indian"),
    ("BRICS",        "BRICS"),
    ("FMI",          "IMF"),
    ("Banca Mondiale", "World Bank"),
    ("Nazioni Unite", "United Nations"),
    ("NATO",         "NATO"),
    ("G7",           "G7"),
    ("G20",          "G20"),

    # ── Vari termini tecnici ──
    ("misurazione",  "measurement"),
    ("misurabile",   "measurable"),
    ("operativizzato", "operationalized"),
    ("operativo",    "operational"),
    ("formale",      "formal"),
    ("formalismo",   "formalism"),
    ("variabile",    "variable"),
    ("variabili",    "variables"),
    ("parametro",    "parameter"),
    ("parametri",    "parameters"),
    ("operatore",    "operator"),
    ("operatori",    "operators"),
    ("equazione",    "equation"),
    ("equazioni",    "equations"),
    ("ipotesi",      "hypothesis"),
    ("verifica",     "verification"),
    ("dimostrazione", "proof"),
    ("dimostrato",   "proved"),
    ("congettura",   "conjecture"),
    ("teorema",      "theorem"),
    ("lemma",        "lemma"),
    ("corollario",   "corollary"),
    ("proposizione", "proposition"),
    ("definizione",  "definition"),
    ("osservazione", "remark"),
    ("nota",         "note"),
    ("esempio",      "example"),
    ("problema aperto", "open problem"),

    # ── Frase finali tabelle ──
    ("stessa soglia",   "same threshold"),
    ("invarianza di scala", "scale invariance"),
    ("microstruttura",  "microstructure"),
    ("strategia del",   "strategy of the"),
    ("legge locale del campo", "local field law"),
    ("emerge",          "emerges"),
    ("Legge locale",    "Local field law"),
    ("Microstruttura",  "Microstructure"),
]

# ─── Substitution engine ──────────────────────────────────────────────────────

def translate(tex: str) -> str:
    """Applica la mappa terminologica al testo LaTeX."""
    # Preserva ambienti math (non tradurre il loro contenuto)
    # Semplice approccio: applica solo fuori da ambienti math
    math_pattern = re.compile(
        r'(\\\[[\s\S]*?\\\]'      # \[...\]
        r'|\$\$[\s\S]*?\$\$'      # $$...$$
        r'|\\\([\s\S]*?\\\)'      # \(...\)
        r'|\$[^\$\n]+?\$)'        # $...$
    )
    parts = math_pattern.split(tex)
    result = []
    for i, part in enumerate(parts):
        in_math = (i % 2 == 1)
        if not in_math:
            for it, en in TERMS:
                part = part.replace(it, en)
        result.append(part)
    return ''.join(result)

# ─── Main ─────────────────────────────────────────────────────────────────────

def translate_file(src_name: str, dst_name: str):
    src = SRC / src_name
    dst = DST / dst_name
    print(f"  {src_name} -> {dst_name}")
    tex = src.read_text(encoding='utf-8')
    tex = translate(tex)
    dst.write_text(tex, encoding='utf-8')

def main():
    if '--all' in sys.argv:
        DST.mkdir(exist_ok=True)
        for src_name, dst_name in FILE_MAP.items():
            translate_file(src_name, dst_name)
        print("[OK] Tutti i file tradotti.")
    elif len(sys.argv) >= 2:
        src_name = sys.argv[1]
        dst_name = FILE_MAP.get(src_name, src_name.replace('.tex', '-en.tex'))
        DST.mkdir(exist_ok=True)
        translate_file(src_name, dst_name)
    else:
        print("Uso: python translate_it_en.py [file.tex | --all]")

if __name__ == '__main__':
    main()
