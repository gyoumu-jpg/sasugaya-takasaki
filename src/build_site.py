#!/usr/bin/env python3
"""Render the Design-canvas LP (Main.dc.html) into a standalone static index.html."""
import re, json, sys, html

import os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'src', 'Main.dc.html')
OUT = os.path.join(ROOT, 'index.html')

# Google Ads conversion settings (filled after the conversion actions are created)
AW_ID = sys.argv[1] if len(sys.argv) > 1 else 'AW-18407097518'
LABEL_TEL = sys.argv[2] if len(sys.argv) > 2 else 'FweFCPifq7AdEK6JmMlE'
LABEL_LINE = sys.argv[3] if len(sys.argv) > 3 else 'JkcnCPufq7AdEK6JmMlE'
LABEL_ROUTE = sys.argv[4] if len(sys.argv) > 4 else 'vgbsCP6fq7AdEK6JmMlE'

src = open(SRC, encoding='utf-8').read()

BLOBS = {
    '/_blob/3a81253738736e03785749fdc0314923': 'img/hero.jpg',
    '/_blob/db8029c3cb752aa79d815d2260ab2d89': 'img/hero.jpg',
    '/_blob/2817dec0217510d01ce8bf0db620f936': 'img/interior1.jpg',
    '/_blob/f0b1afde92d3b97a265d0e2981cfb6fd': 'img/interior2.jpg',
    '/_blob/e2e69fb8ab9ba367bc5419bb6fa57898': 'img/staff1.jpg',
    '/_blob/1785966f8a7432565851590110fc42b0': 'img/staff2.jpg',
    '/_blob/b935f7d786e69ed4bbbb9f03fca21b19': 'img/parking.jpg',
    '/_blob/dc532101ae32abd39e568b5cdb87f2c0': 'img/r1.jpg',
    '/_blob/b12599dada3ed5a0e840166d7a3a2879': 'img/r2.jpg',
    '/_blob/4403c5a8ccdc56c42f1597ee1418950b': 'img/r3.jpg',
    '/_blob/42778c475582aac16dfa0b980ee1de58': 'img/r4.jpg',
    '/_blob/c6e314b32bc74917dc7f993a769d7822': 'img/r5.jpg',
    '/_blob/38e5b70be7ac23ba1a724a6cd27d0e9a': 'img/r6.jpg',
}

# ---- data (mirrors renderVals) ----
props = json.loads(re.search(r"data-props='([^']*)'", src).group(1))
V = {k: v.get('default') for k, v in props.items() if isinstance(v, dict) and 'default' in v}
V['lineUrl'] = 'https://lin.ee/wYV9gZC'
n = int(re.sub(r'[^0-9]', '', V['goldRate']) or 0)
V['fiveGram'] = '約' + f"{round(n * 5 / 1000) / 10:.1f}" + '万円'

def js_array(name):
    m = re.search(name + r': \[(.*?)\n      \]', src, re.S)
    items = []
    for obj in re.findall(r'\{(.*?)\}', m.group(1), re.S):
        d = {}
        for k, val in re.findall(r"(\w+): '((?:[^'\\]|\\.)*)'", obj):
            d[k] = val
        items.append(d)
    return items

for name in ['results', 'items', 'faqs', 'reviews']:
    V[name] = js_array(name)

# ---- template ----
TEMPLATE = re.search(r'<x-dc>(.*)</x-dc>', src, re.S).group(1)
TEMPLATE = re.sub(r'<helmet>.*?</helmet>', '', TEMPLATE, flags=re.S)

def render_body(V, template=TEMPLATE, prefix=''):
    def render_for(m):
        lst, var, inner = m.group(1), m.group(2), m.group(3)
        out = []
        for i, it in enumerate(V[lst]):
            s = inner
            s = re.sub(r'\{\{\s*' + var + r'\.(\w+)\s*\}\}', lambda mm: html.escape(it.get(mm.group(1), '')), s)
            s = s.replace('{{$index}}', str(i))
            out.append(s)
        return ''.join(out)
    body = re.sub(r'<sc-for list="\{\{(\w+)\}\}" as="(\w+)"[^>]*>(.*?)</sc-for>', render_for, template, flags=re.S)
    body = re.sub(r'\{\{\s*(\w+)\s*\}\}', lambda m: html.escape(str(V.get(m.group(1), ''))), body)
    for k, v in BLOBS.items():
        body = body.replace(k, prefix + v)
    assert '{{' not in body, re.findall(r'\{\{[^}]*\}\}', body)[:5]
    assert '/_blob/' not in body
    # live open/closed status instead of a fixed 「営業中」
    body = body.replace('font-weight: 500">営業中</span>', 'font-weight: 500" data-open>営業中</span>')
    body = body.replace(' · 18:00 に営業終了 · 定休日なし', ' <span data-open-note>· 18:00 に営業終了</span> · 定休日なし')
    # mark CTA links for conversion tracking
    body = re.sub(r'<a href="tel:', '<a data-cv="tel" href="tel:', body)
    body = re.sub(r'<a href="https://lin\.ee/', '<a data-cv="line" href="https://lin.ee/', body)
    body = re.sub(r'<a href="https://www\.google\.com/maps/dir/', '<a data-cv="route" href="https://www.google.com/maps/dir/', body)
    # external links open in a new tab
    body = re.sub(r'<a (data-cv="(?:line|route)" )?href="(https://[^"]+)"', lambda m: f'<a {m.group(1) or ""}href="{m.group(2)}" target="_blank" rel="noopener"', body)
    return body

BASE_URL = 'https://gyoumu-jpg.github.io/sasugaya-takasaki/'
title = '金・ブランド品 高価買取｜高崎市の買取専門店さすがや高崎飯塚店'
desc = ('高崎市飯塚町、コメダ珈琲 高崎飯塚店の向かいの買取専門店。金・プラチナ・ブランド品・腕時計を査定無料でその場で現金化。'
        '査定だけでもOK、断っても無料。駐車場6台、定休日なし、群馬県内全域へ出張買取。')

ld = {
    "@context": "https://schema.org",
    "@type": "Store",
    "name": "買取専門店 さすがや 高崎飯塚店",
    "image": "https://gyoumu-jpg.github.io/sasugaya-takasaki/img/hero.jpg", "url": "https://gyoumu-jpg.github.io/sasugaya-takasaki/",
    "telephone": "+81-27-364-1619",
    "address": {"@type": "PostalAddress", "postalCode": "370-0069", "addressRegion": "群馬県",
                "addressLocality": "高崎市", "streetAddress": "飯塚町431-5 上原貸店舗B号室", "addressCountry": "JP"},
    "geo": {"@type": "GeoCoordinates", "latitude": 36.3414316, "longitude": 139.0083548},
    "openingHoursSpecification": [{"@type": "OpeningHoursSpecification",
        "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
        "opens": "10:00", "closes": "18:00"}],
    "areaServed": ["高崎市", "前橋市", "藤岡市", "安中市", "富岡市", "甘楽町"],
    "aggregateRating": {"@type": "AggregateRating", "ratingValue": V['rating'], "reviewCount": V['reviewCount']},
}

gtag = ''
if AW_ID:
    labels = {'tel': LABEL_TEL, 'line': LABEL_LINE, 'route': LABEL_ROUTE}
    gtag = f'''<script async src="https://www.googletagmanager.com/gtag/js?id={AW_ID}"></script>
<script>
window.dataLayer = window.dataLayer || [];
function gtag(){{dataLayer.push(arguments);}}
gtag('js', new Date());
gtag('config', '{AW_ID}');
(function () {{
  var labels = {json.dumps(labels)};
  document.addEventListener('click', function (e) {{
    var a = e.target.closest && e.target.closest('a[data-cv]');
    if (!a) return;
    var label = labels[a.getAttribute('data-cv')];
    if (label) gtag('event', 'conversion', {{ send_to: '{AW_ID}/' + label }});
  }}, true);
}})();
</script>'''

def make_page(body, title, desc, url):
    return f'''<!doctype html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:type" content="website">
<meta property="og:image" content="{BASE_URL}img/hero.jpg">
<meta property="og:url" content="{url}">
<link rel="canonical" href="{url}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;500;700&amp;family=Noto+Serif+JP:wght@700;900&amp;family=Roboto:wght@400;500;700&amp;display=swap" rel="stylesheet">
<style>
body{{margin:0;background:#f1f3f4}}
a{{color:#1a73e8}}a:hover{{color:#174ea6}}
img{{max-width:100%}}
</style>
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
{gtag}
</head>
<body>
{body.strip()}
<script>
(function () {{
  // Japan time; open 10:00-18:00 every day except 12/29-1/3
  var now = new Date(Date.now() + 9 * 3600 * 1000 + new Date().getTimezoneOffset() * 60000);
  var m = now.getMonth() + 1, d = now.getDate(), h = now.getHours();
  var holiday = (m === 12 && d >= 29) || (m === 1 && d <= 3);
  var open = !holiday && h >= 10 && h < 18;
  document.querySelectorAll('[data-open]').forEach(function (el) {{
    el.textContent = open ? '営業中' : '営業時間外';
    el.style.color = open ? '#188038' : '#c5221f';
  }});
  document.querySelectorAll('[data-open-note]').forEach(function (el) {{
    el.textContent = open ? '· 18:00 に営業終了' : (holiday ? '· 年末年始休業' : '· 10:00 に営業開始');
  }});
}})();
</script>
<script>
(function () {{
  // 金・プラチナの目安額（参考相場 × 純度 × 重さ）
  var box = document.querySelector('[data-calc]');
  if (!box) return;
  var num = function (t) {{ return parseFloat(String(t).replace(/[^0-9.]/g, '')) || 0; }};
  var rate = {{ g: num(box.getAttribute('data-gold')), p: num(box.getAttribute('data-pt')), s: num(box.getAttribute('data-sv')) }};
  var sel = box.querySelector('[data-calc-purity]'), gram = box.querySelector('[data-calc-gram]'), out = box.querySelector('[data-calc-out]');
  function update() {{
    var v = sel.value.split(':'), g = parseFloat(gram.value) || 0;
    var yen = Math.floor(rate[v[0]] * parseFloat(v[1]) * g / 10) * 10;
    out.textContent = '約' + yen.toLocaleString('ja-JP') + '円';
  }}
  sel.addEventListener('change', update); gram.addEventListener('input', update); update();
}})();
</script>
</body>
</html>
'''

import variants
pages = [('', V, TEMPLATE, title, desc)] + variants.build(V, TEMPLATE)
for sub, v, tpl, t, d in pages:
    prefix = '../' if sub else ''
    out = os.path.join(ROOT, sub, 'index.html')
    os.makedirs(os.path.dirname(out), exist_ok=True)
    page = make_page(render_body(v, tpl, prefix), t, d, BASE_URL + (sub + '/' if sub else ''))
    open(out, 'w', encoding='utf-8').write(page)
    print('wrote', out, len(page), 'bytes; gtag:', bool(AW_ID))
