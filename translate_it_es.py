#!/usr/bin/env python3
"""
translate_it_es.py — Traduzione semi-automatica IT→ES dei capitoli LaTeX DEQ²
Sostituisce terminologia tecnica e strutturale; il testo narrativo richiede revisione.

Uso:
    python translate_it_es.py --all   # traduce tutti
"""

import re
import sys
from pathlib import Path

SRC = Path("C:/Users/Utente/bilanciere-quantistico/chapters-it")
DST = Path("C:/Users/Utente/bilanciere-quantistico/chapters-es")

FILE_MAP = {
    "01-topografia.tex":              "01-topografia.tex",
    "02-geometria.tex":               "02-geometria.tex",
    "03-equazione-unificata.tex":     "03-ecuacion-unificada.tex",
    "04-forma-sistemica.tex":         "04-forma-sistemica.tex",
    "05-quattro-variabili.tex":       "05-cuatro-variables.tex",
    "06-solitone-musk.tex":           "06-soliton-musk.tex",
    "07-egemone-decoerente.tex":      "07-hegemon-decoherente.tex",
    "08-rigido-sincronizzato.tex":    "08-rigido-sincronizado.tex",
    "09-bilanciere-brasile.tex":      "09-balanza-brasil.tex",
    "10-dashboard-spc.tex":          "10-dashboard-spc.tex",
    "11-predizioni-datate.tex":       "11-predicciones-fechadas.tex",
    "12-strategie-antifragili.tex":   "12-estrategias-antifragiles.tex",
    "13-conclusioni.tex":             "13-conclusiones.tex",
    "AppA-derivazione-formale.tex":   "AppA-derivacion-formal.tex",
    "AppB-calibrazione-sigma.tex":    "AppB-calibracion-sigma.tex",
    "AppC-protocolli-misurazione.tex": "AppC-protocolos-medicion.tex",
    "AppD-dialogo-tradizioni.tex":    "AppD-dialogo-tradiciones.tex",
}

TERMS = [
    # ── Titoli capitoli e appendici ──
    ("La Topografia: l'Apparato Micro",           "La Topografía: el Aparato Micro"),
    ("La Geometria: l'Apparato Macro",            "La Geometría: el Aparato Macro"),
    ("L'Equazione Unificata:",                    "La Ecuación Unificada:"),
    ("La Forma Sistemica:",                       "La Forma Sistémica:"),
    ("Le Quattro Variabili Strutturali in Quadro Coerente", "Las Cuatro Variables Estructurales en Marco Coherente"),
    ("Il Solitone (Musk):",                       "El Solitón (Musk):"),
    ("L'Egemone Decoerente (USA):",               "El Hegemón Decoherente (EE.UU.):"),
    ("Il Rigido Sincronizzato (Cina):",           "El Rígido Sincronizado (China):"),
    ("Il Bilanciere Quantistico (Brasile):",      "La Balanza Cuántica (Brasil):"),
    ("Scenari Quantizzati e Dashboard SPC-DEQ",  "Escenarios Cuantizados y Dashboard SPC-DEQ"),
    ("Predizioni Rischiose Datate:",              "Predicciones Arriesgadas Fechadas:"),
    ("Cosa Fare: Strategie Antifragili",          "Qué Hacer: Estrategias Antifrágiles"),
    ("Conclusioni e Ricerca Futura",              "Conclusiones e Investigación Futura"),
    ("Derivazione Formale Completa",              "Derivación Formal Completa"),
    ("Calibrazione Empirica di",                  "Calibración Empírica de"),
    ("Protocolli di Misurazione dei Parametri DEQ", "Protocolos de Medición de Parámetros DEQ²"),
    ("Dialogo Testuale con le Tradizioni",        "Diálogo Textual con las Tradiciones"),

    # ── Sezioni tipiche ──
    ("Argomento portante:",            "Argumento central:"),
    ("Note Epistemiche di Chiusura Capitolo", "Notas Epistémicas de Cierre del Capítulo"),
    ("Note Epistemiche di Chiusura",   "Notas Epistémicas de Cierre"),
    ("Apertura della Parte",           "Apertura de la Parte"),
    ("Sintesi del Capitolo",           "Síntesis del Capítulo"),
    ("Definizione Strutturale",        "Definición Estructural"),
    ("Criteri DEQ",                    "Criterios DEQ"),

    # ── Termini DEQ² ──
    ("Egemone Decoerente",            "Hegemón Decoherente"),
    ("Rigido Sincronizzato",          "Rígido Sincronizado"),
    ("Bilanciere Quantistico",        "Balanza Cuántica"),
    ("Solitone",                      "Solitón"),
    ("parametro d'ordine",            "parámetro de orden"),
    ("transizione di fase",           "transición de fase"),
    ("coerenza di fase",              "coherencia de fase"),
    ("soglia critica",                "umbral crítico"),
    ("stato critico",                 "estado crítico"),
    ("regime sub-critico",            "régimen subcrítico"),
    ("regime super-critico",          "régimen supercrítico"),
    ("decoerenza",                    "decoherencia"),
    ("sincronizzazione",              "sincronización"),
    ("accoppiamento",                 "acoplamiento"),
    ("forza di accoppiamento",        "fuerza de acoplamiento"),
    ("campo medio",                   "campo medio"),
    ("trasposizione di scala",        "transposición de escala"),
    ("invarianza di scala",           "invarianza de escala"),
    ("microfondazione",               "microfundación"),
    ("microfondazioni",               "microfundaciones"),
    ("Folk Theorem Discorsivo",       "Teorema Folk Discursivo"),
    ("Folk Theorem della Geometria",  "Teorema Folk de la Geometría"),
    ("Folk Theorem",                  "Teorema Folk"),
    ("equilibrio separante bayesiano", "equilibrio separante bayesiano"),
    ("equilibrio di Nash perfetto nei sottogiochi", "equilibrio de Nash perfecto en subjuegos"),
    ("equilibrio di Nash",            "equilibrio de Nash"),
    ("ottimo paretiano",              "óptimo de Pareto"),
    ("Barbarie Tecnologica",          "Barbarie Tecnológica"),
    ("fattore di erosione",           "factor de erosión"),
    ("effetto boomerang",             "efecto boomerang"),
    ("massa comunicativa",            "masa comunicativa"),
    ("qualità etica",                 "calidad ética"),
    ("resistenza critica",            "resistencia crítica"),
    ("funzione predittiva",           "función predictiva"),
    ("legge predittiva",              "ley predictiva"),
    ("legge micro fondamentale",      "ley micro fundamental"),
    ("payoff istantaneo",             "payoff instantáneo"),
    ("frequenza naturale",            "frecuencia natural"),

    # ── Topografia ──
    ("Spazio Discorsivo",             "Espacio Discursivo"),
    ("spazio discorsivo",             "espacio discursivo"),
    ("Vettore Etico",                 "Vector Ético"),
    ("vettore etico",                 "vector ético"),
    ("coerenza formale",              "coherencia formal"),
    ("precisione tecnica",            "precisión técnica"),
    ("complessità dialettica",        "complejidad dialéctica"),
    ("amplificazione algoritmica",    "amplificación algorítmica"),
    ("saturazione",                   "saturación"),
    ("impatto atteso",                "impacto esperado"),
    ("propaganda efficace",           "propaganda eficaz"),
    ("propaganda inerte",             "propaganda inerte"),
    ("agire comunicativo habermasiano", "acción comunicativa habermasiana"),
    ("Scuola di Francoforte",         "Escuela de Fráncfort"),
    ("industria culturale",           "industria cultural"),
    ("colonizzazione del mondo della vita", "colonización del mundo de la vida"),
    ("rendimenti decrescenti",        "rendimientos decrecientes"),

    # ── Geometria ──
    ("coesione interna",              "cohesión interna"),
    ("capacità materiale",            "capacidad material"),
    ("legittimità etico-discorsiva",  "legitimidad ético-discursiva"),
    ("fattore di sconto",             "factor de descuento"),
    ("orizzonte temporale",           "horizonte temporal"),
    ("volatilità stocastica",         "volatilidad estocástica"),
    ("coefficiente di disimpegno morale", "coeficiente de desvinculación moral"),
    ("biforcazione",                  "bifurcación"),
    ("punto di biforcazione",         "punto de bifurcación"),
    ("stabilità strutturale",         "estabilidad estructural"),
    ("collasso",                      "colapso"),
    ("collasso sistemico",            "colapso sistémico"),
    ("transizione egemonica",         "transición hegemónica"),
    ("ciclo egemonico",               "ciclo hegemónico"),

    # ── Kuramoto ──
    ("parametro d'ordine complesso",  "parámetro de orden complejo"),
    ("riduzione di campo medio",      "reducción de campo medio"),
    ("sincronizzazione parziale",     "sincronización parcial"),
    ("sincronizzazione piena",        "sincronización plena"),
    ("decoerenza completa",           "decoherencia completa"),
    ("grandezza locale",              "magnitud local"),
    ("quantità sistemica derivata",   "cantidad sistémica derivada"),

    # ── Antifragilità ──
    ("convessità positiva",           "convexidad positiva"),
    ("concavità negativa",            "concavidad negativa"),
    ("fragilità",                     "fragilidad"),
    ("antifragilità",                 "antifragilidad"),
    ("antifragile",                   "antifrágil"),
    ("robusto",                       "robusto"),
    ("resiliente",                    "resiliente"),
    ("resilienza",                    "resiliencia"),
    ("indice di antifragilità",       "índice de antifragilidad"),
    ("involuzione",                   "involución"),
    ("pressione demografica",         "presión demográfica"),

    # ── Attori ──
    ("Estado Logístico",              "Estado Logístico"),
    ("Phi-engine",                    "Phi-engine"),
    ("motore di coerenza",            "motor de coherencia"),
    ("iper-estensione",               "hiperextensión"),
    ("polarizzazione affettiva",      "polarización afectiva"),
    ("legittimità",                   "legitimidad"),
    ("rete di coordinamento",         "red de coordinación"),

    # ── Predizioni ──
    ("predizione rischiosa",          "predicción arriesgada"),
    ("predizioni rischiose",          "predicciones arriesgadas"),
    ("predizione datata",             "predicción fechada"),
    ("soglia numerica",               "umbral numérico"),
    ("fonte dati pubblica",           "fuente de datos pública"),
    ("falsificazione",                "falsificación"),
    ("falsificabilità",               "falsificabilidad"),
    ("pre-registrazione",             "pre-registro"),
    ("aggiornamento bayesiano",       "actualización bayesiana"),
    ("probabilità soggettiva",        "probabilidad subjetiva"),
    ("correzione locale",             "corrección local"),
    ("riformulazione strutturale",    "reformulación estructural"),
    ("aggiustamento parametrico",     "ajuste paramétrico"),
    ("strutturale",                   "estructural"),
    ("locale",                        "local"),
    ("condizionale",                  "condicional"),
    ("pendente",                      "pendiente"),

    # ── Dashboard SPC ──
    ("Dashboard SPC-DEQ",             "Dashboard SPC-DEQ"),
    ("pannello bivariato",            "panel bivariado"),
    ("pannello aggregato",            "panel agregado"),
    ("regola WE-DEQ",                 "regla WE-DEQ"),
    ("causa speciale",                "causa especial"),
    ("fuori-limite",                  "fuera de control"),
    ("indice di capacità",            "índice de capacidad"),
    ("limiti di controllo",           "límites de control"),
    ("limite superiore",              "límite superior"),
    ("limite inferiore",              "límite inferior"),

    # ── Struttura libro ──
    ("Parte I",   "Parte I"),
    ("Parte II",  "Parte II"),
    ("Parte III", "Parte III"),
    ("Parte IV",  "Parte IV"),
    ("Parte V",   "Parte V"),
    ("Cap. 1",  "Cap.~1"),
    ("Cap. 2",  "Cap.~2"),
    ("Cap. 3",  "Cap.~3"),
    ("Cap. 4",  "Cap.~4"),
    ("Cap. 5",  "Cap.~5"),
    ("Cap. 6",  "Cap.~6"),
    ("Cap. 7",  "Cap.~7"),
    ("Cap. 8",  "Cap.~8"),
    ("Cap. 9",  "Cap.~9"),
    ("Cap. 10", "Cap.~10"),
    ("Cap. 11", "Cap.~11"),
    ("Cap. 12", "Cap.~12"),
    ("Cap. 13", "Cap.~13"),
    ("App. A",  "Ap.~A"),
    ("App. B",  "Ap.~B"),
    ("App. C",  "Ap.~C"),
    ("App. D",  "Ap.~D"),
    ("capitolo", "capítulo"),
    ("Capitolo", "Capítulo"),
    ("appendice", "apéndice"),
    ("Appendice", "Apéndice"),
    ("tabella",  "tabla"),
    ("Tabella",  "Tabla"),
    ("sezione",  "sección"),
    ("il lettore", "el lector"),
    ("nel testo",  "en el texto"),

    # ── Parole connettive italiane → spagnolo ──
    ("dove:",    "donde:"),
    ("dove ",    "donde "),
    ("quindi",   "por lo tanto"),
    ("dunque",   "por lo tanto"),
    ("dunque:",  "por lo tanto:"),
    ("pertanto", "así"),
    ("inoltre",  "además"),
    ("tuttavia", "sin embargo"),
    ("invece",   "en cambio"),
    ("mentre",   "mientras"),
    ("poiché",   "dado que"),
    ("perché",   "porque"),
    ("sebbene",  "aunque"),
    ("nonostante", "a pesar de"),
    ("ovvero",   "es decir"),
    ("ossia",    "a saber"),
    ("cioè",     "es decir,"),
    ("ad esempio", "por ejemplo"),
    ("per esempio", "por ejemplo"),
    ("in particolare", "en particular"),
    ("in generale", "en general"),
    ("in sintesi", "en resumen"),
    ("in conclusione", "en conclusión"),
    ("si noti che", "nótese que"),
    ("si osserva che", "se observa que"),
    ("è possibile", "es posible"),
    ("è necessario", "es necesario"),
    ("è sufficiente", "es suficiente"),
    ("è importante", "es importante"),
    ("abbiamo",  "tenemos"),
    ("otteniamo", "obtenemos"),
    ("deriva",   "se deriva"),
    ("segue",    "se sigue"),
    ("si dimostra", "se puede demostrar"),
    ("si può",   "se puede"),
    ("da cui",   "de donde"),
    ("per cui",  "por lo cual"),
    ("tale che", "tal que"),
    ("così",     "así"),
    ("allora",   "entonces"),
    ("infine",   "finalmente"),
    ("prima",    "primero"),
    ("poi",      "luego"),
    ("dopo",     "después"),
    ("tramite",  "mediante"),
    ("mediante", "mediante"),
    ("attraverso", "a través de"),
    ("rispetto a", "con respecto a"),
    ("in termini di", "en términos de"),
    ("in funzione di", "en función de"),
    ("a partire da", "a partir de"),
    ("a causa di", "debido a"),
    ("grazie a",  "gracias a"),
    ("al fine di", "con el fin de"),
    ("al contrario", "por el contrario"),
    ("d'altra parte", "por otra parte"),
    ("da un lato", "por un lado"),
    ("dall'altro", "por el otro"),

    # ── Epistemic labels ──
    ("Affermazione",  "Afirmación"),
    ("affermazione",  "afirmación"),
    ("Riferimento",   "Referencia"),
    ("riferimento",   "referencia"),
    ("Status",        "Estado"),
    ("definizione operativa", "definición operativa"),
    ("stima empirica su corpus", "estimación empírica sobre corpus"),
    ("giustificata teoricamente", "justificado teóricamente"),
    ("derivato dai payoff", "derivado de los payoffs"),
    ("verificato",    "verificado"),
    ("ipotesi strutturale", "hipótesis estructural"),
    ("ipotesi operativa", "hipótesis operativa"),
    ("ipotesi",       "hipótesis"),
    ("dimostrazione", "demostración"),
    ("dimostrato",    "demostrado"),
    ("congettura",    "conjetura"),
    ("teorema",       "teorema"),
    ("lemma",         "lema"),
    ("corollario",    "corolario"),
    ("proposizione",  "proposición"),
    ("definizione",   "definición"),
    ("osservazione",  "observación"),
    ("problema aperto", "problema abierto"),

    # ── Termini paese ──
    ("gli Stati Uniti", "los Estados Unidos"),
    ("Stati Uniti",  "Estados Unidos"),
    ("Cina",         "China"),
    ("cinese",       "chino"),
    ("brasiliano",   "brasileño"),
    ("brasiliana",   "brasileña"),
    ("Brasile",      "Brasil"),
    ("Europa",       "Europa"),
    ("europeo",      "europeo"),
    ("Russia",       "Rusia"),
    ("russo",        "ruso"),
    ("India",        "India"),
    ("BRICS",        "BRICS"),
    ("FMI",          "FMI"),
    ("Banca Mondiale", "Banco Mundial"),
    ("Nazioni Unite", "Naciones Unidas"),

    # ── Termini tecnici vari ──
    ("misurazione",  "medición"),
    ("misurabile",   "medible"),
    ("operativo",    "operativo"),
    ("formale",      "formal"),
    ("formalismo",   "formalismo"),
    ("variabile",    "variable"),
    ("variabili",    "variables"),
    ("parametro",    "parámetro"),
    ("parametri",    "parámetros"),
    ("equazione",    "ecuación"),
    ("equazioni",    "ecuaciones"),
    ("verifica",     "verificación"),
    ("nota",         "nota"),
    ("esempio",      "ejemplo"),

    # ── Frase tabelle ──
    ("stessa soglia",   "mismo umbral"),
    ("microstruttura",  "microestructura"),
    ("Microstruttura",  "Microestructura"),
    ("emerge",          "emerge"),
]

def translate(tex: str) -> str:
    math_pattern = re.compile(
        r'(\\\[[\s\S]*?\\\]'
        r'|\$\$[\s\S]*?\$\$'
        r'|\\\([\s\S]*?\\\)'
        r'|\$[^\$\n]+?\$)'
    )
    parts = math_pattern.split(tex)
    result = []
    for i, part in enumerate(parts):
        in_math = (i % 2 == 1)
        if not in_math:
            for it, es in TERMS:
                part = part.replace(it, es)
        result.append(part)
    return ''.join(result)

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
        print("[OK] Tutti i file tradotti in ES.")
    elif len(sys.argv) >= 2:
        src_name = sys.argv[1]
        dst_name = FILE_MAP.get(src_name, src_name.replace('.tex', '-es.tex'))
        DST.mkdir(exist_ok=True)
        translate_file(src_name, dst_name)
    else:
        print("Uso: python translate_it_es.py [file.tex | --all]")

if __name__ == '__main__':
    main()
