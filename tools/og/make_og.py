# 버전별 공유(오픈그래프) 이미지 원본 HTML을 만든다. 각 페이지 첫 화면 문구 그대로.
# 1) python3 tools/og/make_og.py  → tools/og/<이름>.html
# 2) 각 HTML을 1200x630으로 캡처해 creatives/<이름>.png 로 저장(로컬 서버 http://localhost:8900 기준, shot.mjs 참고)
import html, os
HERE = os.path.dirname(os.path.abspath(__file__))
BLUE, RED = '#3470f0', '#e5484d'
PAGES = {
  'og-index':   dict(kick='', l1='지금, 자사몰 회원의', l2='절반을 놓치고 계십니다.', c=BLUE, sub='우리 브랜드는 얼마를 놓치고 있을까?'),
  'og-general': dict(kick='', l1='지금, 자사몰 고객', l2='10명 중 7명을 놓치고 계십니다.', c=BLUE, sub='카카오톡 채널 친구는, 많아야 10명 중 3명입니다.'),
  'og-app':     dict(kick='', l1='회원에게 보낸 앱 푸시,', l2='지금 몇 명이나 볼까요?', c=BLUE, sub='알림을 꺼두거나 지나치는 회원이 늘면서,<br>공들여 보낸 푸시가 예전만큼 닿지 않고 있진 않나요?'),
  'og-price':   dict(kick='', l1='지금 CRM에,', l2='매달 얼마나 쓰고 계세요?', c=BLUE, sub='매달 나가는 이용료에, 보낼 때마다 붙는 발송 단가까지.<br>메시온은 월 이용료 없이, 발송한 만큼만 냅니다.'),
  'og-receipt': dict(kick='발송비 리포트 예시', l1='우리 브랜드 발송비,', l2='메시온으로 얼마나 줄어들까요?', c=BLUE, sub='카톡 채널 친구 수 기준으로 타사 CRM과 메시온의<br>한 달 발송비를 비교한 영수증입니다.'),
  'og-about':   dict(kick='메시온 소개', l1='메시온이란?', l2='', c=BLUE, sub='네이버 스마트 톡톡과 카카오 브랜드메시지로 보낼 수 있는 고객을 넓히고<br>캠페인 기획부터 성과 분석까지 AI 에이전트와 함께하는 세일즈 캠페인 솔루션입니다.'),
  'og-kisa-guide': dict(kick='정보통신망법 개정 · 2026년 10월 과징금 시행', kc='red', l1='쿠폰 안내가 광고가 됐어요.', l2='이제 CRM 메시지, 어디로 어떻게 보내야 할까요?', c=RED, small=True, sub='바뀐 규정부터 헷갈리는 사례, 광고 메시지를 보낼 곳까지.<br>실제 메시지 사례와 국내외 연구로 정리했어요.'),
}
TPL = '''<!doctype html><html><head><meta charset="utf-8">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/variable/pretendardvariable.min.css">
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
body{{width:1200px;height:630px;overflow:hidden;font-family:"Pretendard Variable",Pretendard,sans-serif;letter-spacing:-.03em;color:#1a1c22;
 background:radial-gradient(70% 90% at 92% 0%,{bg} 0%,#f6f8fd 50%,#fff 100%)}}
.w{{height:100%;padding:62px 72px 70px;display:flex;flex-direction:column}}
.logo{{height:34px;width:auto;align-self:flex-start}}
.m{{margin-top:auto}}
.kick{{display:inline-block;margin-bottom:24px;font-size:22px;font-weight:700;color:{kcol};background:{kbg};border-radius:999px;padding:9px 20px}}
h1{{font-size:{fs}px;font-weight:800;line-height:1.24;letter-spacing:-.045em}}
h1 em{{font-style:normal;color:{c}}}
.sub{{margin-top:28px;font-size:25px;line-height:1.55;font-weight:500;color:#4a4e57}}
</style></head><body><div class="w">
<img class="logo" src="../../creatives/intro/50db884207e5.webp" alt="">
<div class="m">{kick}<h1>{l1}{br}<em>{l2}</em></h1><p class="sub">{sub}</p></div>
</div></body></html>'''
for name, d in PAGES.items():
    red = d.get('kc') == 'red'
    kick = f'<span class="kick">{html.escape(d["kick"])}</span>' if d['kick'] else ''
    out = TPL.format(bg='#fde6e7' if red else '#e3ebfd', kcol='#c2343a' if red else '#2455c7', kbg='#fdeeee' if red else '#eaf0fe',
                     fs=52 if d.get('small') else 64, c=d['c'], kick=kick, l1=d['l1'], br='<br>' if d['l2'] else '', l2=d['l2'], sub=d['sub'])
    open(os.path.join(HERE, name + '.html'), 'w', encoding='utf-8').write(out)
print('ok', len(PAGES))
