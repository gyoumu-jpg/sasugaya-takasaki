"""金向け（gold/）とブランド向け（brand/）のLPを、共通の Main.dc.html から作る。

build_site.py から呼ばれ、(サブフォルダ名, データV, テンプレート, title, description) のリストを返す。
テンプレートは <!-- 見出し --> コメントで区切られたブロックの並べ替えと、文言の置き換えで作る。
置き換え元の文言が見つからないときは止まる（ソースを直したときに気づけるように）。
"""
import copy
import re

PH = ('<path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3.1 19.5 19.5 0 0 1-6-6A19.8 19.8 0 0 1 2.1 4.2 2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1.9.4 1.8.7 2.7'
      'a2 2 0 0 1-.5 2.1L8 9.8a16 16 0 0 0 6 6l1.3-1.3a2 2 0 0 1 2.1-.4c.9.3 1.8.6 2.7.7a2 2 0 0 1 1.7 2z"></path>')


def split(tpl):
    """テンプレートを [先頭, (名前, html), ..., 末尾] に分ける。末尾は「下部固定ボタン」以降。"""
    parts = re.split(r'(<!-- [^>]+? -->)', tpl)
    head = parts[0]
    blocks = []
    for i in range(1, len(parts), 2):
        blocks.append((re.sub(r'（.*?）$', '', parts[i][5:-4]), parts[i] + parts[i + 1]))
    return head, blocks


def join(head, blocks, order, extra):
    d = dict(blocks)
    d.update(extra)
    first = 'お店パネル'
    out = head + d[first]
    for name in order:
        out += d[name]
    return out


def rep(s, old, new):
    assert old in s, old[:60]
    return s.replace(old, new)


def cards(items, bg):
    return ''.join(
        f'<div style="display: flex; flex-direction: column; gap: 2px; padding: 10px 12px; border-radius: 10px; background: {bg}">'
        f'<span style="font-size: 14px; font-weight: 700; color: #202124">✓ {a}</span><span style="font-size: 12px; color: #5f6368">{b}</span></div>'
        for a, b in items)


def okish(title, lead, items, bg):
    return f'''<!-- こんな物でも売れます -->
<section style="padding: 16px 24px; border-bottom: 1px solid #dadce0; display: flex; flex-direction: column; gap: 10px">
<h2 style="margin: 0; font-size: 18px; font-weight: 500">{title}</h2>
<span style="font-size: 13px; color: #5f6368">{lead}</span>
<div style="display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 8px">{cards(items, bg)}</div>
</section>

'''


def set_hero(hero, title=None, thumbs=None, badge=None, perk3=None):
    """A案ヒーローの見出し・写真・右上バッジ・3つ目の特典を差し替える。"""
    if title:
        hero, n = re.subn(r'(<span data-hero-title[^>]*>).*?(</span>)', lambda m: m.group(1) + title + m.group(2), hero, count=1, flags=re.S)
        assert n == 1
    if thumbs is not None:
        hero, n = re.subn(r'(<div data-hero-thumbs[^>]*>).*?(</div>)', lambda m: m.group(1) + thumbs + m.group(2), hero, count=1, flags=re.S)
        assert n == 1
    if badge is not None:
        hero, n = re.subn(r'<span data-hero-badge.*?</span></span></span>', badge, hero, count=1, flags=re.S)
        assert n == 1
    if perk3:
        old = '<b style="display: block; font-size: 13px">査定<br>0円</b><span style="font-size: 10px">断っても無料</span>'
        hero = rep(hero, old, f'<b style="display: block; font-size: 13px">{perk3[0]}</b><span style="font-size: 10px">{perk3[1]}</span>')
    return hero


def thumb(bid, alt):
    return (f'<img src="/_blob/{bid}" alt="{alt}" style="width: 100%; aspect-ratio: 1 / 1; object-fit: cover; border-radius: 10px; '
            'border: 2px solid #e9c46a; box-shadow: 0 4px 12px rgba(0,0,0,0.5)">')


R1, R2, R3, R4, R5 = ('dc532101ae32abd39e568b5cdb87f2c0', 'b12599dada3ed5a0e840166d7a3a2879', '4403c5a8ccdc56c42f1597ee1418950b',
                      '42778c475582aac16dfa0b980ee1de58', 'c6e314b32bc74917dc7f993a769d7822')


ORDER_TAIL = ['最新情報', '概要文', '買取の流れ', '基本情報', '買取品目', '買取方法', '写真', '質問と回答', 'クチコミ導線']
PHONE_EXAMPLE = '「金の指輪が2つ」「ヴィトンのバッグ」など、品物を伝えるだけ。'


def gold(V, tpl):
    v = copy.deepcopy(V)
    v['results'] = [r for r in v['results'] if 'シャネル' not in r['cat']]
    v['faqs'] = [
        {'q': '壊れたネックレスや片方だけのピアスも売れますか？', 'a': '金・プラチナは素材の重さで査定するため、壊れていてもお値段がつきます。'},
        {'q': '刻印がなくて金かどうかわかりません。', 'a': 'お持ちいただければ素材を確認して査定します。査定だけでも無料です。'},
        {'q': '査定だけでも大丈夫ですか？', 'a': 'もちろんです。売らない場合も費用は一切かかりません。'},
        {'q': '予約は必要ですか？', 'a': '予約なしでご来店いただけます。お品物が多い場合は事前にお電話いただくとスムーズです。'},
        {'q': '売るときに必要なものは？', 'a': '法律により本人確認が必要です。運転免許証・マイナンバーカードなどをお持ちください。'},
    ]
    head, blocks = split(tpl)
    b = dict(blocks)
    b['カバー写真'] = set_hero(b['カバー写真'], title='金・銀<br>高価買取',
                            thumbs=thumb(R1, '金貨＆銀貨の買取実績') + thumb(R2, '喜平ネックレスの買取実績') + thumb(R3, '純銀小判の買取実績') + thumb(R5, 'プラチナのバングルとリングの買取実績'),
                            perk3=('壊れて<br>いてもOK', '重さで査定'))
    b['電話の訴求'] = rep(b['電話の訴求'], PHONE_EXAMPLE, '「18金の指輪が2つ」「喜平ネックレス」など、品物を伝えるだけ。')
    extra = {'こんな物でも売れます': okish(
        'こんな金・銀・プラチナも、お値段がつきます', '重さで査定するので、壊れていても大丈夫です。',
        [('切れたネックレス', '金・プラチナは重さで査定'), ('片方だけのピアス', '1点だけでもOK'),
         ('刻印がわからないアクセサリー', '素材を確認して査定'), ('金歯', '金・プラチナとして査定'),
         ('記念コイン・金貨', '金貨・銀貨・小判も'), ('銀貨・純銀の小判や器', '銀も買取しています')], '#fef7e0')}
    order = ['カバー写真', '店名', 'アクションボタン', '電話の訴求', 'タブ', '相場', '買取実績', 'こんな物でも売れます'] + ORDER_TAIL + ['下部固定ボタン']
    out = join(head, list(b.items()), order, extra)
    return ('gold', v, out,
            '金・銀 高価買取｜高崎市の買取専門店さすがや高崎飯塚店',
            '高崎市飯塚町、コメダ珈琲の向かいの買取専門店。金・銀・プラチナの指輪・ネックレス・喜平・金貨・銀貨を重さで査定し、その場で現金化。'
            '壊れていてもOK、査定だけでも無料。今日の金相場と目安の計算機も掲載。駐車場6台、定休日なし。')


def brand(V, tpl):
    v = copy.deepcopy(V)
    v['results'] = sorted(v['results'], key=lambda r: 0 if 'シャネル' in r['cat'] else 1)
    v['faqs'] = [
        {'q': '箱や保証書がなくても売れますか？', 'a': 'ご相談ください。付属品がない状態でも査定します。'},
        {'q': '使用感があったり、古いデザインでも大丈夫ですか？', 'a': '状態を見て査定します。まずはお気軽にお持ちください。査定だけでも無料です。'},
        {'q': '電話でもおおよその金額はわかりますか？', 'a': 'ブランド名と品物（バッグ・財布など）を伝えていただければ、おおよその金額をお伝えします。'},
        {'q': '予約は必要ですか？', 'a': '予約なしでご来店いただけます。お品物が多い場合は事前にお電話いただくとスムーズです。'},
        {'q': '売るときに必要なものは？', 'a': '法律により本人確認が必要です。運転免許証・マイナンバーカードなどをお持ちください。'},
    ]
    head, blocks = split(tpl)
    b = dict(blocks)
    G = 'fill="none" stroke="#f3cf73" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"'
    icons = {
        # 上部ハンドルのハンドバッグ（汎用の形）
        'bag': f'<svg viewBox="0 0 48 48" width="40" height="40" aria-hidden="true"><path {G} d="M17 17v-3a7 7 0 0 1 14 0v3"/><path {G} d="M9 17h30l-2 22a3 3 0 0 1-3 3H14a3 3 0 0 1-3-3z"/><path {G} d="M19 24h10"/></svg>',
        # 長財布
        'wallet': f'<svg viewBox="0 0 48 48" width="40" height="40" aria-hidden="true"><rect {G} x="6" y="13" width="36" height="22" rx="3"/><path {G} d="M6 21h36"/><circle {G} cx="35" cy="28" r="2.2"/></svg>',
        # 腕時計
        'watch': f'<svg viewBox="0 0 48 48" width="40" height="40" aria-hidden="true"><path {G} d="M18 6h12l1 9H17zM17 33h14l-1 9H18z"/><circle {G} cx="24" cy="24" r="10"/><path {G} d="M24 18v6l4 3"/><path {G} d="M34.5 22.5h2"/></svg>',
    }
    tile = lambda ic, n: ('<span style="display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 2px; aspect-ratio: 1 / 1; '
                          'border-radius: 10px; border: 1px solid #e9c46a; background: radial-gradient(circle at 50% 35%, rgba(243,207,115,0.18), rgba(255,255,255,0.02) 70%)">'
                          f'{icons[ic]}<span style="font-family: \'Noto Serif JP\', serif; font-size: 11px; font-weight: 700; color: #f7e3a6; line-height: 1.2; text-align: center">{n}</span></span>')
    names = tile('bag', 'エルメス') + tile('wallet', 'ルイ・<br>ヴィトン') + tile('watch', 'ロレックス')
    badge = ('<span style="display: flex; flex-direction: column; align-items: flex-end; flex: none; border: 1px solid #e9c46a; color: #f7e3a6; padding: 3px 8px; border-radius: 8px; line-height: 1.25">'
             '<span style="font-size: 10px; font-weight: 700">Googleクチコミ</span><span style="font-size: 15px; font-weight: 700"><span style="color: #fbbc04">★</span>{{rating}}</span></span>')
    b['カバー写真'] = set_hero(b['カバー写真'], title='ブランド品・腕時計<br>高価買取', thumbs=thumb(R4, 'シャネルの財布の買取実績') + names,
                            badge=badge, perk3=('箱・保証書<br>なしもOK', 'ご相談ください'))
    b['カバー写真'] = rep(b['カバー写真'], '予約不要・駐車場6台・定休日なし ／ コメダ特典は2026年12月末まで',
                         '※ブランド名の絵はイメージです。予約不要・駐車場6台・定休日なし ／ コメダ特典は2026年12月末まで')
    b['電話の訴求'] = rep(b['電話の訴求'], PHONE_EXAMPLE, '「ヴィトンの長財布」「シャネルのバッグ」など、ブランド名と品物を伝えるだけ。')
    brands = [('エルメス', 'バッグ・財布・小物'), ('ルイ・ヴィトン', 'バッグ・財布・小物'), ('シャネル', 'バッグ・財布・アクセサリー'),
              ('ロレックス', '腕時計'), ('オメガ', '腕時計'), ('グランドセイコー', '腕時計')]
    tiles = ''.join(
        f'<div style="display: flex; flex-direction: column; gap: 2px; padding: 12px; border: 1px solid #dadce0; border-radius: 10px">'
        f'<span style="font-size: 15px; font-weight: 700">{a}</span><span style="font-size: 12px; color: #5f6368">{c}</span></div>' for a, c in brands)
    extra = {
        'ブランド': f'''<!-- ブランド -->
<section id="brands" style="padding: 16px 24px; border-bottom: 1px solid #dadce0; display: flex; flex-direction: column; gap: 10px">
<h2 style="margin: 0; font-size: 18px; font-weight: 500">買取強化ブランド</h2>
<div style="display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 8px">{tiles}</div>
<span style="font-size: 13px; color: #5f6368">ほかのブランドもご相談ください。ブランド名がわからない品物でも、お持ちいただければ確認します。</span>
<a href="tel:0273641619" style="display: flex; align-items: center; justify-content: center; gap: 8px; min-height: 48px; border-radius: 999px; background: #1a73e8; color: #ffffff; text-decoration: none; font-size: 15px; font-weight: 700"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{PH}</svg>ブランド名を伝えて金額を聞く（無料）</a>
</section>

''',
        'こんな物でも売れます': okish(
            'こんなブランド品も、ご相談ください', '「これは売れないかも」と思う物こそ、一度お持ちください。',
            [('箱・保証書のないバッグ', '付属品なしでも査定'), ('使用感のある財布', '状態を見て査定'),
             ('古いデザインの品物', 'まずはお気軽に'), ('ベルトが傷んだ腕時計', 'まずはご相談ください'),
             ('片方だけのアクセサリー', '金・プラチナなら重さで'), ('使わなくなった小物', 'キーケース・名刺入れなど')], '#e8f0fe'),
    }
    order = ['カバー写真', '店名', 'アクションボタン', '電話の訴求', 'タブ', 'ブランド', '買取実績', 'こんな物でも売れます'] + ORDER_TAIL + ['相場', '下部固定ボタン']
    out = join(head, list(b.items()), order, extra)
    return ('brand', v, out,
            'ブランド品・腕時計 高価買取｜高崎市の買取専門店さすがや高崎飯塚店',
            '高崎市飯塚町、コメダ珈琲の向かいの買取専門店。エルメス・ルイ・ヴィトン・シャネルのバッグや財布、ロレックスなどの腕時計を査定無料でその場で現金化。'
            '箱や保証書がなくてもご相談ください。駐車場6台、定休日なし。')


def build(V, tpl):
    head, blocks = split(tpl)
    names = [n for n, _ in blocks]
    for need in ['お店パネル', 'カバー写真', '店名', 'アクションボタン', '電話の訴求', 'タブ', '相場', '買取実績',
                 'こんな物でも売れます', '下部固定ボタン'] + ORDER_TAIL:
        assert need in names, need
    return [gold(V, tpl), brand(V, tpl)]
