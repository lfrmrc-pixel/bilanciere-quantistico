#!/usr/bin/env python3
"""
translate_it_pt.py — Tradução semi-automática IT→PT dos capítulos LaTeX DEQ²
Substitui terminologia técnica e estrutural; o texto narrativo requer revisão.

Uso:
    python translate_it_pt.py --all   # traduz todos
"""

import re
import sys
from pathlib import Path

SRC = Path("C:/Users/Utente/bilanciere-quantistico/chapters-it")
DST = Path("C:/Users/Utente/bilanciere-quantistico/chapters-pt")

FILE_MAP = {
    "01-topografia.tex":              "01-topografia.tex",
    "02-geometria.tex":               "02-geometria.tex",
    "03-equazione-unificata.tex":     "03-equacao-unificada.tex",
    "04-forma-sistemica.tex":         "04-forma-sistemica.tex",
    "05-quattro-variabili.tex":       "05-quatro-variaveis.tex",
    "06-solitone-musk.tex":           "06-soliton-musk.tex",
    "07-egemone-decoerente.tex":      "07-hegemon-decoerente.tex",
    "08-rigido-sincronizzato.tex":    "08-rigido-sincronizado.tex",
    "09-bilanciere-brasile.tex":      "09-balanca-brasil.tex",
    "10-dashboard-spc.tex":          "10-dashboard-spc.tex",
    "11-predizioni-datate.tex":       "11-predicoes-datadas.tex",
    "12-strategie-antifragili.tex":   "12-estrategias-antifrageis.tex",
    "13-conclusioni.tex":             "13-conclusoes.tex",
    "AppA-derivazione-formale.tex":   "AppA-derivacao-formal.tex",
    "AppB-calibrazione-sigma.tex":    "AppB-calibracao-sigma.tex",
    "AppC-protocolli-misurazione.tex": "AppC-protocolos-medicao.tex",
    "AppD-dialogo-tradizioni.tex":    "AppD-dialogo-tradicoes.tex",
}

TERMS = [
    # ── Títulos capítulos e apêndices ──
    ("La Topografia: l'Apparato Micro",           "A Topografia: o Aparato Micro"),
    ("La Geometria: l'Apparato Macro",            "A Geometria: o Aparato Macro"),
    ("L'Equazione Unificata:",                    "A Equação Unificada:"),
    ("La Forma Sistemica:",                       "A Forma Sistêmica:"),
    ("Le Quattro Variabili Strutturali in Quadro Coerente", "As Quatro Variáveis Estruturais em Quadro Coerente"),
    ("Il Solitone (Musk):",                       "O Soliton (Musk):"),
    ("L'Egemone Decoerente (USA):",               "O Hegemon Decoerente (EUA):"),
    ("Il Rigido Sincronizzato (Cina):",           "O Rígido Sincronizado (China):"),
    ("Il Bilanciere Quantistico (Brasile):",      "A Balança Quântica (Brasil):"),
    ("Scenari Quantizzati e Dashboard SPC-DEQ",  "Cenários Quantizados e Dashboard SPC-DEQ"),
    ("Predizioni Rischiose Datate:",              "Predições Arriscadas Datadas:"),
    ("Cosa Fare: Strategie Antifragili",          "O Que Fazer: Estratégias Antifrágeis"),
    ("Conclusioni e Ricerca Futura",              "Conclusões e Pesquisa Futura"),
    ("Derivazione Formale Completa",              "Derivação Formal Completa"),
    ("Calibrazione Empirica di",                  "Calibração Empírica de"),
    ("Protocolli di Misurazione dei Parametri DEQ", "Protocolos de Medição dos Parâmetros DEQ²"),
    ("Dialogo Testuale con le Tradizioni",        "Diálogo Textual com as Tradições"),

    # ── Seções típicas ──
    ("Argomento portante:",            "Argumento central:"),
    ("Note Epistemiche di Chiusura Capitolo", "Notas Epistêmicas de Encerramento do Capítulo"),
    ("Note Epistemiche di Chiusura",   "Notas Epistêmicas de Encerramento"),
    ("Apertura della Parte",           "Abertura da Parte"),
    ("Sintesi del Capitolo",           "Síntese do Capítulo"),
    ("Definizione Strutturale",        "Definição Estrutural"),
    ("Criteri DEQ",                    "Critérios DEQ"),

    # ── Termos DEQ² ──
    ("Egemone Decoerente",            "Hegemon Decoerente"),
    ("Rigido Sincronizzato",          "Rígido Sincronizado"),
    ("Bilanciere Quantistico",        "Balança Quântica"),
    ("Solitone",                      "Soliton"),
    ("parametro d'ordine",            "parâmetro de ordem"),
    ("transizione di fase",           "transição de fase"),
    ("coerenza di fase",              "coerência de fase"),
    ("soglia critica",                "limiar crítico"),
    ("stato critico",                 "estado crítico"),
    ("regime sub-critico",            "regime subcrítico"),
    ("regime super-critico",          "regime supercrítico"),
    ("decoerenza",                    "decoerência"),
    ("sincronizzazione",              "sincronização"),
    ("accoppiamento",                 "acoplamento"),
    ("forza di accoppiamento",        "força de acoplamento"),
    ("campo medio",                   "campo médio"),
    ("trasposizione di scala",        "transposição de escala"),
    ("invarianza di scala",           "invariância de escala"),
    ("microfondazione",               "microfundação"),
    ("microfondazioni",               "microfundações"),
    ("Folk Theorem Discorsivo",       "Teorema Folk Discursivo"),
    ("Folk Theorem della Geometria",  "Teorema Folk da Geometria"),
    ("Folk Theorem",                  "Teorema Folk"),
    ("equilibrio separante bayesiano", "equilíbrio separante bayesiano"),
    ("equilibrio di Nash perfetto nei sottogiochi", "equilíbrio de Nash perfeito em subjogos"),
    ("equilibrio di Nash",            "equilíbrio de Nash"),
    ("ottimo paretiano",              "ótimo de Pareto"),
    ("Barbarie Tecnologica",          "Barbárie Tecnológica"),
    ("fattore di erosione",           "fator de erosão"),
    ("effetto boomerang",             "efeito bumerangue"),
    ("massa comunicativa",            "massa comunicativa"),
    ("qualità etica",                 "qualidade ética"),
    ("resistenza critica",            "resistência crítica"),
    ("funzione predittiva",           "função preditiva"),
    ("legge predittiva",              "lei preditiva"),
    ("legge micro fondamentale",      "lei micro fundamental"),
    ("payoff istantaneo",             "payoff instantâneo"),
    ("frequenza naturale",            "frequência natural"),

    # ── Topografia ──
    ("Spazio Discorsivo",             "Espaço Discursivo"),
    ("spazio discorsivo",             "espaço discursivo"),
    ("Vettore Etico",                 "Vetor Ético"),
    ("vettore etico",                 "vetor ético"),
    ("coerenza formale",              "coerência formal"),
    ("precisione tecnica",            "precisão técnica"),
    ("complessità dialettica",        "complexidade dialética"),
    ("amplificazione algoritmica",    "amplificação algorítmica"),
    ("saturazione",                   "saturação"),
    ("impatto atteso",                "impacto esperado"),
    ("propaganda efficace",           "propaganda eficaz"),
    ("propaganda inerte",             "propaganda inerte"),
    ("agire comunicativo habermasiano", "ação comunicativa habermasiana"),
    ("Scuola di Francoforte",         "Escola de Frankfurt"),
    ("industria culturale",           "indústria cultural"),
    ("colonizzazione del mondo della vita", "colonização do mundo da vida"),
    ("rendimenti decrescenti",        "retornos decrescentes"),

    # ── Geometria ──
    ("coesione interna",              "coesão interna"),
    ("capacità materiale",            "capacidade material"),
    ("legittimità etico-discorsiva",  "legitimidade ético-discursiva"),
    ("fattore di sconto",             "fator de desconto"),
    ("orizzonte temporale",           "horizonte temporal"),
    ("volatilità stocastica",         "volatilidade estocástica"),
    ("coefficiente di disimpegno morale", "coeficiente de desengajamento moral"),
    ("biforcazione",                  "bifurcação"),
    ("punto di biforcazione",         "ponto de bifurcação"),
    ("stabilità strutturale",         "estabilidade estrutural"),
    ("collasso",                      "colapso"),
    ("collasso sistemico",            "colapso sistêmico"),
    ("transizione egemonica",         "transição hegemônica"),
    ("ciclo egemonico",               "ciclo hegemônico"),

    # ── Kuramoto ──
    ("parametro d'ordine complesso",  "parâmetro de ordem complexo"),
    ("riduzione di campo medio",      "redução de campo médio"),
    ("sincronizzazione parziale",     "sincronização parcial"),
    ("sincronizzazione piena",        "sincronização plena"),
    ("decoerenza completa",           "decoerência completa"),
    ("grandezza locale",              "grandeza local"),
    ("quantità sistemica derivata",   "quantidade sistêmica derivada"),

    # ── Antifragilidade ──
    ("convessità positiva",           "convexidade positiva"),
    ("concavità negativa",            "concavidade negativa"),
    ("fragilità",                     "fragilidade"),
    ("antifragilità",                 "antifragilidade"),
    ("antifragile",                   "antifrágil"),
    ("robusto",                       "robusto"),
    ("resiliente",                    "resiliente"),
    ("resilienza",                    "resiliência"),
    ("indice di antifragilità",       "índice de antifragilidade"),
    ("involuzione",                   "involução"),
    ("pressione demografica",         "pressão demográfica"),

    # ── Atores ──
    ("Estado Logístico",              "Estado Logístico"),
    ("Phi-engine",                    "Phi-engine"),
    ("motore di coerenza",            "motor de coerência"),
    ("iper-estensione",               "hiperextensão"),
    ("polarizzazione affettiva",      "polarização afetiva"),
    ("legittimità",                   "legitimidade"),
    ("rete di coordinamento",         "rede de coordenação"),

    # ── Predições ──
    ("predizione rischiosa",          "predição arriscada"),
    ("predizioni rischiose",          "predições arriscadas"),
    ("predizione datata",             "predição datada"),
    ("soglia numerica",               "limiar numérico"),
    ("fonte dati pubblica",           "fonte de dados pública"),
    ("falsificazione",                "falsificação"),
    ("falsificabilità",               "falsificabilidade"),
    ("pre-registrazione",             "pré-registro"),
    ("aggiornamento bayesiano",       "atualização bayesiana"),
    ("probabilità soggettiva",        "probabilidade subjetiva"),
    ("correzione locale",             "correção local"),
    ("riformulazione strutturale",    "reformulação estrutural"),
    ("aggiustamento parametrico",     "ajuste paramétrico"),
    ("strutturale",                   "estrutural"),
    ("locale",                        "local"),
    ("condizionale",                  "condicional"),
    ("pendente",                      "pendente"),

    # ── Dashboard SPC ──
    ("pannello bivariato",            "painel bivariado"),
    ("pannello aggregato",            "painel agregado"),
    ("regola WE-DEQ",                 "regra WE-DEQ"),
    ("causa speciale",                "causa especial"),
    ("fuori-limite",                  "fora de controle"),
    ("indice di capacità",            "índice de capacidade"),
    ("limiti di controllo",           "limites de controle"),
    ("limite superiore",              "limite superior"),
    ("limite inferiore",              "limite inferior"),

    # ── Estrutura livro ──
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
    ("appendice", "apêndice"),
    ("Appendice", "Apêndice"),
    ("tabella",  "tabela"),
    ("Tabella",  "Tabela"),
    ("sezione",  "seção"),
    ("il lettore", "o leitor"),
    ("nel testo",  "no texto"),

    # ── Palavras conectivas IT → PT ──
    ("dove:",    "onde:"),
    ("dove ",    "onde "),
    ("quindi",   "portanto"),
    ("dunque",   "portanto"),
    ("dunque:",  "portanto:"),
    ("pertanto", "assim"),
    ("inoltre",  "além disso"),
    ("tuttavia", "no entanto"),
    ("invece",   "em vez disso"),
    ("mentre",   "enquanto"),
    ("poiché",   "uma vez que"),
    ("perché",   "porque"),
    ("sebbene",  "embora"),
    ("nonostante", "apesar de"),
    ("ovvero",   "ou seja"),
    ("ossia",    "a saber"),
    ("cioè",     "isto é,"),
    ("ad esempio", "por exemplo"),
    ("per esempio", "por exemplo"),
    ("in particolare", "em particular"),
    ("in generale", "em geral"),
    ("in sintesi", "em síntese"),
    ("in conclusione", "em conclusão"),
    ("si noti che", "note-se que"),
    ("si osserva che", "observa-se que"),
    ("è possibile", "é possível"),
    ("è necessario", "é necessário"),
    ("è sufficiente", "é suficiente"),
    ("è importante", "é importante"),
    ("abbiamo",  "temos"),
    ("otteniamo", "obtemos"),
    ("deriva",   "deriva"),
    ("segue",    "segue"),
    ("si dimostra", "pode-se demonstrar"),
    ("si può",   "pode-se"),
    ("da cui",   "do qual"),
    ("per cui",  "pelo qual"),
    ("tale che", "tal que"),
    ("così",     "assim"),
    ("allora",   "então"),
    ("infine",   "por fim"),
    ("prima",    "primeiro"),
    ("poi",      "depois"),
    ("dopo",     "após"),
    ("tramite",  "por meio de"),
    ("mediante", "mediante"),
    ("attraverso", "através de"),
    ("rispetto a", "com relação a"),
    ("in termini di", "em termos de"),
    ("in funzione di", "em função de"),
    ("a partire da", "a partir de"),
    ("a causa di", "devido a"),
    ("grazie a",  "graças a"),
    ("al fine di", "a fim de"),
    ("al contrario", "pelo contrário"),
    ("d'altra parte", "por outro lado"),
    ("da un lato", "por um lado"),
    ("dall'altro", "pelo outro"),

    # ── Labels epistêmicas ──
    ("Affermazione",  "Afirmação"),
    ("affermazione",  "afirmação"),
    ("Riferimento",   "Referência"),
    ("riferimento",   "referência"),
    ("definizione operativa", "definição operativa"),
    ("stima empirica su corpus", "estimativa empírica sobre corpus"),
    ("giustificata teoricamente", "justificado teoricamente"),
    ("derivato dai payoff", "derivado dos payoffs"),
    ("verificato",    "verificado"),
    ("ipotesi strutturale", "hipótese estrutural"),
    ("ipotesi operativa", "hipótese operativa"),
    ("ipotesi",       "hipótese"),
    ("dimostrazione", "demonstração"),
    ("dimostrato",    "demonstrado"),
    ("congettura",    "conjetura"),
    ("teorema",       "teorema"),
    ("lemma",         "lema"),
    ("corollario",    "corolário"),
    ("proposizione",  "proposição"),
    ("definizione",   "definição"),
    ("osservazione",  "observação"),
    ("problema aperto", "problema aberto"),

    # ── Países ──
    ("gli Stati Uniti", "os Estados Unidos"),
    ("Stati Uniti",  "Estados Unidos"),
    ("Cina",         "China"),
    ("cinese",       "chinês"),
    ("brasiliano",   "brasileiro"),
    ("brasiliana",   "brasileira"),
    ("Brasile",      "Brasil"),
    ("Europa",       "Europa"),
    ("europeo",      "europeu"),
    ("Russia",       "Rússia"),
    ("russo",        "russo"),
    ("India",        "Índia"),
    ("BRICS",        "BRICS"),
    ("FMI",          "FMI"),
    ("Banca Mondiale", "Banco Mundial"),
    ("Nazioni Unite", "Nações Unidas"),

    # ── Termos técnicos ──
    ("misurazione",  "medição"),
    ("misurabile",   "mensurável"),
    ("operativo",    "operativo"),
    ("formalismo",   "formalismo"),
    ("variabile",    "variável"),
    ("variabili",    "variáveis"),
    ("parametro",    "parâmetro"),
    ("parametri",    "parâmetros"),
    ("equazione",    "equação"),
    ("equazioni",    "equações"),
    ("verifica",     "verificação"),
    ("nota",         "nota"),
    ("esempio",      "exemplo"),

    # ── Tabelas ──
    ("stessa soglia",   "mesmo limiar"),
    ("microstruttura",  "microestrutura"),
    ("Microstruttura",  "Microestrutura"),
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
            for it, pt in TERMS:
                part = part.replace(it, pt)
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
        print("[OK] Tutti i file tradotti in PT.")
    elif len(sys.argv) >= 2:
        src_name = sys.argv[1]
        dst_name = FILE_MAP.get(src_name, src_name.replace('.tex', '-pt.tex'))
        DST.mkdir(exist_ok=True)
        translate_file(src_name, dst_name)
    else:
        print("Uso: python translate_it_pt.py [file.tex | --all]")

if __name__ == '__main__':
    main()
