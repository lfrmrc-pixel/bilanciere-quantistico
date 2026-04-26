-- strip-math-labels.lua
-- Rimuove \label{}, \nonumber e whitespace extra dalle equazioni
-- prima della conversione MathML (pandoc --mathml per EPUB).
-- Permette di usare lo stesso sorgente LaTeX per stampa ed ebook.
function Math(el)
  el.text = el.text:gsub("\\label%b{}", "")
  el.text = el.text:gsub("\\nonumber", "")
  el.text = el.text:gsub("^%s+", ""):gsub("%s+$", "")
  return el
end
