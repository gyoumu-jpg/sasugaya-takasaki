#!/usr/bin/env python3
"""田中貴金属の地金 店頭買取価格（税込）を取得して、LPの相場（goldRate / ptRate / rateDate）を更新する。
変更があれば True を返し、src/Main.dc.html を書き換える。index.html の生成は build_site.py で行う。"""
import os, re, sys, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'src', 'Main.dc.html')
URL = 'https://gold.tanaka.co.jp/commodity/souba/index.php'

def fetch():
    req = urllib.request.Request(URL, headers={'User-Agent': 'Mozilla/5.0 (rate-updater)'})
    return urllib.request.urlopen(req, timeout=30).read().decode('utf-8', 'replace')

def parse(h):
    t = re.search(r'<table id="metal_price">(.*?)</table>', h, re.S).group(1)
    def buy(cls):
        row = re.search(r'<tr class="%s">(.*?)</tr>' % cls, t, re.S).group(1)
        return re.search(r'<td class="purchase_tax">\s*([\d,.]+)\s*円', row).group(1)
    m = re.search(r'地金価格<span>(\d{4})年(\d{1,2})月(\d{1,2})日', h)
    return buy('gold'), buy('pt'), buy('silver'), f'{int(m.group(2))}月{int(m.group(3))}日更新'

def main():
    gold, pt, sv, date = parse(fetch())
    for v, lo, hi in ((gold, 1000, 100000), (pt, 1000, 100000), (sv, 30, 10000)):
        n = float(v.replace(',', ''))
        if not lo <= n <= hi:
            sys.exit(f'想定外の値: {v}')
    s = open(SRC, encoding='utf-8').read()
    new = s
    for key, val in (('goldRate', gold + '円'), ('ptRate', pt + '円'), ('svRate', sv + '円'), ('rateDate', date)):
        new = re.sub(r'("%s":\{"editor":"text","default":")[^"]*(")' % key, lambda m: m.group(1) + val + m.group(2), new)
        new = re.sub(r"(%s: this\.props\.%s \?\? ')[^']*(')" % (key, key), lambda m: m.group(1) + val + m.group(2), new)
    if new == s:
        print('変更なし', gold, pt, sv, date)
        return
    open(SRC, 'w', encoding='utf-8').write(new)
    print('更新', gold, pt, sv, date)

if __name__ == '__main__':
    main()
