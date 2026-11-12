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


ORDER_TAIL = ['最新情報', '概要文', '買取の流れ', '基本情報', '買取品目', '買取方法', '写真', '質問と回答', 'クチコミ導線']
HERO_EYEBROW = '<span style="font-size: 13px; font-weight: 700; letter-spacing: 0.06em; color: #ffd1de">金・プラチナ／ブランド品／腕時計</span>'
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
    b['カバー写真'] = rep(b['カバー写真'], HERO_EYEBROW, HERO_EYEBROW.replace('金・プラチナ／ブランド品／腕時計', '金・プラチナ・貴金属の買取'))
    b['電話の訴求'] = rep(b['電話の訴求'], PHONE_EXAMPLE, '「18金の指輪が2つ」「喜平ネックレス」など、品物を伝えるだけ。')
    extra = {'こんな物でも売れます': okish(
        'こんな金・プラチナも、お値段がつきます', '重さで査定するので、壊れていても大丈夫です。',
        [('切れたネックレス', '金・プラチナは重さで査定'), ('片方だけのピアス', '1点だけでもOK'),
         ('刻印がわからないアクセサリー', '素材を確認して査定'), ('金歯', '金・プラチナとして査定'),
         ('記念コイン・金貨', '金貨・銀貨・小判も'), ('変色・傷のある指輪', '状態を問わずご相談を')], '#fef7e0')}
    order = ['カバー写真', '店名', 'アクションボタン', '電話の訴求', 'タブ', '相場', '買取実績', 'こんな物でも売れます'] + ORDER_TAIL + ['下部固定ボタン']
    out = join(head, list(b.items()), order, extra)
    return ('gold', v, out,
            '他店に負けない高価買取に挑戦中｜高崎市の金・プラチナ買取 さすがや高崎飯塚店',
            '高崎市飯塚町、コメダ珈琲の向かいの買取専門店。金・プラチナの指輪・ネックレス・喜平・金貨を重さで査定し、その場で現金化。'
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
    hero = rep(b['カバー写真'], HERO_EYEBROW, HERO_EYEBROW.replace('金・プラチナ／ブランド品／腕時計', 'ブランド品・腕時計の買取'))
    hero = re.sub(r'<span style="display: flex; flex-direction: column; align-items: flex-end; background: #fff7e0;.*?</span></span></span>',
                  '<span style="display: flex; flex-direction: column; align-items: flex-end; background: #ffffff; border: 2px solid #fbbc04; color: #202124; padding: 4px 10px; border-radius: 10px; line-height: 1.25">'
                  '<span style="font-size: 10px; font-weight: 700">Googleクチコミ</span><span style="font-size: 16px; font-weight: 700"><span style="color: #fbbc04">★</span>{{rating}}</span></span>',
                  hero, count=1, flags=re.S)
    assert 'Googleクチコミ' in hero
    b['カバー写真'] = hero
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
            '他店に負けない高価買取に挑戦中｜高崎市のブランド品・腕時計買取 さすがや高崎飯塚店',
            '高崎市飯塚町、コメダ珈琲の向かいの買取専門店。エルメス・ルイ・ヴィトン・シャネルのバッグや財布、ロレックスなどの腕時計を査定無料でその場で現金化。'
            '箱や保証書がなくてもご相談ください。駐車場6台、定休日なし。')


def build(V, tpl):
    head, blocks = split(tpl)
    names = [n for n, _ in blocks]
    for need in ['お店パネル', 'カバー写真', '店名', 'アクションボタン', '電話の訴求', 'タブ', '相場', '買取実績',
                 'こんな物でも売れます', '下部固定ボタン'] + ORDER_TAIL:
        assert need in names, need
    return [gold(V, tpl), brand(V, tpl)]
