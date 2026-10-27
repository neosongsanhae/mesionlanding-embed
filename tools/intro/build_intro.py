# 소개서 덱(tools/intro/mesion_intro_deck.html) → 세로 스크롤 웹 소개 페이지(intro.html)
# 실행: 저장소 맨 위에서  python3 tools/intro/build_intro.py
# 내용·요소는 덱(=PDF) 그대로 두고, 스크롤 배치·반응형·간단한 애니메이션만 더한다.
import base64, hashlib, os, re

# 저장소 안에서만 동작: tools/intro/ 에 덱 원본과 이 스크립트, 결과는 저장소 맨 위 intro.html
HERE = os.path.dirname(os.path.abspath(__file__))
DECK = os.path.join(HERE, 'mesion_intro_deck.html')
REPO = os.path.abspath(os.path.join(HERE, '..', '..'))
OUT = f'{REPO}/intro.html'
IMG_DIR = 'creatives/intro'
URL = 'https://neosongsanhae.github.io/mesionlanding-embed/intro.html'
# PostHog(방문·리드 분석). 키가 비어 있으면 스크립트를 넣지 않음. phc_ 키는 웹에 공개되는 용도라 커밋해도 됨
POSTHOG_KEY = 'phc_DmKZTzeFEhLd7TQNjkk2cib9GZaUCuQFSXvSDGBZ4ma8'
POSTHOG_HOST = 'https://us.i.posthog.com'  # EU 프로젝트면 https://eu.i.posthog.com

src = open(DECK, encoding='utf-8').read()
os.makedirs(f'{REPO}/{IMG_DIR}', exist_ok=True)

EXT = {'image/webp': 'webp', 'image/png': 'png', 'image/jpeg': 'jpg', 'image/svg+xml': 'svg', 'image/gif': 'gif'}


def externalize(html):
    """base64 이미지를 파일로 빼고 상대 경로로 바꿈"""
    def rep(m):
        mime, data = m.group(1), m.group(2)
        raw = base64.b64decode(data)
        name = hashlib.sha1(raw).hexdigest()[:12] + '.' + EXT[mime]
        path = f'{REPO}/{IMG_DIR}/{name}'
        if not os.path.exists(path):
            open(path, 'wb').write(raw)
        return f'{IMG_DIR}/{name}'
    return re.sub(r'data:(image/(?:webp|png|jpeg|svg\+xml|gif));base64,([A-Za-z0-9+/=]+)', rep, html)


# ---- 덱 조각 ----
css_start = src.index('<style>\n:root')
deck_css = src[css_start + 7:src.index('</style>', css_start)]

body = src[src.index('<div class="deck" id="deck">'):src.index('<div class="nav"')]
parts = body.split('<section class="slide')[1:]
sections = {}
order = []
for p in parts:
    sec = '<section class="slide' + p[:p.index('</section>') + 10]
    label = re.search(r'aria-label="([^"]+)"', sec).group(1)
    sections[label] = sec
    order.append(label)

topbar = src[src.index('<div class="topbar">'):src.index('<div class="pbar">')]
logo = re.search(r'<img src="([^"]+)" alt="Mesion">', topbar).group(1)


def inner(sec, cls):
    m = re.search(r'<[a-z0-9]+ class="' + cls + r'"[^>]*>(.*?)</', sec, re.S)
    return m.group(1) if m else ''


# ---- AX 1~4 → 한 화면 슬라이드: ax-receipt.html의 AX 블록을 그대로 가져옴(클래스만 덱과 안 겹치게 q로 바꿈) ----
ax_labels = [l for l in order if l.startswith('AX ') and l != 'AX 답']
rc = open(f'{REPO}/ax-receipt.html', encoding='utf-8').read()
AXREN = {'axv2': 'qax', 'axl': 'qal', 'axs': 'qas', 'axh': 'qah', 'axf': 'qaf', 'axt': 'qat', 'axc': 'qac', 'mdsc': 'qmd'}


def axren(t):
    return re.sub(r'\b(axv2|axl|axs|axh|axf|axt|axc|mdsc)\b', lambda m: AXREN[m.group(1)], t)


i = rc.index('<div class="axv2" id="ax">')
j = rc.index('<span class="axc">', i)
j = rc.index('</div>\n      </div>', j) + len('</div>\n      </div>')
ax_block = axren(rc[i:j]).replace('<span class="qac">예시 화면</span>', '<span class="qac">(예시 화면)</span>')
ax_css = axren(rc[rc.index('/* AX 4단계 (소개서 13~16p) */'):rc.index('/* 가격표 (소개서 20p) */')])
_r = rc[rc.index('/* receipt hero'):rc.index('.sales{')]
rc_css = '\n'.join(l for l in _r.split('\n') if not l.startswith(('.rcv{', '.rcv .kick', '.rcv h1', '#rSave', '.rcv .lede', '.mesion .rmeta')))
k = rc.index('/* AX 4단계: 5초마다')
ax_js = axren(rc[rc.rindex('<script>', 0, k):rc.index('</script>', k) + 9])
# 마우스를 올리면 멈추는 동작은 뺌: AX 영역이 넓어 스크롤 중 마우스가 늘 위에 있어서 자동 넘김이 멈춰 있었음
ax_js = re.sub(r"\n\s*root\.addEventListener\('mouse(?:enter|leave)'.*", '', ax_js)
assert 'mouseenter' not in ax_js
# 단계 제목은 ax-receipt처럼 화면 위가 아니라, 다른 섹션과 같은 자리(kick 아래 h2)에 둠(10/28 요청)
_qh = re.search(r'<div class="qah">(.*?)</div>', ax_block, re.S)
ax_titles = re.sub(r'<h4( class="on")?>(.*?)<span>(.*?)</span></h4>', lambda m: f'<h2 class="t one{" on" if m.group(1) else ""}">{m.group(2)}<span class="em">{m.group(3)}</span></h2>', _qh.group(1))
ax_block = ax_block.replace(_qh.group(0), '')
ax_js = ax_js.replace("hs=root.querySelectorAll('.qah h4')", "hs=document.querySelectorAll('.qah .t')").replace("root.querySelector('.qah').after(md)", "root.querySelector('.qaf').before(md)")
assert ".qah .t" in ax_js and ".qaf').before" in ax_js
ax_section = f"""<section class="slide" aria-label="메시온 AX 4단계">
  <div class="stage">
    <span class="kick so">메시온 AX</span>
    <div class="qah">{ax_titles}</div>
    <div class="body anim">{ax_block}</div>
  </div>
</section>"""

# ---- 비용 비교 → 영수증 ----
cost = sections['비용 비교']


def num(t):
    return int(re.sub(r'[^\d]', '', t) or 0)


def rows_of(cls_src):
    blk = re.search(r'<div class="rq ' + cls_src + r'">(.*?)<div class="rqt">(.*?)</div>', cost, re.S)
    rows = [r for r in re.findall(r'<div class="rql( [a-z]+)?"><span>(.*?)</span><span>(.*?)</span><span>(.*?)</span><span>(.*?)</span></div>', blk.group(1)) if r[0].strip() != 'hd']
    cnt = re.search(r'<div class="rqs"><span>(.*?)</span><b>(.*?)</b></div>', blk.group(1))
    tot = re.search(r'<span>(.*?)</span><b>(.*?)</b>', blk.group(2))
    return rows, cnt, tot


KEYS = ['fr', 'nf', 'np']
o_rows, o_cnt, o_tot = rows_of('ot')
m_rows, m_cnt, m_tot = rows_of('me')
st = re.search(r'<div class="rst"[^>]*><b>(.*?)</b><span>(.*?)</span></div>', cost)


def receipt(rows, cnt, tot, name, cls, other=None):
    trs = ''
    for n, (kind, a, b, c, d) in enumerate(rows):
        kind, key = kind.strip(), KEYS[n]
        tc = {'no': 'na', 'add': 'gr'}.get(kind, '')
        c_td = f'<td class="no">{c}</td>' if kind == 'no' else f'<td>{c}</td>'
        amt = f'<span data-v="{num(d)}">{d}</span>' if num(d) else d
        dl = ''
        if other is not None:
            od = num(other[n][4])
            dl = f'<i class="dlt plus">+{b} 발송</i>' if not od else f'<i class="dlt">−{od - num(d):,}원</i>'
        trs += f'<tr data-row="{key}"{f" class={chr(34)}{tc}{chr(34)}" if tc else ""}><td>{a}</td><td>{b}</td>{c_td}<td>{dl}{amt}</td></tr>'
    stamp = f'<div class="stamp"><b data-pct="{num(st.group(1))}">{st.group(1)}</b><span>{st.group(2)}</span></div>' if cls == 'mesion' else ''
    return (f'<div class="rcpt {cls}">{stamp}<div class="rh">{name}</div>'
            f'<table><thead><tr><th>매체 · 대상</th><th>인원</th><th>단가</th><th>금액</th></tr></thead><tbody>{trs}</tbody></table>'
            f'<div class="rcnt"><span>{cnt.group(1)}</span><b>{cnt.group(2)}</b></div>'
            f'<div class="rtot"><span>{tot.group(1)}</span><b data-v="{num(tot.group(2))}">{tot.group(2)}</b></div></div>')


rcpts = receipt(o_rows, o_cnt, o_tot, '타사 CRM', 'other') + receipt(m_rows, m_cnt, m_tot, '메시온', 'mesion', o_rows)
once = num(o_tot.group(2)) - num(m_tot.group(2))
rxs = re.search(r'<p class="rxs">(.*?)</p>', cost, re.S).group(1)
# PDF 문장: "1회 421.5만 원, 월 4회면 1년에 약 2억 232만 원 차이입니다.<br>지금 보내시는 단가로 계산해 드릴까요?"
line1, line2 = rxs.split('<br>')
m1 = re.match(r'1회 <b>(.*?)</b>, 월 4회면 1년에 <b>약 (.*?)</b> 차이입니다\.', line1)
assert m1, line1
seg = '<span class="seg" id="rSeg" role="group" aria-label="월 발송 횟수"><button type="button" data-t="1">1회</button><button type="button" data-t="2">2회</button><button type="button" data-t="4" class="on">4회</button><i></i></span>'
# '지금 보내시는 단가로 계산해 드릴까요?'는 뺌(10/28 요청), 두 줄: '1회 ~, 월 n회면' / '1년에 약 ~ 차이입니다.'
rsum = (f'<div class="rsum" data-once="{once}"><p>1회 <b>{m1.group(1)}</b>, 월 {seg}면</p>'
        f'<p>1년에 <b>약 <span id="rYear">{m1.group(2)}</span></b> 차이입니다.</p></div>')
cost_new = re.sub(r'<div class="body rx anim">.*?</div>\s*<p class="rxs">.*?</p>', f'<div class="body"><div class="rcpts">{rcpts}</div>{rsum}</div>', cost, flags=re.S)
cost_new = cost_new.replace('<section class="slide', '<section class="slide rcv', 1)
assert cost_new != cost

# ---- 고객사·투자사 로고 → index.html의 로고 마퀴 방식 그대로 ----
def marquee(one, dur):
    half = one + one
    return f'<div class="cmq"><div class="ctk" style="--cd:{dur}s">{half}<span class="cdup" aria-hidden="true">{half}</span></div></div>'


fin = sections['문의']
a = fin.index('<div class="lgx6">')
b = fin.index('</div></div></div>', a) + len('</div></div></div>')
imgs = re.findall(r'<img src="([^"]+)" alt="([^"]+)"', fin[a:b])
one = ''.join(f'<span class="clg"><img class="clgimg" src="{src}" alt="{alt}"></span>' for src, alt in imgs)
# 문의 장 배치: 글은 위, 고객사 띠는 아래 전체 폭(index.html의 고객사 띠처럼)
sections['문의'] = fin[:a] + fin[b:].replace('</div>\n</section>', f'<div class="cred"><span class="fk2">주요 고객사</span>{marquee(one, 22)}</div>\n  </div>\n</section>', 1)

pt = sections['파트너']
# 투자사 로고 띠: 천천히 흐르도록 기본 속도의 1.8배 시간
a = pt.index('<div class="ivg">')
b = pt.index('</div></div>', a) + len('</div>')
ivs = re.findall(r'<span class="ivs">(.*?)</span>', pt[a:b], re.S)
one = ''.join(f'<span class="clg">{x.replace("<img ", "<img class=\"clgimg iv\" ")}</span>' for x in ivs)
sections['파트너'] = pt[:a] + '<div class="ivmq">' + marquee(one, round(len(ivs) * 2 * 24 / 44 * 1.8)) + '</div>' + pt[b:]

# 폰 목업 섹션 제목([N]은 네이버 로고 자리)
PHONE_H2 = '여러 매체를 통합해 [K][N]<br>고객과 더 자주 만나보세요'  # [K]·[N]: 카카오톡·네이버 공식 앱 로고(brand-assets와 같은 파일)

# ---- 매체 통합: '매체를 넓히면' 제목 아래로 '나눠 보내기' 도표를 올리고, 원래 화면 3개는 폰 목업 섹션으로 ----
r7sec = sections['역할 분담']
r7_h2 = re.search(r'<h2 class="t">.*?</h2>', r7sec, re.S).group(0)
sections['나눠 보내기'] = re.sub(r'<h2 class="t">.*?</h2>', lambda m: r7_h2, sections['나눠 보내기'], count=1, flags=re.S)
shots = re.findall(r'<figcaption class="p7l">(.*?)</figcaption><div class="r7s r7img([^"]*)"[^>]*><img src="([^"]+)"', r7sec)
assert len(shots) == 3, shots
shots = [(('카카오 브랜드메시지' if cap == '카카오톡 브랜드메시지' else cap), cls, src) for cap, cls, src in shots]  # 매체 이름 표기(10/28)
NSVG = '<svg viewBox="0 0 24 24"><path d="M16.273 12.845 7.376 0H0v24h7.727V11.155L16.624 24H24V0h-7.727v12.845z" fill="#fff"/></svg>'
chips = ''.join(f'<button type="button" class="pcp{" on" if i == 0 else ""}" data-i="{i}">{cap}</button>' for i, (cap, _, _) in enumerate(shots))
pimgs = ''.join(f'<img class="pvi{cls}{" on" if i == 0 else ""}" src="{src}" alt="{cap} 화면 예시"{"" if i == 0 else " loading=\"lazy\""}>' for i, (cap, cls, src) in enumerate(shots))
phone_section = f"""<section class="slide aha2" aria-label="매체 3곳 화면">
  <div class="stage">
    <div class="ahl">
    <h2 class="aha-h">{PHONE_H2.replace('[K]', '<img class="hlogo" src="creatives/axp/a1207eb6a9.webp" alt="카카오톡">').replace('[N]', '<img class="hlogo" src="creatives/axp/40a22b9f91.webp" alt="네이버">')}</h2>
    <div class="pcps" role="group" aria-label="매체 고르기">{chips}</div>
    </div>
    <div class="aphone" id="aphone">
      <div class="aphone-frame"><div class="aphone-screen">
        <div class="aphone-island"></div>
        <div class="pvw">{pimgs}</div>
      </div></div>
    </div>
  </div>
</section>"""

# ---- 리드 폼(문의 장 오른쪽 + 상단 버튼 팝업 공용) ----
KF = ['~1만', '~5만', '~10만', '~20만', '20만 이상']


def lead_form(pre):
    kfs = ''.join(f'<button type="button" data-v="{v}">{v}</button>' for v in KF)
    return f"""<div class="ldform" data-pre="{pre}">
        <div class="ldbody">
          <h3>상담 신청</h3>
          <p class="ldfs">영업일 기준 하루 안에 담당자가 연락드립니다.</p>
          <label class="ldl" for="{pre}Brand">기업명</label>
          <input class="ldi" id="{pre}Brand" placeholder="예) 메시온" autocomplete="organization">
          <label class="ldl" for="{pre}Name">담당자명</label>
          <input class="ldi" id="{pre}Name" placeholder="예) 홍길동" autocomplete="name">
          <label class="ldl" for="{pre}Phone">연락처</label>
          <input class="ldi" id="{pre}Phone" placeholder="01012345678 (숫자만)" inputmode="numeric" autocomplete="tel">
          <span class="ldl" id="{pre}KfL">카카오톡 채널 친구 수</span>
          <div class="ldkf" role="group" aria-labelledby="{pre}KfL">{kfs}</div>
          <p class="lderr">기업명·담당자명·연락처·친구 수를 모두 입력해 주세요.</p>
          <button class="ldbtn" type="button">상담 신청하기</button>
        </div>
        <div class="lddone">
          <div class="ldok">✓</div>
          <h3>신청이 접수됐습니다</h3>
          <p>영업일 기준 하루 안에 담당자가 연락드리겠습니다.</p>
        </div>
      </div>"""


fin = sections['문의']
fa = fin.index('<div class="stage fin2">\n    <div>') + len('<div class="stage fin2">\n    ')
fb = fin.index('\n    </div>', fa) + len('\n    </div>')
sections['문의'] = fin[:fa] + '<div class="apply">' + fin[fa:fb] + '\n      ' + lead_form('b') + '\n    </div>' + fin[fb:]
sections['문의'] = sections['문의'].replace('<section class="slide fin"', '<section class="slide fin" id="apply"', 1)

# ---- 순서·배경 교차 ----
# 현재 CRM의 문제를 다룬 장은 빼고 제품 설명 위주로(10/27 요청)
SKIP = {'한계 한눈에', '환경 변화', '담당자 리소스', '질문 1', '질문 3'}
out_secs = []
k = 0
for l in order:
    if l in SKIP:
        continue
    if l in ax_labels:
        if l != ax_labels[0]:
            continue
        sec = ax_section
    elif l == '비용 비교':
        sec = cost_new
    elif l == '나눠 보내기':
        continue
    elif l == '역할 분담':
        sec = sections['나눠 보내기']
    else:
        sec = sections[l]
    m = re.match(r'<section class="([^"]+)"', sec)
    cls = [c for c in m.group(1).split() if c != 'alt']
    if not ({'cover', 'qs', 'fin', 'aha2'} & set(cls)):
        if k % 2 == 1:
            cls.append('alt')
        k += 1
    sec = f'<section class="{" ".join(cls)}"' + sec[m.end():]
    out_secs.append(sec)
    if l == '역할 분담':
        out_secs.append(phone_section)

# ---- 스크롤 페이지용 CSS ----
web_css = r'''
/* ===== 웹 페이지(세로 스크롤) ===== */
html,body{height:auto;overflow:visible}
html,body{overflow-x:clip}
html{scroll-behavior:smooth;scroll-padding-top:56px}
body{line-height:1.5}
.topbar a{display:block}
.deck{position:static;display:block;overflow:visible}
#deck>.slide{flex:none;width:auto;height:auto;min-height:0;display:flex;align-items:flex-start!important;justify-content:center;overflow:visible;
  padding:clamp(64px,6.5vw,92px) clamp(18px,5vw,72px)!important}
#deck>.slide.cover{min-height:min(calc(100svh - 70px),520px);align-items:center!important;padding-top:clamp(88px,8vw,112px)!important;padding-bottom:clamp(40px,4vw,56px)!important}
#deck>.slide.cover .cv{margin-inline:auto;text-align:center}#deck>.slide.cover .cv .lead{margin-inline:auto}
#deck .kick{display:none}
#deck>.slide.cover+.slide{padding-top:clamp(48px,4.5vw,64px)!important}
#deck>.slide.qs{padding:clamp(72px,7vw,100px) clamp(18px,5vw,72px)!important;align-items:center!important}
#deck>.slide.fin{padding-bottom:clamp(80px,7.5vw,108px)!important}
#deck>.slide .stage{zoom:normal}
.nav{display:none}
/* 나타나기 */
.js #deck>.slide .anim{opacity:0;transform:translateY(22px);transition:opacity .7s var(--ease),transform .9s var(--ease)}
.js #deck>.slide.on .anim{opacity:1;transform:none}
.js #deck>.slide.on .anim+.anim{transition-delay:.12s}
.js #deck>.slide .stage>.kick,.js #deck>.slide .stage>.t,.js #deck>.slide .stage>.lead,.js #deck>.slide .stage>.qsub{transition:opacity .6s var(--ease),transform .7s var(--ease)}
.js #deck>.slide:not(.on) .stage>.kick,.js #deck>.slide:not(.on) .stage>.t,.js #deck>.slide:not(.on) .stage>.lead,.js #deck>.slide:not(.on) .stage>.qsub{opacity:0;transform:translateY(14px)}
@media(prefers-reduced-motion:reduce){.js #deck>.slide .anim,.js #deck>.slide .stage>*{opacity:1!important;transform:none!important}}
/* 화면 높이에 묶여 있던 크기 풀기 */
.slide[aria-label="역할 분담"] .r7s{height:380px}
@media(max-width:900px){.slide[aria-label="역할 분담"] .r7s{height:auto}}
/* 모바일: 네이버페이 비회원 구매자 도식은 PC 모양 그대로 두고 옆으로 밀어서 봄(세로로 쌓으면 화살표·원이 겹쳐 깨짐) */
@media(max-width:900px){
  .slide[aria-label="비회원 구매자"] .h9{grid-template-columns:auto 132px auto 132px auto!important;overflow-x:auto;-webkit-overflow-scrolling:touch;
    margin:22px -18px 0;padding:96px 18px 12px;scrollbar-width:thin}
  .slide[aria-label="비회원 구매자"] .h9r{height:180px;transform:none!important}
  .slide[aria-label="비회원 구매자"] .h9n{min-width:max-content}
  .slide[aria-label="비회원 구매자"] .h9>*{zoom:.82}
}
/* 모바일: 영수증 차액 칩이 단가 칸을 덮지 않게 작게 */
@media(max-width:560px){.rcpt .dlt{font-size:10.5px;padding:2px 7px;right:0}}
/* 모바일: 해결 요약 두 칸은 위아래로, 로고는 작게 */
@media(max-width:700px){
  .y6{grid-template-columns:1fr!important;row-gap:4px}
  .y6o{padding:2px 0}
  .z6lg{gap:8px;min-height:96px}
  .z6lg img{width:52px;height:52px}
  .z6lg i{font-size:18px}
  /* 넓은 표는 옆으로 밀어서 봄 */
  .slide[aria-label="나눠 보내기"] .body,.slide[aria-label="요금과 도입"] .body{overflow-x:auto;-webkit-overflow-scrolling:touch;margin:0 -18px;padding:14px 18px 10px}
  .slide[aria-label="나눠 보내기"] .cov,.slide[aria-label="요금과 도입"] .qt{min-width:660px}
  .slide[aria-label="나눠 보내기"] .cov{margin-top:20px}
}

/* ===== ax-receipt.html에서 가져온 부분 ===== */
:root{--red:#e5484d;--red-d:#c2343a;--red-t:#fdeeee;--shadow:0 1px 2px rgba(20,24,40,.04),0 8px 22px -12px rgba(20,24,40,.14)}
''' + ax_css + rc_css + r'''
.slide.rcv .rsum{margin-top:30px}
.qah .t{grid-area:1/1;opacity:0;transform:translateY(10px);transition:opacity .4s,transform .5s var(--ease);pointer-events:none}
.qah .t.on{opacity:1;transform:none;pointer-events:auto}
.qas .qmd{margin-bottom:2px}
.js .rcv:not(.play) .rcpt{opacity:0}

/* ===== 고객사·투자사 로고: index.html 로고 마퀴 ===== */
.cmq{overflow:hidden;margin-top:40px;-webkit-mask-image:linear-gradient(90deg,transparent,#000 12%,#000 88%,transparent);mask-image:linear-gradient(90deg,transparent,#000 12%,#000 88%,transparent)}
.ctk{display:flex;gap:52px;width:max-content;animation:cslide var(--cd,24s) linear infinite}
.cdup{display:contents}
@keyframes cslide{to{transform:translateX(-50%)}}
.clg{display:inline-flex;align-items:center;flex:none}
.clgimg{height:30px;width:auto;max-width:150px;object-fit:contain;filter:grayscale(1);opacity:.55;transition:filter .25s,opacity .25s}
.cmq:hover .clgimg{filter:none;opacity:1}
@media(prefers-reduced-motion:reduce){.ctk{animation:none;flex-wrap:wrap;width:auto;justify-content:center;row-gap:20px}.cdup{display:none}.cmq{-webkit-mask-image:none;mask-image:none}}
.slide.fin .fin2{display:block!important}
@media(max-width:900px){.slide.fin .lead{white-space:normal}.qas .qmd{display:block}}
.slide.fin .cred{margin-top:clamp(48px,6vw,72px);padding-top:clamp(32px,4vw,44px);border-top:1px solid var(--line2);text-align:center}
.slide.fin .cred .fk2{font-size:13px;font-weight:800;color:var(--muted);letter-spacing:.04em}
.slide.fin .cred .cmq{margin-top:26px}
.slide[aria-label="파트너"] .ivmq{min-width:0}
.slide[aria-label="파트너"] .ivmq .cmq{margin-top:0}
.slide[aria-label="파트너"] .ivmq .clgimg.iv{height:auto;max-width:none;transform:none!important;filter:grayscale(1)!important;opacity:.55!important}
.slide[aria-label="파트너"] .ivmq .cmq:hover .clgimg.iv{filter:none!important;opacity:1!important}
@media(max-width:900px){.slide[aria-label="파트너"] .ivr{grid-template-columns:1fr!important;gap:16px}.slide[aria-label="파트너"] .pt5{grid-template-columns:minmax(0,1fr) minmax(0,1fr)!important;gap:10px!important}.slide[aria-label="파트너"] .ptc{min-width:0;padding-left:12px;padding-right:12px}.slide[aria-label="파트너"] .ptc:last-child{grid-column:1/-1}.slide[aria-label="파트너"] .ptl img{max-width:100%;height:auto}}


/* ===== 매체 3곳 화면: index-naver 전환 섹션 방식, 폰 안에서 화면이 바뀜 ===== */
#deck>.slide.aha2{background:#15171c;text-align:center;padding-top:clamp(96px,10vw,128px)!important;padding-bottom:clamp(104px,11vw,136px)!important}
.aha2 .stage{display:grid;grid-template-columns:minmax(0,1fr) auto;align-items:center;column-gap:clamp(40px,7vw,110px);text-align:left}
@media(min-width:901px){.aha2 .aphone{margin-right:clamp(24px,4vw,64px)}}
.aha2 .ahl{display:flex;flex-direction:column;align-items:flex-start}
.aha2 .aphone{margin-top:0}
@media(max-width:900px){.aha2 .stage{grid-template-columns:1fr;justify-items:center;text-align:center}.aha2 .ahl{align-items:center}.aha2 .aphone{margin-top:36px}}
.aha-h{font-size:clamp(26px,3.4vw,44px);font-weight:800;letter-spacing:-.035em;line-height:1.34;color:#fff;text-wrap:balance}
.hlogo{display:inline-block;width:.92em;height:.92em;border-radius:24%;vertical-align:-.12em;margin-left:.22em;box-shadow:0 6px 16px -6px rgba(0,0,0,.6)}
.hlogo+.hlogo{margin-left:.16em}
.nlogo{display:inline-flex;align-items:center;justify-content:center;width:.82em;height:.82em;background:#03C75A;border-radius:23%;vertical-align:-.04em;margin:0 .16em}
.nlogo svg{width:56%;height:56%;display:block}
.pcps{margin-top:34px;display:inline-flex;gap:6px;padding:5px;border-radius:999px;background:rgba(255,255,255,.08);border:1px solid rgba(255,255,255,.1)}
.pcp{border:0;background:none;cursor:pointer;font-size:14px;font-weight:700;color:#9aa1b0;padding:9px 16px;border-radius:999px;transition:background .3s,color .3s;white-space:nowrap}
.pcp.on{background:#fff;color:#15171c}
.pcp:not(.on):hover{color:#fff}
.aphone{margin-top:40px;position:relative;width:310px;max-width:86vw}
.aphone::after{content:"";position:absolute;left:50%;bottom:-34px;width:72%;height:56px;transform:translateX(-50%);background:radial-gradient(ellipse at center,rgba(0,0,0,.6),transparent 70%);filter:blur(7px);z-index:-1}
.aphone-frame{position:relative;width:100%;aspect-ratio:380/660;background:linear-gradient(152deg,#42454d,#161719 44%);border-radius:47px;padding:11px;box-shadow:inset 0 2px 0 1px rgba(255,255,255,.07),inset 0 0 0 1px rgba(0,0,0,.5),0 36px 74px -26px rgba(0,0,0,.9);-webkit-mask-image:linear-gradient(to bottom,#000 62%,transparent 96%);mask-image:linear-gradient(to bottom,#000 62%,transparent 96%)}
.aphone-screen{position:relative;width:100%;height:100%;border-radius:37px;overflow:hidden;background:#fff}
.aphone-island{position:absolute;top:13px;left:50%;transform:translateX(-50%);width:88px;height:26px;background:#000;border-radius:16px;z-index:7}
.pvw{position:absolute;inset:0;padding-top:46px;background:#fff}
.pvi{position:absolute;left:0;right:0;top:46px;width:100%;height:calc(100% - 46px);object-fit:cover;object-position:center top;opacity:0;transform:translateY(16px) scale(.985);transition:opacity .4s var(--ease),transform .55s var(--ease)}
.pvi.on{opacity:1;transform:none}
.pvi.ka2{background:#b2c7d9}
@media(max-width:560px){.pcp{font-size:12.5px;padding:8px 11px}}
/* 배경을 검정 대신 짙은 회색으로, 그림자는 옅게(10/28 가독성 요청) */
#deck>.slide.aha2{background:#3a3d45}
.pcps{background:rgba(255,255,255,.1);border-color:rgba(255,255,255,.14)}
.pcp{color:#c7cbd4}
.pcp.on{color:#2a2c32}
.aphone::after{background:radial-gradient(ellipse at center,rgba(0,0,0,.28),transparent 70%)}
.aphone-frame{box-shadow:inset 0 2px 0 1px rgba(255,255,255,.07),inset 0 0 0 1px rgba(0,0,0,.5),0 30px 60px -30px rgba(0,0,0,.45)}
/* 하단 페이드 없이 폰 전체를 보여 줌(10/28 요청) */
.aphone-frame{-webkit-mask-image:none;mask-image:none}
.aphone::after{bottom:-22px}

/* ===== 상담 신청: ax-promo 신청 영역·상단 버튼 방식 ===== */
.topbar .tcta{font-family:inherit;font-size:13px;font-weight:700;color:#fff;background:var(--blue);border:0;border-radius:999px;padding:8px 15px;cursor:pointer}
.topbar .tcta:hover{background:var(--blue-d)}
/* 다른 홈페이지와 같은 '메시온 소개' 링크 */
.topbar .navlink{font-size:14px;font-weight:600;color:var(--ink2);text-decoration:none;white-space:nowrap;margin-right:6px;transition:color .15s}
.topbar .navlink:hover{color:var(--blue)}
@media(max-width:600px){.topbar .navlink{display:none}}
.slide.fin .apply{display:grid;grid-template-columns:1fr 1fr;gap:36px;align-items:center}
.slide.fin .lead{white-space:normal!important}
@media(max-width:900px){.slide.fin .apply{grid-template-columns:1fr;gap:28px}}
.ldform{background:#fff;border:1px solid var(--line);border-radius:20px;padding:24px;box-shadow:0 18px 40px -22px rgba(20,24,40,.3);text-align:left}
.ldform h3{font-size:19px;font-weight:800;letter-spacing:-.03em;margin-bottom:4px;color:var(--ink)}
.ldfs{font-size:13.5px;color:var(--muted);margin-bottom:16px}
.ldl{display:block;font-size:13px;font-weight:700;color:var(--ink2);margin:12px 0 6px}
.ldi{width:100%;font-family:inherit;font-size:15px;color:var(--ink);background:var(--paper2);border:1px solid var(--line);border-radius:12px;padding:13px 14px;outline:0;transition:border-color .15s,background .15s}
.ldi:focus{border-color:var(--blue);background:#fff}
.ldkf{display:flex;flex-wrap:wrap;gap:6px}
.ldkf button{font-family:inherit;font-size:14px;font-weight:700;color:var(--ink2);background:var(--paper2);border:1px solid var(--line);border-radius:999px;padding:9px 14px;cursor:pointer;transition:background .15s,color .15s,border-color .15s}
.ldkf button:hover{border-color:var(--line2)}
.ldkf button.on{background:var(--blue);border-color:var(--blue);color:#fff}
.lderr{display:none;font-size:12.5px;color:var(--red-d);font-weight:600;margin-top:10px}
.lderr.on{display:block}
.ldbtn{display:flex;width:100%;margin-top:18px;align-items:center;justify-content:center;font-family:inherit;font-size:15px;font-weight:700;color:#fff;background:var(--blue);border:0;border-radius:999px;padding:14px 26px;cursor:pointer;transition:background .15s,transform .15s;box-shadow:0 10px 24px -10px rgba(36,85,199,.6)}
.ldbtn:hover{background:var(--blue-d);transform:translateY(-1px)}
.ldbtn:disabled{opacity:.6;cursor:default;transform:none}
.ldbtn:focus-visible,.ldi:focus-visible,.ldkf button:focus-visible,.tcta:focus-visible{outline:2px solid var(--blue);outline-offset:2px}
.lddone{display:none;text-align:center;padding:20px 0}
.ldok{width:52px;height:52px;border-radius:50%;background:var(--blue);color:#fff;font-size:24px;font-weight:800;display:grid;place-items:center;margin:0 auto 14px}
.lddone h3{margin-bottom:6px}
.lddone p{font-size:14px;color:var(--muted)}
.ldform.sent .ldbody{display:none}
.ldform.sent .lddone{display:block}
/* 상단 버튼 팝업 */
.ldm{position:fixed;inset:0;z-index:100;display:grid;place-items:center;padding:16px}
.ldm[hidden]{display:none}
.ldm-bg{position:absolute;inset:0;background:rgba(15,18,28,.5);backdrop-filter:blur(4px);-webkit-backdrop-filter:blur(4px);animation:ldFade .25s ease both}
.ldm-box{position:relative;width:min(420px,100%);max-height:calc(100dvh - 32px);overflow:auto;animation:ldUp .4s var(--ease) both;border-radius:20px}
.ldm-box .ldform{box-shadow:0 30px 70px -20px rgba(0,0,0,.45)}
.ldm-x{position:absolute;top:12px;right:12px;z-index:2;width:34px;height:34px;border-radius:50%;border:0;background:var(--paper2);font-size:20px;line-height:1;color:var(--muted);cursor:pointer}
@keyframes ldFade{from{opacity:0}}
@keyframes ldUp{from{opacity:0;transform:translateY(24px) scale(.98)}}
@media(max-width:560px){.ldm{place-items:end center;padding:0}.ldm-box{width:100%;border-radius:20px 20px 0 0}.ldm-box .ldform{border-radius:20px 20px 0 0}}

/* 푸터 */
.gfoot{background:var(--paper);border-top:1px solid var(--line);padding:36px clamp(18px,5vw,72px) 44px}
.gfoot .in{width:min(1080px,100%);margin:0 auto;font-size:12.5px;line-height:1.75;color:var(--muted)}
.gfoot a{color:inherit}
'''

script = r'''<script>
(function(){
  document.documentElement.classList.add('js');
  var pfill=document.getElementById('pfill');
  function sync(){var h=document.documentElement;var max=h.scrollHeight-h.clientHeight;pfill.style.width=(max>0?h.scrollTop/max*100:0)+'%';}
  addEventListener('scroll',sync,{passive:true}); addEventListener('resize',sync); sync();
  /* 섹션이 화면에 들어오면 나타남 */
  var secs=[].slice.call(document.querySelectorAll('#deck>.slide'));
  if(!('IntersectionObserver' in window)){ secs.forEach(function(s){s.classList.add('on');}); return; }
  var io=new IntersectionObserver(function(es){ es.forEach(function(e){ if(e.isIntersecting){ e.target.classList.add('on'); io.unobserve(e.target); count(e.target); } }); },{threshold:.18,rootMargin:'0px 0px -6% 0px'});
  secs.forEach(function(s){ io.observe(s); });
  /* 숫자 올라가기: 프로모션 단가(정가에서 내려옴)·성과 사례 ROAS */
  function count(sec){
    if(matchMedia('(prefers-reduced-motion: reduce)').matches) return;
    sec.querySelectorAll('.pkv b,.rk .n').forEach(function(el){
      var node=el.firstChild; if(!node||node.nodeType!==3) return;
      var txt=node.nodeValue.trim(), to=parseFloat(txt.replace(/,/g,'')); if(isNaN(to)) return;
      var dec=(txt.split('.')[1]||'').length, from=+el.getAttribute('data-from')||0, t0=0;
      function fmt(v){ return v.toLocaleString('en-US',{minimumFractionDigits:dec,maximumFractionDigits:dec}); }
      node.nodeValue=fmt(from);
      requestAnimationFrame(function f(t){ if(!t0)t0=t; var x=Math.min(1,(t-t0)/1100), v=from+(to-from)*(1-Math.pow(1-x,3)); node.nodeValue=x<1?fmt(v):txt; if(x<1) requestAnimationFrame(f); });
    });
  }
})();
</script>
''' + ax_js + r'''
<script>
/* 비용 비교 영수증(ax-receipt 방식): 보이면 인쇄되듯 나오고 금액이 올라감, 같은 항목끼리 짝지어 강조, 월 발송 횟수에 따라 1년 차이 */
(function(){
  var sec=document.querySelector('.rcv'); if(!sec) return;
  var $=function(q,r){return (r||document).querySelector(q);}, $$=function(q,r){return (r||document).querySelectorAll(q);};
  var still=matchMedia('(prefers-reduced-motion: reduce)').matches;
  var won=function(n){ return Math.round(n).toLocaleString('ko-KR')+'원'; };
  var man=function(n){ var v=Math.round(n/1000)/10; return v.toLocaleString('ko-KR',{maximumFractionDigits:1})+'만'; };
  function big(n){ var e=Math.floor(n/1e8), m=Math.round((n-e*1e8)/1e4); if(m===10000){e++;m=0;} return e?e+'억'+(m?' '+m.toLocaleString('ko-KR')+'만':'')+' 원':man(n)+' 원'; }
  function count(el,v,fmt,dur,delay){
    if(still||!dur){ el.textContent=fmt(v); return; }
    var t0=0; el.textContent=fmt(0);
    setTimeout(function(){ requestAnimationFrame(function tick(t){ if(!t0)t0=t; var k=Math.min(1,(t-t0)/dur); el.textContent=fmt(v*(1-Math.pow(1-k,3))); if(k<1) requestAnimationFrame(tick); }); },delay||0);
  }
  var rsum=$('.rsum',sec), once=+rsum.dataset.once, times=4;
  // 행 등장 순서
  $$('.rcpt',sec).forEach(function(r,k){
    $$('tbody tr',r).forEach(function(tr,i){ tr.style.animationDelay=(350+i*110+k*250)+'ms'; });
    $('.rcnt',r).style.animationDelay=(850+k*250)+'ms';
    $('.rtot',r).style.animationDelay=(950+k*250)+'ms';
  });
  function play(){
    sec.classList.add('play');
    $$('[data-v]',sec).forEach(function(e){
      var tr=e.closest('tr'), i=tr?[].indexOf.call(tr.parentNode.children,tr):4;
      count(e,+e.dataset.v,won,700,350+i*110+(e.closest('.mesion')?250:0));
    });
    var p=$('[data-pct]',sec); count(p,+p.dataset.pct,function(x){return Math.round(x)+'%';},500,1900);
    count($('#rYear'),once*times*12,big,1400,300);
    if(!still) auto=setTimeout(step,2700);
  }
  // 같은 항목끼리 짝지어 강조(마우스 올리기·탭), 처음 한 번은 차례로 보여 줌
  var auto=null, user=false, seq=['fr','nf','np'], si=0;
  function hot(row){ $$('.rcpt tr[data-row]',sec).forEach(function(tr){ tr.classList.toggle('hot',tr.dataset.row===row); }); }
  function step(){ if(user) return; if(si<seq.length){ hot(seq[si++]); auto=setTimeout(step,1100); } else hot(null); }
  $$('.rcpt tbody tr[data-row]',sec).forEach(function(tr){
    tr.addEventListener('mouseenter',function(){ user=true; clearTimeout(auto); hot(tr.dataset.row); });
    tr.addEventListener('mouseleave',function(){ hot(null); });
    tr.addEventListener('click',function(){ user=true; clearTimeout(auto); hot(tr.classList.contains('hot')?null:tr.dataset.row); });
  });
  // 월 발송 횟수
  var seg=$('#rSeg'), pill=$('i',seg);
  function place(){ var b=$('button.on',seg); pill.style.width=b.offsetWidth+'px'; pill.style.transform='translateX('+b.offsetLeft+'px)'; }
  seg.addEventListener('click',function(e){
    var b=e.target.closest('button'); if(!b) return;
    $$('button',seg).forEach(function(x){ x.classList.toggle('on',x===b); }); place();
    times=+b.dataset.t; count($('#rYear'),once*times*12,big,500,0);
  });
  place(); addEventListener('resize',place); document.fonts&&document.fonts.ready.then(place);
  if(!('IntersectionObserver' in window)) return play();
  var io=new IntersectionObserver(function(es){ if(es[0].isIntersecting){ io.disconnect(); play(); } },{threshold:.25});
  io.observe($('.rcpts',sec));
})();
</script>'''

# 기존 홈페이지 파비콘
gen = open(f'{REPO}/index-general.html', encoding='utf-8').read()
favicon = re.search(r'<link rel="icon"[^>]+>', gen).group(0)

# 공유(오픈그래프) 정보: 소개서 표지·요약 문장 그대로. 공유 이미지 원본은 tools/intro/og-intro.html → creatives/og-intro.png
title = '메시온 소개 | 비회원까지 닿는 세일즈 캠페인 솔루션'
desc = '네이버 스마트 톡톡과 카카오 브랜드메시지로 더 많은 고객에게 보내고, 캠페인 준비와 성과 분석은 AI 에이전트에게, 담당자는 전략에만 집중하세요.'
og_title = '비회원까지 닿는 세일즈 캠페인 솔루션, 메시온'
og_img = 'https://neosongsanhae.github.io/mesionlanding-embed/creatives/og-intro.png?v=1'
og_alt = '메시온 소개: 비회원까지 닿는 세일즈 캠페인 솔루션. 비회원 구매자까지, 메시온 AX 기획부터 성과 분석까지, 솔루션 이용료 0원'

# 프로모션 단가는 정가에서 내려오도록 시작값 표시
promo_from = {'16': '22', '4': '10'}

html = f'''<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{URL}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="메시온">
<meta property="og:url" content="{URL}">
<meta property="og:title" content="{og_title}">
<meta property="og:description" content="{desc}">
<meta property="og:image" content="{og_img}">
<meta property="og:image:secure_url" content="{og_img}">
<meta property="og:image:type" content="image/png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="{og_alt}">
<meta property="og:locale" content="ko_KR">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{og_title}">
<meta name="twitter:description" content="{desc}">
<meta name="twitter:image" content="{og_img}">
{favicon}
<link rel="preconnect" href="https://cdn.jsdelivr.net" crossorigin>
<link rel="stylesheet" crossorigin href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/variable/pretendardvariable-dynamic-subset.min.css">
<style>{deck_css}{web_css}</style>
<script>
/* PostHog: localhost·사내 브라우저(?internal=1 한 번 방문)는 수집 안 함 */
(function(){{
  var KEY='{POSTHOG_KEY}', HOST='{POSTHOG_HOST}';
  if(!KEY||/^(localhost|127[.]0[.]0[.]1)$/.test(location.hostname)) return;
  !function(t,e){{var o,n,p,r;e.__SV||(window.posthog=e,e._i=[],e.init=function(i,s,a){{function g(t,e){{var o=e.split(".");2==o.length&&(t=t[o[0]],e=o[1]),t[e]=function(){{t.push([e].concat(Array.prototype.slice.call(arguments,0)))}}}}(p=t.createElement("script")).type="text/javascript",p.crossOrigin="anonymous",p.async=!0,p.src=s.api_host.replace(".i.posthog.com","-assets.i.posthog.com")+"/static/array.js",(r=t.getElementsByTagName("script")[0]).parentNode.insertBefore(p,r);var u=e;for(void 0!==a?u=e[a]=[]:a="posthog",u.people=u.people||[],u.toString=function(t){{var e="posthog";return"posthog"!==a&&(e+="."+a),t||(e+=" (stub)"),e}},u.people.toString=function(){{return u.toString(1)+".people (stub)"}},o="init capture register register_once identify reset get_distinct_id opt_in_capturing opt_out_capturing has_opted_out_capturing".split(" "),n=0;n<o.length;n++)g(u,o[n]);e._i.push([i,s,a])}},e.__SV=1)}}(document,window.posthog||[]);
  posthog.init(KEY,{{api_host:HOST,person_profiles:'identified_only'}});
  try{{ var q=new URLSearchParams(location.search).get('internal'); if(q==='1') posthog.opt_out_capturing(); if(q==='0') posthog.opt_in_capturing(); }}catch(e){{}}
  posthog.register({{page_name:'intro'}});
}})();
function phCapture(n,p){{ try{{ window.posthog&&window.posthog.capture&&window.posthog.capture(n,p); }}catch(e){{}} }}
</script>
</head>
<body>
<div class="topbar"><a href="intro.html" aria-label="메시온"><img src="{logo}" alt="Mesion"></a><div class="tbr"><a class="navlink" href="about.html">메시온 소개</a><button class="tcta" type="button" data-lead>상담 신청하기</button></div></div>
<div class="pbar"><i id="pfill"></i></div>
<main class="deck" id="deck">
{chr(10).join(out_secs)}
</main>
<div class="ldm" id="ldm" hidden><div class="ldm-bg" data-close></div><div class="ldm-box" role="dialog" aria-modal="true" aria-label="상담 신청"><button class="ldm-x" type="button" data-close aria-label="닫기">×</button>{lead_form('m')}</div></div>
<footer class="gfoot"><div class="in">(주)유니드컴즈 · 대표자 양재필, 전형신<br>주소 서울특별시 마포구 양화로 81, L1층 L105호(서교동, 패스트파이브 합정점)<br>문의 <a href="mailto:public@uneedcomms.com">public@uneedcomms.com</a><br>Copyrights © 2022 UNEEDCOMMS All Rights Reserved.</div></footer>
{script}
<script>
/* 매체 3곳 화면: 2초마다 다음 화면, 매체 이름을 누르면 그 화면 */
(function(){{
  var ph=document.getElementById('aphone'); if(!ph) return;
  var cps=[].slice.call(document.querySelectorAll('.pcp')), ims=[].slice.call(ph.querySelectorAll('.pvi'));
  var cur=0, t=null, vis=false, still=matchMedia('(prefers-reduced-motion: reduce)').matches;
  function show(i){{ cur=i; cps.forEach(function(c,k){{c.classList.toggle('on',k===i);}}); ims.forEach(function(m,k){{m.classList.toggle('on',k===i);}}); run(); }}
  function run(){{ clearTimeout(t); if(!vis||still) return; t=setTimeout(function(){{ show((cur+1)%ims.length); }},2000); }}
  cps.forEach(function(c,k){{ c.addEventListener('click',function(){{ show(k); }}); }});
  if('IntersectionObserver' in window) new IntersectionObserver(function(es){{ vis=es[0].isIntersecting; run(); }},{{threshold:.3}}).observe(ph);
}})();
</script>
<script>
/* 상담 신청: 문의 장 폼과 상단 버튼 팝업 폼, 같은 시트로 보냄 */
var LEAD_ENDPOINT='https://script.google.com/macros/s/AKfycbwg67vy0WnjA29Ln9jdXBxvtiszfh7qusnP8D1tx4KvK3tJCDl5dpF74cTD1nZv5I8L/exec';
(function(){{
  document.querySelectorAll('.ldform').forEach(function(form){{
    var pre=form.dataset.pre, kf='', err=form.querySelector('.lderr'), btn=form.querySelector('.ldbtn');
    var el=function(k){{ return document.getElementById(pre+k); }};
    el('Phone').addEventListener('input',function(){{ this.value=this.value.replace(/[^0-9]/g,'').slice(0,11); }});
    form.querySelectorAll('.ldkf button').forEach(function(b){{ b.addEventListener('click',function(){{
      kf=b.dataset.v; form.querySelectorAll('.ldkf button').forEach(function(x){{ x.classList.toggle('on',x===b); x.setAttribute('aria-pressed',x===b?'true':'false'); }});
    }}); }});
    btn.addEventListener('click',function(){{
      var brand=el('Brand').value.trim(), name=el('Name').value.trim(), phone=el('Phone').value.replace(/[^0-9]/g,'');
      if(!brand||!name||!phone||!kf){{ err.classList.add('on'); return; }}
      err.classList.remove('on'); btn.disabled=true; btn.textContent='보내는 중…';
      var b=''; try{{ b=new URLSearchParams(location.search).get('b')||''; }}catch(e){{}}
      var page=location.href.split('#')[0];
      // 친구 수는 kf로 보내고, 수집기를 새로 배포하기 전에도 남도록 유입경로 끝(#)에도 붙임
      var payload={{brand:brand,name:name,phone:phone,email:'',b:b,src:'소개서 웹페이지',kf:kf,ref:page+'#카톡친구='+kf,ua:navigator.userAgent}};
      phCapture('lead_submitted',{{form:pre==='m'?'팝업':'하단',kf:kf,b:b,src:'소개서 웹페이지'}});
      var finish=function(){{ document.querySelectorAll('.ldform').forEach(function(f){{ f.classList.add('sent'); }}); }};
      try{{ fetch(LEAD_ENDPOINT,{{method:'POST',mode:'no-cors',headers:{{'Content-Type':'text/plain;charset=utf-8'}},body:JSON.stringify(payload)}}).then(finish).catch(finish); }}catch(e){{ finish(); }}
    }});
  }});
  var m=document.getElementById('ldm'), last=null;
  function open(){{ last=document.activeElement; m.hidden=false; document.documentElement.style.overflow='hidden'; setTimeout(function(){{ var f=document.getElementById('mBrand'); if(f&&!m.querySelector('.sent')) f.focus(); }},60); }}
  function close(){{ m.hidden=true; document.documentElement.style.overflow=''; if(last) last.focus(); }}
  document.querySelectorAll('[data-lead]').forEach(function(b){{ b.addEventListener('click',function(){{ phCapture('lead_form_opened',{{from:'상단 버튼'}}); open(); }}); }});
  m.querySelectorAll('[data-close]').forEach(function(b){{ b.addEventListener('click',close); }});
  addEventListener('keydown',function(e){{ if(e.key==='Escape'&&!m.hidden) close(); }});
}})();
</script>
</body>
</html>
'''
html = re.sub(r'<div class="pkv"><b>(\d+)</b>', lambda m: f'<div class="pkv"><b data-from="{promo_from.get(m.group(1), m.group(1))}">{m.group(1)}</b>', html)
# 문제 장을 뺐으므로 '해결 1·2' 번호 없이 영역 이름만 남김
# 프로모션 대상 기준 50만 → 20만(10/27 요청)
html = html.replace('카카오톡 채널 친구 50만 명 이상 브랜드', '카카오톡 채널 친구 20만 명 이상 브랜드')
html = html.replace('해결 1 · 매체 통합', '매체 통합').replace('해결 2 · 메시온 AX', '메시온 AX')
html = externalize(html)
html = html.replace('<div class="deck" id="deck">', '')
open(OUT, 'w', encoding='utf-8').write(html)
print('written', OUT, len(html), 'sections', len(out_secs))
