"""Export the consolidated report without code: .venv/bin/python src/export_html.py."""
from pathlib import Path
from html import escape
from urllib.parse import unquote
import copy
import json
import nbformat
from nbconvert import HTMLExporter
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / 'reports/html'
SOURCE = ROOT / 'notebooks/bank-churn-summary.ipynb'
OUTPUT = DEST / 'bank-churn.html'
# Only these earlier generated exports may be removed after successful verification.
LEGACY_EXPORTS = ('index.html', '01-data-cleaning.html', '02-data-analysis.html',
                  '03-prediction.html', '04-business-insights.html')
SECTIONS = [
    ('decision', 'The decision in brief', 'Decision'),
    ('audit', '1. A usable dataset', 'Data audit'),
    ('segments', '2. Training patterns', 'Customer patterns'),
    ('models', '3. A model selected', 'Models'),
    ('targeting', '4. Compare targeting', 'Targeting'),
    ('economics', '5. Economic scenarios', 'Economic scenarios'),
    ('pilot', '6. Turn the uncertainty', 'Controlled pilot'),
    ('evidence', 'Evidence and reproducibility', 'Evidence'),
]
CSS = '''
:root { color-scheme: light; --ink:#18313b; --accent:#176b76; --muted:#526670; }
* { box-sizing: border-box; }
body { margin:0; background:#f5f8f8; color:var(--ink); font:17px/1.65 system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; }
nav { background:#123d48; color:#fff; padding:1.1rem max(1rem,calc((100% - 1140px)/2)); display:flex; flex-wrap:wrap; gap:.6rem 1.3rem; }
nav a { color:#fff; text-decoration:none; padding:.2rem 0; }
nav a[aria-current="page"] { border-bottom:2px solid #90e0d6; }
main { max-width:1140px; margin:1.5rem auto 3rem; padding:2rem 2.6rem; background:#fff; border:1px solid #e0e8e9; border-radius:12px; min-width:0; }
h1,h2,h3 { line-height:1.25; color:#123d48; overflow-wrap:anywhere; }
h1 { font-size:2.1rem; margin:0 0 1.5rem; }
h2 { font-size:1.55rem; margin-top:2.7rem; }
h3 { font-size:1.25rem; margin-top:2rem; }
p,li { overflow-wrap:anywhere; }
a { color:var(--accent); text-underline-offset:3px; }
strong { font-weight:700; }
code { background:#edf3f3; border-radius:3px; padding:.1em .3em; font-size:.88em; overflow-wrap:anywhere; }
pre { white-space:pre-wrap; overflow-wrap:anywhere; font-size:.83rem; color:var(--muted); line-height:1.5; }
.jp-Cell { margin:1.1rem 0; }
.jp-OutputArea-child { margin:.8rem 0; }
.jp-OutputArea-output { min-width:0; }
.table-scroll { max-width:100%; overflow-x:auto; margin:1.2rem 0; }
table { border-collapse:collapse; min-width:100%; font-size:.88rem; line-height:1.5; text-align:left; }
th,td { padding:.6rem .75rem; border-bottom:1px solid #dbe5e6; vertical-align:top; }
th { background:#edf4f5; color:#123d48; font-weight:650; }
tbody tr:nth-child(even) { background:#f8fbfb; }
figure { margin:0; max-width:100%; }
.figure-scroll { max-width:100%; overflow-x:auto; margin:1.4rem 0; }
.figure-scroll img { display:block; width:100%; height:auto; }
figcaption { color:var(--muted); font-size:.8rem; margin-top:.4rem; }
footer { max-width:1140px; margin:0 auto 2rem; padding:0 1rem; font-size:.9rem; color:var(--muted); }
.notice { border-left:4px solid var(--accent); background:#edf5f5; padding:.85rem 1.1rem; }
.contents { list-style:none; padding:0; }
.contents li { margin:1rem 0; padding:1rem 1.2rem; background:#edf5f5; border-radius:8px; }
@media(max-width:700px) { body {font-size:16px;} nav {padding:.8rem 1rem; gap:.5rem 1rem; font-size:.9rem;} main {margin:.7rem; padding:1.2rem; border-radius:8px;} h1 {font-size:1.7rem;} h2 {font-size:1.35rem;} th,td {padding:.45rem .6rem;} .figure-scroll img {min-width:760px;} }
@media print { body {background:#fff; font-size:11pt;} nav,footer {display:none;} main {max-width:none; border:0; margin:0; padding:0;} .table-scroll,.figure-scroll {overflow:visible;} .figure-scroll img {min-width:0; max-width:100%;} h2,h3 {break-after:avoid;} table,img {break-inside:avoid;} }
'''


def navigation():
    return '<nav aria-label="Report sections">' + ''.join(
        f'<a href="#{anchor}">{escape(label)}</a>' for anchor, _, label in SECTIONS
    ) + '</nav>'


def shell(content):
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Bank customer retention: from risk scores to a measurable pilot</title><meta name="description" content="A consolidated retrospective bank retention study: data audit, customer patterns, predictive targeting, hypothetical economics and a proposed controlled pilot. No measured campaign effectiveness."><style>{CSS}</style></head><body>
{navigation()}
<main id="study">{content}</main>
<footer>Retrospective study of the supplied file · Hypothetical economic scenarios · Local preparation, no deployment</footer>
</body></html>'''


def verify(html):
    final = BeautifulSoup(html, 'html.parser')
    assert final.html['lang'] == 'en'
    assert final.find('meta', attrs={'name': 'viewport'})
    assert not final.select('script, link, .jp-CodeCell .jp-InputArea, .jp-InputPrompt, .jp-OutputPrompt')
    assert len(final.find_all('h1')) == 1
    ids = [tag['id'] for tag in final.find_all(id=True)]
    assert len(ids) == len(set(ids)), 'Duplicate HTML anchors'
    for anchor, _, _ in SECTIONS:
        assert final.find(id=anchor), f'Missing report section: {anchor}'
    for link in final.find_all('a', href=True):
        href = link['href']
        if href.startswith('#'):
            assert final.find(id=unquote(href[1:])), f'Broken section link: {href}'
        else:
            assert href.startswith(('https://', 'http://')), f'Unexpected local page link: {href}'
    images = final.find_all('img')
    assert len(images) == 3
    assert all(image.get('src', '').startswith('data:image/') for image in images)
    assert all(not tag.get('src', '').startswith(('http:', 'https:')) for tag in final.find_all(src=True))
    text = final.get_text(' ', strip=True)
    # Check locally available identifiers without embedding individual examples in source code.
    raw_path = ROOT / 'data/raw/Churn_Modelling.csv'
    if raw_path.exists():
        import csv
        with raw_path.open(newline='', encoding='utf-8') as source:
            for row in csv.DictReader(source):
                identifier = row.get('CustomerId', '')
                assert not identifier or identifier not in text, 'Individual data found in report'
    for value in ['248', '407', '62%', '60.9%', '3.05', '0.857', '0.685', '€20,800', '€4,000']:
        assert value in text, f'Missing expected summary result: {value}'
    return final


def export():
    DEST.mkdir(parents=True, exist_ok=True)
    nb = nbformat.read(SOURCE, as_version=4)
    for cell in nb.cells:
        if cell.cell_type == 'code':
            assert cell.execution_count is not None, 'Publication notebook is not executed'
            assert all(output.output_type != 'error' for output in cell.outputs)
            cell.outputs = [output for output in cell.outputs
                            if not (output.output_type == 'stream' and output.name == 'stderr')]
    exporter = HTMLExporter(template_name='lab', exclude_input=True,
                            exclude_input_prompt=True, exclude_output_prompt=True)
    html, _ = exporter.from_notebook_node(copy.deepcopy(nb))
    soup = BeautifulSoup(html, 'html.parser')
    content = soup.find('main') or soup.body
    for element in content.select('script, link, .jp-CodeCell .jp-InputArea, .jp-InputPrompt, .jp-OutputPrompt, .anchor-link'):
        element.decompose()
    headings = content.find_all('h2')
    assert len(headings) == len(SECTIONS), 'Unexpected summary structure'
    for heading, (anchor, prefix, _) in zip(headings, SECTIONS):
        assert heading.get_text().strip().startswith(prefix), prefix
        heading['id'] = anchor
    for table in list(content.find_all('table')):
        table.wrap(soup.new_tag('div', attrs={
            'class': 'table-scroll', 'tabindex': '0', 'role': 'region',
            'aria-label': 'Horizontally scrollable table'}))
    descriptions = [
        'Training departure-label rates by activity and age band, with sample sizes and 95% Wilson intervals.',
        'Departure labels targeted by the frozen no-contact, random, business and predictive strategies.',
        'Simulated net gain across the frozen assumptions for retention effect, including no effect.',
    ]
    captions = [
        'Training associations do not establish causes or offer effectiveness.',
        'Targeted departure labels are not customers successfully retained.',
        'Hypothetical economic scenarios, not measured gains or a validated forecast.',
    ]
    images = list(content.find_all('img'))
    assert len(images) == len(descriptions)
    for i, (image, description, caption) in enumerate(zip(images, descriptions, captions), 1):
        assert image.get('src', '').startswith('data:image/'), 'Image is not embedded'
        image['alt'] = f'Figure {i}. {description}'
        figure = soup.new_tag('figure', attrs={'class': 'figure-scroll', 'tabindex': '0'})
        image.wrap(figure)
        label = soup.new_tag('figcaption')
        label.string = f'Figure {i}. {caption} On small screens, scroll horizontally to read the labels.'
        figure.append(label)
    final_html = shell(content.decode_contents())
    verify(final_html)
    OUTPUT.write_text(final_html, encoding='utf-8')
    final = verify(OUTPUT.read_text(encoding='utf-8'))
    # Remove only the five explicitly superseded generated files, after verification.
    for name in LEGACY_EXPORTS:
        (DEST / name).unlink(missing_ok=True)
    print(json.dumps({'export': str(OUTPUT.relative_to(ROOT)),
                      'source': str(SOURCE.relative_to(ROOT)),
                      'sections': len(SECTIONS), 'figures': len(final.find_all('img')),
                      'tables': len(final.find_all('table'))}, indent=2))


if __name__ == '__main__':
    export()
