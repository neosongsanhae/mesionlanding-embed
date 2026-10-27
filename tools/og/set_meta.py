# 버전별 head의 제목·설명·공유(OG·트위터) 태그를 한 형식으로 맞춘다. 본문은 건드리지 않음.
# 실행: 저장소 맨 위에서 python3 tools/og/set_meta.py   (intro.html은 tools/intro/build_intro.py가 관리)
import html, os, re
REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
BASE = 'https://neosongsanhae.github.io/mesionlanding-embed/'
V = 1  # 공유 이미지를 바꾸면 올려서 카카오톡·링크드인 캐시를 갱신
P = {
 'index.html': dict(title='메시온 | 지금, 자사몰 회원의 절반을 놓치고 계십니다',
   desc='지금 메시지가 닿지 않는 자사몰 회원, 우리 브랜드는 얼마를 놓치고 있을까요?',
   og='지금, 자사몰 회원의 절반을 놓치고 계십니다', img='og-index.png'),
 'index-general.html': dict(title=None, desc=None, og='지금, 자사몰 고객 10명 중 7명을 놓치고 계십니다', img='og-general.png',
   alt_extra='카카오톡 채널 친구는, 많아야 10명 중 3명입니다.'),
 'index-app.html': dict(title=None, desc=None, og='회원에게 보낸 앱 푸시, 지금 몇 명이나 볼까요?', img='og-app.png'),
 'index-naver.html': dict(title='매출은 네이버 스마트스토어에서, 홍보는 카카오톡에서? | 메시온',
   desc='네이버 스마트스토어에서 주로 매출이 나는 우리 브랜드, 정작 홍보 메시지는 카카오톡으로 보내고 있나요?',
   og='매출은 네이버 스마트스토어에서, 홍보는 카카오톡에서?', img='og.png'),
 'index-price.html': dict(title='CRM 비용 계산기 | 메시온', desc=None, og=None, img='og-price.png'),
 'index-kisa.html': dict(title=None,
   desc='동의 없이 보내오던 쿠폰·적립금 만료 안내는 이미 광고성(스팸)입니다. 10월 1일부터는 과태료에 매출 과징금까지 더해집니다.',
   og=None, img='og-kisa.png'),
 'about.html': dict(title='메시온 소개 | 세일즈 캠페인 솔루션',
   desc='메시온은 네이버 스마트 톡톡과 카카오 브랜드메시지로 보낼 수 있는 고객을 넓히고 캠페인 기획부터 성과 분석까지 AI 에이전트와 함께하는 세일즈 캠페인 솔루션입니다.',
   og='메시온이란? | 메시온 소개', img='og-about.png'),
 'kisa-crm-guide.html': dict(title='쿠폰 규제 이후 CRM 실무 가이드 | 메시온',
   desc='바뀐 규정부터 헷갈리는 사례, 광고 메시지를 보낼 곳까지. 실제 메시지 사례와 국내외 연구로 정리했어요.',
   og='쿠폰 안내가 광고가 됐어요. 이제 CRM 메시지, 어디로 어떻게 보내야 할까요?', img='og-kisa-guide.png'),
 'ax-receipt.html': dict(title=None, desc=None, og=None, img='og-receipt.png'),
}
for f, d in P.items():
    path = os.path.join(REPO, f); s = open(path, encoding='utf-8').read()
    # kisa-crm-guide.html처럼 <head> 태그 없이 시작하는 파일은 첫 <style> 앞까지를 머리로 봄
    hi = s.index('</head>') if '</head>' in s else s.index('<style>'); head, rest = s[:hi], s[hi:]
    old = lambda pat: (re.search(pat, head) or [None, None])[1] if re.search(pat, head) else None
    title = d['title'] or old(r'<title>(.*?)</title>')
    desc = d['desc'] or old(r'<meta name="description" content="([^"]*)"')
    og = d['og'] or old(r'<meta property="og:title" content="([^"]*)"') or title
    assert title and desc, f
    alt = html.unescape(og) + (' ' + d['alt_extra'] if d.get('alt_extra') else '')
    img = f'{BASE}creatives/{d["img"]}?v={V}'
    e = lambda t: html.escape(html.unescape(t), quote=True)
    block = (f'<title>{e(title)}</title>\n<meta name="description" content="{e(desc)}">\n'
             f'<meta property="og:type" content="website">\n<meta property="og:site_name" content="메시온">\n'
             f'<meta property="og:url" content="{BASE}{f}">\n<meta property="og:title" content="{e(og)}">\n'
             f'<meta property="og:description" content="{e(desc)}">\n<meta property="og:image" content="{img}">\n'
             f'<meta property="og:image:secure_url" content="{img}">\n<meta property="og:image:type" content="image/png">\n'
             f'<meta property="og:image:width" content="1200">\n<meta property="og:image:height" content="630">\n'
             f'<meta property="og:image:alt" content="{e(alt)}">\n<meta property="og:locale" content="ko_KR">\n'
             f'<meta name="twitter:card" content="summary_large_image">\n<meta name="twitter:title" content="{e(og)}">\n'
             f'<meta name="twitter:description" content="{e(desc)}">\n<meta name="twitter:image" content="{img}">')
    # 기존 제목·설명·OG·트위터 태그를 지우고 같은 자리에 새 묶음
    head2 = re.sub(r'[ \t]*<meta (?:name|property)="(?:description|og:[^"]+|twitter:[^"]+)" content="[^"]*">\s*\n?', '', head)
    if '<title>' in head2:
        head2 = re.sub(r'[ \t]*<title>.*?</title>', lambda m: block, head2, count=1, flags=re.S)
    else:
        head2 = re.sub(r'(<meta name="viewport"[^>]*>\n?)', lambda m: m.group(1) + block + '\n', head2, count=1)
    assert head2.count('og:image" content') == 1, f
    open(path, 'w', encoding='utf-8').write(head2 + rest)
    print('ok', f)
