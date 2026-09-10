"""Convert the supplied sources to static, accessible HTML without rewriting DOCX text."""
from pathlib import Path
import json, re, shutil, hashlib, html
from zipfile import ZipFile
import mammoth, markdown
from bs4 import BeautifulSoup
from lxml import etree

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / 'sources'
OUT = ROOT / 'public'
OUT.mkdir(exist_ok=True)
(OUT / 'pliki').mkdir(exist_ok=True)
NS = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
titles = ['Wprowadzenie do innowacji', 'Rozwiązywanie problemów i praca zespołowa', 'Narzędzia cyfrowe dla innowacji', 'Zrównoważony rozwój i odpowiedzialność', 'Przedsiębiorczość i intraprzedsiębiorczość', 'Komunikacja i zarządzanie zmianą', 'Osobiste kompetencje przyszłości']
briefs = [
 'Dostrzeganie codziennych usprawnień i korzyści dla pracowników oraz firmy.',
 'Wspólna analiza przyczyn, metoda 5 × dlaczego i współpraca w zespole.',
 'Dobór narzędzi do komunikacji, planowania i usprawniania procesów.',
 'People, Planet, Profit: zielony audyt i odpowiedzialne decyzje w zawodzie.',
 'Od pomysłu do planu: potrzeby klientów, zasoby, ryzyko i inicjatywa pracownicza.',
 'Wyjaśnianie zmian, aktywne słuchanie i odpowiadanie na obawy zespołu.',
 'Samoocena, adaptacyjność i osobisty plan dalszego uczenia się.'
]
mdfiles = sorted(SRC.glob('*.md'))
links = {p.name: ('program.html' if p.name.startswith('00') else 'zrodla.html' if p.name.startswith('08') else f'modul-{int(p.name[:2])}.html') for p in mdfiles}
file_records = []
for i, p in enumerate(sorted(SRC.iterdir()), 1):
    dest = f'zrodlo-{i:02}{p.suffix}'
    shutil.copy2(p, OUT / 'pliki' / dest)
    file_records.append({'name': p.name, 'url': 'pliki/' + dest, 'bytes': p.stat().st_size, 'sha256': hashlib.sha256(p.read_bytes()).hexdigest()})
file_map = {x['name']: x['url'] for x in file_records}

def nav(active):
    items = [('index.html','Przewodnik'),('program.html','Program'),('wdrozenie.html','Wdrożenie w ZSZ5'),('scenariusze.html','Scenariusze 1–3'),('omowienie.html','Omówienie po przejrzeniu'),('biblioteka.html','Dokumenty')]
    return ''.join(f'<a href="{u}"'+(' aria-current="page"' if u==active else '')+f'>{t}</a>' for u,t in items)

def enhance(body):
    soup=BeautifulSoup(body,'html.parser')
    for a in soup.find_all('a',href=True):
        href=a['href']
        if href in links: a['href']=links[href]
        elif href.startswith(('file:', 'javascript:')): a.unwrap()
    for code in soup.find_all('code'):
        text=code.get_text()
        if text in links:
            a=soup.new_tag('a',href=links[text]); a.string=text; code.replace_with(a)
    for table in soup.find_all('table'):
        wrap=soup.new_tag('div',attrs={'class':'table-scroll','tabindex':'0','role':'region','aria-label':'Tabela — przewiń poziomo w razie potrzeby'})
        table.wrap(wrap)
    toc=[]
    for i, h in enumerate(soup.find_all(['h2','h3'])):
        h['id']=f'sekcja-{i+1}'
        if h.name=='h2': toc.append((h['id'],h.get_text()))
    return str(soup),toc

def page(slug,title,body,eyebrow='WIN4SMEs · WP4.1 / A4.1',intro='',note='',lang='pl',pager=''):
    body,toc=enhance(body)
    contents = ('<details class="toc" open><summary>Na tej stronie</summary><nav aria-label="Spis treści strony">'+''.join(f'<a href="#{i}">{html.escape(t)}</a>' for i,t in toc)+'</nav></details>') if toc else ''
    rendered=f'''<!doctype html>
<html lang="pl"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="description" content="{html.escape(intro or title,quote=True)}"><meta name="theme-color" content="#153e41"><title>{html.escape(title)} — WIN4SMEs</title><link rel="icon" href="favicon.svg" type="image/svg+xml"><link rel="stylesheet" href="style.css"></head>
<body><a class="skip" href="#tresc">Przejdź do treści</a><header class="masthead"><a class="brand" href="index.html">WIN<span>4</span>SMEs<span class="brand-sub">Innowacje w miejscu pracy</span></a><nav aria-label="Nawigacja główna">{nav(slug)}</nav></header>
<main id="tresc"><div class="page-heading"><p class="eyebrow">{eyebrow}</p><h1>{html.escape(title)}</h1>{f'<p class="lead">{intro}</p>' if intro else ''}</div>{f'<aside class="notice">{note}</aside>' if note else ''}<div class="reading-layout"><article class="prose" lang="{lang}">{body}{pager}</article>{contents}</div></main>
<footer><div><strong>WIN4SMEs</strong><p>Workplace Innovation &amp; Future Skills<br>Materiały programu i adaptacja ZSZ5 we Wrocławiu</p></div><div><a href="biblioteka.html">Dokumenty źródłowe</a><a href="zrodla.html">Bibliografia i uwagi</a><p>Opracowanie internetowe · wrzesień 2026</p></div><p class="funding">Funded by the European Union. Views and opinions expressed are however those of the author(s) only and do not necessarily reflect those of the European Union or the European Education and Culture Executive Agency (EACEA). Neither the European Union nor EACEA can be held responsible for them.</p></footer></body></html>'''
    (OUT/slug).write_text(rendered)

def md(text):
    return markdown.markdown(text, extensions=['tables','fenced_code','sane_lists'])

def readmd(p):
    t=p.read_text();t=re.sub(r'^# .+\n','',t,count=1)
    return md(t)

overview='''<p>Innowacja w miejscu pracy zaczyna się od zauważenia, co można zrobić lepiej. Program łączy tę obserwację z pracą zespołową, narzędziami cyfrowymi, odpowiedzialnością i rozwojem własnych kompetencji.</p>
<div class="entry-pair"><a href="scenariusze.html"><span class="label">DLA PROWADZĄCYCH ZAJĘCIA</span><strong>Trzy pełne scenariusze szkolne</strong><span>Treść DOCX bez zmian, wraz z tabelami i kartą audytu. <b aria-hidden="true">↗</b></span></a><a href="wdrozenie.html"><span class="label">ORGANIZACJA W SZKOLE</span><strong>Jak wdrożyć program w ZSZ5</strong><span>Powiązania tematów, czas zajęć i przygotowanie materiałów. <b aria-hidden="true">↗</b></span></a></div>
<h2>Siedem modułów programu</h2><p>Każde opracowanie zawiera cele, kontekst, przebieg zajęć, ćwiczenia, metody oceny i kartę pracy. Moduły można dobierać do potrzeb klasy i branży.</p><ol class="module-list">'''
for i,(t,b) in enumerate(zip(titles,briefs),1):
    overview+=f'<li><a href="modul-{i}.html"><span class="module-number">0{i}</span><span><strong>{t}</strong><span>{b}</span></span><b aria-hidden="true">↗</b></a></li>'
overview+='''</ol><h2>Jak czytać tę dokumentację</h2><p><strong>Program</strong> obejmuje siedem tematów dla kształcenia zawodowego na poziomach EQF 3–4. <strong>Wdrożenie w ZSZ5</strong> wyjaśnia szkolny wybór pięciu tematów. <strong>Scenariusze 1–3</strong> zawierają pełne teksty przekazanych dokumentów, z zachowaniem ich numeracji i brzmienia.</p><p>Szkolny moduł 3 dotyczy zrównoważonego rozwoju — odpowiada modułowi 4 programu. Narzędzia cyfrowe są modułem 3 wyłącznie w programie siedmiomodułowym.</p><p>W bibliotece dostępne są wszystkie 15 plików źródłowych: program w DOCX i PDF, dokument „myśl innowacyjnie”, dziewięć opracowań i trzy scenariusze. Uwagi do źródeł i propozycje wdrożenia są oddzielone od pełnych tekstów.</p>'''
page('index.html','Innowacje w miejscu pracy',overview,intro='Przewodnik po programie, materiałach dla nauczycieli i scenariuszach zajęć zawodowych.')

for p in mdfiles:
    i=int(p.name[:2]); title='Założenia programu' if i==0 else 'Bibliografia i uwagi do źródeł' if i==8 else titles[i-1]
    note='Opracowanie z dokumentacji projektu. Notatki wdrożeniowe stanowią komentarz do programu. <a href="biblioteka.html">Zobacz źródła</a>.'
    if i==0: note+=' Załączony PDF ma 76 stron; wzmianka o 74 stronach poniżej pochodzi z wcześniejszego opracowania.'
    if i==8: note='Zachowane zestawienie z folderu projektu. Oceny wiarygodności i statusy weryfikacji należą do tego opracowania; nie oznaczają nowego audytu zewnętrznych stron we wrześniu 2026 r.'
    if i in [3,4,6,7]: note+=' Liczby z przykładów i raportów należy czytać z <a href="zrodla.html">uwagami źródłowymi</a>; nie są wynikami pilotażu ZSZ5.'
    pager=''
    if 1<=i<=7:
        pager='<nav class="pager" aria-label="Kolejne moduły">'+(f'<a href="modul-{i-1}.html">← Moduł {i-1}</a>' if i>1 else '<a href="program.html">← Założenia programu</a>')+(f'<a href="modul-{i+1}.html">Moduł {i+1} →</a>' if i<7 else '<a href="scenariusze.html">Scenariusze szkolne →</a>')+'</nav>'
    page(links[p.name],title,readmd(p),eyebrow=f'PROGRAM · MODUŁ {i:02} / 07' if 1<=i<=7 else 'PROGRAM · DOKUMENTACJA',intro=briefs[i-1] if 1<=i<=7 else '',note=note,pager=pager)

page('wdrozenie.html','Wdrożenie w ZSZ5',readmd(ROOT/'content/wdrozenie.md'),eyebrow='ADAPTACJA SZKOLNA · OPRACOWANIE',intro='Pięć tematów godzin wychowawczych. Trzy rozwinięte scenariusze. Jedna mapa powiązań z programem.',note='Ta strona omawia pierwotne założenia dokumentacji szkolnej. Aktualną propozycję jednodniowych warsztatów dla modułów 1, 2, 4, 5 i 7 opisuje <a href="omowienie.html">Omówienie po przejrzeniu</a>.')
page('omowienie.html','Omówienie po przejrzeniu',readmd(ROOT/'content/omowienie.md'),eyebrow='OCENA SCENARIUSZY · ZAŁOŻENIA WARSZTATÓW',intro='Co już działa, czego brakuje i jak przygotować jednodniowe warsztaty — maksymalnie dwa moduły jednego dnia.')

audit=[]
doc_pages=[('Moduł 1 win4smes (2).docx','scenariusz-1.html','Scenariusz szkolny 1'),('Moduł 2 win4smes (1).docx','scenariusz-2.html','Scenariusz szkolny 2'),('Moduł 3 win4smes (1).docx','scenariusz-3.html','Scenariusz szkolny 3'),('WP4.1 A4.1 myśl innowacyjnie.docx','mysl-innowacyjnie.html','Myśl innowacyjnie — dokument szkolny'),('WP4.1 A4.1 Seven Modules on Workplace Innovation.docx','program-oryginal.html','Workplace Innovation & Future Skills Training Program')]
for filename,slug,title in doc_pages:
    with open(SRC/filename,'rb') as f: result=mammoth.convert_to_html(f)
    soup=BeautifulSoup(result.value,'html.parser')
    # Source titles and section markers become semantic headings; words stay untouched.
    first=True
    for p in soup.find_all(['p','h1','h2','h3']):
        tx=p.get_text().strip()
        if not tx: continue
        if p.name=='h1': p.name='h2'
        if first and tx.startswith('Moduł '): p.name='h2'
        if tx.startswith(('CZĘŚĆ ', 'KARTA AUDYTU ', 'PODSUMOWANIE AUDYTU')): p.name='h2'
        elif tx in ['Cele lekcji:', 'Metody i formy pracy:', 'Materiały dydaktyczne:', 'Tabela 1','Cukiernik','Kucharz','Fryzjer','Sprzedawca']: p.name='h3'
        first=False
    # All tables keep every row, cell, and merge produced by the DOCX converter.
    body=str(soup)
    with ZipFile(SRC/filename) as z:
        tree=etree.fromstring(z.read('word/document.xml'))
        paragraphs=[''.join(x.xpath('.//w:t/text()',namespaces=NS)) for x in tree.xpath('//w:p',namespaces=NS)]
    normalize=lambda t:re.sub(r'\s+','',t)
    # Ordered check, including paragraphs inside tables, independent of HTML rendering.
    converted=normalize(soup.get_text())
    cursor=0;missing=[]
    for j,p in enumerate(paragraphs):
        t=normalize(p)
        if not t:continue
        k=converted.find(t,cursor)
        if k<0:missing.append({'paragraph':j,'text':p})
        else:cursor=k+len(t)
    audit.append({'file':filename,'paragraphs':len(paragraphs),'missing_or_reordered':missing,'warnings':[str(x) for x in result.messages]})
    if filename.startswith('Moduł ') and missing: raise RuntimeError(f'Incomplete conversion: {filename}: {missing}')
    note='Pełna treść dokumentu. Zachowano brzmienie, kolejność akapitów, listy i tabele; układ dostosowano do czytania w przeglądarce. '+f'<a href="{file_map[filename]}" download>Pobierz oryginalny DOCX</a>.'
    if slug=='scenariusz-3.html':note+=' Ten scenariusz odpowiada <a href="modul-4.html">modułowi 4 programu</a>.'
    if slug.startswith('scenariusz'):note+=' Uwagi do czasu i organizacji zajęć znajdują się w <a href="wdrozenie.html">osobnym opracowaniu</a>.'
    page(slug,title,body,eyebrow='DOKUMENT ŹRÓDŁOWY · PEŁNY TEKST',note=note,lang='en' if slug=='program-oryginal.html' else 'pl')

scenarios='''<p>Poniżej znajdują się pełne teksty trzech przekazanych scenariuszy DOCX. Zachowano także przykłady branżowe, tabele i miejsca na odpowiedzi. Oryginały można pobrać z każdej strony.</p><ol class="module-list">'''
for i,t in enumerate([titles[0],titles[1],titles[3]],1):
    timing=['3 × 45 minut','140–150 minut według dokumentu','140 minut według dokumentu'][i-1]
    scenarios+=f'<li><a href="scenariusz-{i}.html"><span class="module-number">0{i}</span><span><strong>{t}</strong><span>{timing} · pełna treść DOCX</span></span><b aria-hidden="true">↗</b></a></li>'
scenarios+='</ol><h2>Numeracja i przygotowanie</h2><p>Scenariusz szkolny 3 dotyczy zrównoważonego rozwoju, czyli modułu 4 w programie siedmiomodułowym. <a href="wdrozenie.html">Sprawdź mapę tematów oraz uwagi do czasu zajęć i ewaluacji</a>.</p><p>W dokumentacji szkolnej tematy 4 i 5 opisano jako zarysy. Ich podstawę merytoryczną znajdziesz w modułach <a href="modul-6.html">6 — Komunikacja i zarządzanie zmianą</a> oraz <a href="modul-7.html">7 — Osobiste kompetencje przyszłości</a>.</p>'
page('scenariusze.html','Scenariusze szkolne 1–3',scenarios,eyebrow='MATERIAŁY DLA WYCHOWAWCÓW',intro='Gotowe przebiegi zajęć, ćwiczenia zawodowe i materiały do pracy z klasą.')

library='''<h2>Program i adaptacja</h2><ul><li><a href="program-oryginal.html">Program Hanse-Parlament — pełny tekst angielski</a> (listopad 2025)</li><li><a href="mysl-innowacyjnie.html">„Myśl innowacyjnie” — pełny dokument szkolny</a> (Wiesław Filipiak i Maciej Najwer, styczeń 2026)</li><li><a href="scenariusze.html">Trzy pełne scenariusze szkolne</a></li><li><a href="zrodla.html">Bibliografia i uwagi do źródeł</a></li></ul><h2>Wszystkie pliki źródłowe</h2><p>Oryginały dokumentów i opracowań wykorzystanych na stronie. Pliki DOCX i PDF zachowują swój pierwotny układ.</p><ul class="downloads">'''
for x in file_records:
    library+=f'<li><a href="{x["url"]}" download>{html.escape(x["name"])}</a><span>{x["name"].split(".")[-1].upper()} · {max(1,round(x["bytes"]/1024))} KB</span></li>'
library+='</ul><h2>Zakres opracowania</h2><p>Opracowania siedmiu modułów i bibliografia pochodzą z dziewięciu plików Markdown w folderze projektu. Strona „Wdrożenie w ZSZ5” syntetyzuje zależności pomiędzy nimi, szkolnym dokumentem i trzema scenariuszami. Pełne teksty są prezentowane osobno, bez dopisywania do nich uwag redakcyjnych.</p><p>Dokumenty stanowią materiały do przygotowania zajęć. W tym zbiorze nie ma raportu potwierdzającego realizację ani skuteczność pilotażu. Załączony PDF liczy 76 stron; wcześniejsze opracowanie w folderze podaje inną liczbę.</p>'
page('biblioteka.html','Biblioteka dokumentów',library,eyebrow='15 PLIKÓW ŹRÓDŁOWYCH',intro='Pełne materiały programu, dokumentacja szkolna i opracowania tematyczne w jednym miejscu.')
(ROOT/'conversion-report.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2))
(OUT/'manifest.json').write_text(json.dumps(file_records,ensure_ascii=False,indent=2))
print('Prepared',len(list(OUT.glob('*.html'))),'HTML pages and',len(file_records),'source downloads.')
for a in audit: print(a['file'], ':',len(a['missing_or_reordered']),'missing/reordered paragraphs;',len(a['warnings']),'conversion notices')
