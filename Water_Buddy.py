"""WaterBuddy - Streamlit edition. Run: streamlit run app.py"""
import json, math, time
from datetime import date, datetime
import streamlit as st
import streamlit.components.v1 as components
import calc

st.set_page_config(page_title="WaterBuddy", page_icon="💧", layout="centered")

PAGES = ["Dashboard", "Hydration Adventure", "Fun Zone", "Progress", "Daily Summary", "Settings"]
NAV = {"Dashboard": "🏠  \nHome", "Hydration Adventure": "🧭  \nQuest", "Fun Zone": "🎮  \nFun", "Progress": "📈  \nStats", "Daily Summary": "📅  \nDay", "Settings": "⚙️  \nSettings"}
# name: (bg, card, text, accent, preview)
THEMES = {
    "Ocean Explorer": ("radial-gradient(circle at 15% 10%,#1fb6ff55,transparent 40%),radial-gradient(circle at 85% 30%,#00e5c955,transparent 45%),radial-gradient(circle at 50% 100%,#0a6cff66,transparent 50%),linear-gradient(180deg,#04122e 0%,#06306b 55%,#0a5a8f 100%)", "rgba(255,255,255,.12)", "#e8fbff", "#2ec4d6"),
    "Space Adventure": ("radial-gradient(circle at 20% 15%,#7c4dff66,transparent 40%),radial-gradient(circle at 80% 40%,#ff4fd855,transparent 45%),radial-gradient(circle at 50% 100%,#2a63ff44,transparent 50%),linear-gradient(180deg,#05030f,#140a3a 60%,#2b1260)", "rgba(255,255,255,.12)", "#f1eaff", "#b388ff"),
    "Jungle Quest": ("radial-gradient(circle at 15% 10%,#b7f55a55,transparent 40%),radial-gradient(circle at 85% 35%,#2ee6a655,transparent 45%),radial-gradient(circle at 50% 100%,#0f7a3a88,transparent 50%),linear-gradient(180deg,#06281a,#0c5a2e 60%,#1b8a43)", "rgba(255,255,255,.14)", "#effbe8", "#9be564"),
    "Candy Pop": ("radial-gradient(circle at 15% 10%,#ff9ad566,transparent 45%),radial-gradient(circle at 85% 30%,#9ad7ff99,transparent 45%),radial-gradient(circle at 50% 100%,#ffe29a99,transparent 50%),linear-gradient(180deg,#fff0f8,#ffd9ef 55%,#d9ecff)", "rgba(255,255,255,.7)", "#4a1a38", "#ff5fa2"),
    "Neon Night": ("radial-gradient(circle at 15% 10%,#00f0ff44,transparent 40%),radial-gradient(circle at 85% 40%,#c400ff55,transparent 45%),radial-gradient(circle at 50% 100%,#ff2e9a44,transparent 50%),linear-gradient(180deg,#04010c,#0d0530 60%,#1a0848)", "rgba(255,255,255,.1)", "#f0f0ff", "#00f0ff"),
    "Calm Minimal": ("radial-gradient(circle at 15% 10%,#cfe9e2,transparent 45%),radial-gradient(circle at 85% 35%,#dfe8f7,transparent 45%),linear-gradient(180deg,#f7f9f8,#e6eeec)", "rgba(255,255,255,.8)", "#223333", "#3f7f7a"),
}
ACC = {  # buddy accessories drawn behind the body
    "Aqua": "",
    "Bubbles": '<circle cx="26" cy="40" r="10" fill="#fff" opacity=".5"/><circle cx="136" cy="56" r="7" fill="#fff" opacity=".5"/><circle cx="130" cy="24" r="4" fill="#fff" opacity=".5"/>',
    "Coral": '<path d="M60 40l-10-22M60 40l12-18M100 40l-12-20M100 40l12-22" stroke="#ff7f7f" stroke-width="6" stroke-linecap="round"/>',
    "Splash": '<path d="M20 50l14 10M140 50l-14 10M80 6v14M40 20l8 10M120 20l-8 10" stroke="#fff" stroke-width="5" stroke-linecap="round"/>',
    "Nova": '<ellipse cx="80" cy="110" rx="74" ry="14" fill="none" stroke="#ffd166" stroke-width="4"/><path d="M128 20l4 9 9 1-7 6 2 9-8-5-8 5 2-9-7-6 9-1z" fill="#ffd166"/>',
    "Leaf": '<path d="M80 22c20-24 44-14 46-12-2 22-22 36-46 12z" fill="#52b788"/>',
}
BUDDIES = {
    "Aqua": ("#4cc9f0", "#0077b6", "The original friendly drop. Cheerful and steady."),
    "Bubbles": ("#8ecae6", "#219ebc", "A playful ocean companion who loves a good giggle."),
    "Coral": ("#ffb4a2", "#e5707e", "An underwater explorer, curious about everything."),
    "Splash": ("#48cae4", "#0096c7", "Energetic and loud. Cheers for every sip."),
    "Nova": ("#9d8cff", "#4a2fbd", "A cosmic explorer who treats each drink as a mission."),
    "Leaf": ("#95d5b2", "#2d6a4f", "Calm and nature-minded. Slow and steady wins."),
}
DESTS = [  # (name, blurb, theme, mission id)
    ("Ocean Reef", "Sunlit coral and gentle currents.", "Ocean Explorer", "first"),
    ("Cosmic Lagoon", "A glittering pool among the stars.", "Space Adventure", "three"),
    ("Jungle Springs", "Mossy pools hidden under giant leaves.", "Jungle Quest", "half"),
    ("Candy Cove", "A sugar-sweet bay of pastel waves.", "Candy Pop", "theme"),
    ("Neon Atlantis", "A glowing sunken city after dark.", "Neon Night", "summary"),
    ("Peaceful Falls", "A quiet waterfall. No rush here.", "Calm Minimal", "goal"),
]


# ---------- state ----------
def init():
    s = st.session_state
    defaults = dict(step=0, age="Adults (18+)", goal=2000, buddy="Aqua", theme="Ocean Explorer", entries=[], awarded=[],
                    badges=[], flags=[], history=[], remind=False, interval=60, h_start=8, h_end=20, reduced=False,
                    day=str(date.today()), nid=0, msg="", celebrate=False, mood="happy", dest=None, confirm=None,
                    page="Dashboard", tick=0, burst=False, ripple=False)
    for k, v in defaults.items():
        s.setdefault(k, v)
    if s.day != str(date.today()):  # daily rollover (untested across real midnight)
        archive_day()
        s.msg = "A new day! Welcome back."


def hourly(entries):
    hrs = {}
    for e in entries:
        h = int(e["time"][:2])
        hrs[h] = hrs.get(h, 0) + e["ml"]
    return hrs


def snapshot():
    s = st.session_state
    t = calc.total(s.entries)
    return dict(date=s.day, total=t, goal=s.goal, percent=round(calc.percent(t, s.goal), 1), drinks=len(s.entries),
                milestones=calc.reached(calc.percent(t, s.goal)), badges=list(s.badges), hours=hourly(s.entries))


def archive_day():
    s = st.session_state
    if s.entries:
        s.history.append(snapshot())
    s.entries, s.awarded, s.flags, s.mood, s.day, s.confirm = [], [], [], "happy", str(date.today()), None


def missions():
    s = st.session_state
    p = calc.percent(calc.total(s.entries), s.goal)
    return {"first": ("Log your first drink", min(len(s.entries), 1), 1),
            "three": ("Record 3 drinks today", min(len(s.entries), 3), 3),
            "half": ("Reach 50% of your goal", int(p >= 50), 1),
            "theme": ("Explore a new theme", int("theme" in s.flags), 1),
            "summary": ("Review the daily summary", int("summary" in s.flags), 1),
            "goal": ("Reach your goal", int(p >= 100), 1)}


def check_badges():
    s = st.session_state
    for k, (_, cur, need) in missions().items():
        if cur >= need and k not in s.badges:
            s.badges.append(k)
            s.msg += f" Badge earned: {missions()[k][0]}!"


def log(raw):
    s = st.session_state
    ml = calc.parse_amount(raw)
    if ml is None:
        s.msg = f"Enter a whole number from {calc.MIN_ML} to {calc.MAX_ML} ml."
        return
    s.nid += 1
    s.entries.append(dict(id=s.nid, ml=ml, time=datetime.now().strftime("%H:%M")))
    p = calc.percent(calc.total(s.entries), s.goal)
    new = calc.new_milestones(p, s.awarded)
    s.awarded += new
    s.mood = "party" if 100 in new else "cheer"
    top = max(new) if new else None
    s.msg = f"{s.buddy}: {top}% reached! Nice work." if top else f"+{ml} ml. {s.buddy} is happy!"
    s.celebrate = 100 in new
    s.burst, s.ripple, s.tick = bool(new), True, s.tick + 1
    check_badges()


def remove(eid):
    s = st.session_state
    s.entries = [e for e in s.entries if e["id"] != eid]
    s.awarded = calc.reached(calc.percent(calc.total(s.entries), s.goal))
    s.tick += 1
    s.mood, s.msg = "happy", "Entry removed. Totals updated."


def pick_theme(name):
    s = st.session_state
    if name != s.theme and "theme" not in s.flags:
        s.flags.append("theme")
    s.theme = name
    check_badges()


def pick_buddy(name):
    st.session_state.buddy, st.session_state.mood = name, "cheer"


# ---------- visuals ----------
PART = {"Ocean Explorer": "○", "Space Adventure": "✦", "Jungle Quest": "❦", "Candy Pop": "●", "Neon Night": "✚", "Calm Minimal": "·"}


def css():
    s = st.session_state
    bg, card, tx, ac = THEMES[s.theme]
    navbg = "rgba(255,255,255,.9)" if s.theme in ("Candy Pop", "Calm Minimal") else "rgba(3,10,30,.66)"
    kf = "".join(
        f"@keyframes cnt{i}{{from{{--n:var(--p)}}}}@keyframes fill{i}{{from{{transform:translateY(var(--d))}}}}"
        f"@keyframes ring{i}{{from{{stroke-dasharray:var(--f) 327}}}}"
        f"@keyframes bn{i}{{0%,100%{{transform:none}}30%{{transform:translateY(-34px) scale(1.08,.92)}}60%{{transform:scale(.92,1.08)}}}}"
        f".k{i}{{animation:cnt{i} 1.1s ease-out}}.f{i}{{animation:fill{i} 1.4s cubic-bezier(.22,.9,.3,1)}}"
        f".r{i}{{animation:ring{i} 1.2s ease-out}}.b{i}{{animation:bn{i} .8s 3}}" for i in (0, 1))
    red = "*,*::before{animation:none!important;transition:none!important}" if s.reduced else ""
    parts = "" if s.reduced else "".join(
        f'<span class="pt" style="--l:{i * 37 % 100}%;--s:{14 + i * 7 % 22}px;--d:{12 + i * 5 % 14}s;--w:-{i * 3 % 12}s">{PART[s.theme]}</span>'
        for i in range(18))
    prim = (f'.stButton>button[kind="primary"],.stButton button[data-testid="stBaseButton-primary"]{{background:linear-gradient(135deg,{ac},{ac}cc);color:#021;border:none;min-height:62px;font-weight:600;box-shadow:0 10px 28px {ac}77;animation:pulse 2.4s ease-in-out infinite}}'
            f'.stButton>button[kind="primary"] p,.stButton button[data-testid="stBaseButton-primary"] p{{color:#021!important;font-size:1.2rem}}@keyframes pulse{{50%{{box-shadow:0 10px 44px {ac}}}}}'
            '.wv{position:fixed;left:0;right:0;bottom:0;height:26vh;z-index:-1;pointer-events:none;overflow:hidden}.wv svg{position:absolute;bottom:0;left:0;width:200%;height:100%;animation:wvs 14s linear infinite}.wv .w2{height:75%;animation-duration:22s;animation-direction:reverse}@keyframes wvs{to{transform:translateX(-50%)}}')
    waves = f'<div class="wv"><svg viewBox="0 0 1200 120" preserveAspectRatio="none"><path d="M0 60Q150 20 300 60T600 60T900 60T1200 60V120H0z" fill="{ac}" opacity=".2"/></svg><svg class="w2" viewBox="0 0 1200 120" preserveAspectRatio="none"><path d="M0 70Q150 30 300 70T600 70T900 70T1200 70V120H0z" fill="{ac}" opacity=".14"/></svg></div>'
    st.markdown(f"""<style>
@import url('https://fonts.googleapis.com/css2?family=Fredoka:wght@400;600&display=swap');
@property --n{{syntax:'<integer>';initial-value:0;inherits:false}}
.stApp{{--ac:{ac};--tx:{tx};--card:{card};isolation:isolate;background:{bg};background-size:220% 220%;animation:bgs 22s ease-in-out infinite;color:{tx}}}
.stApp::before{{content:"";position:fixed;inset:-20%;z-index:-1;pointer-events:none;background:radial-gradient(circle at 20% 20%,{ac},transparent 35%),radial-gradient(circle at 80% 70%,{ac},transparent 30%);opacity:.17;animation:dr 22s ease-in-out infinite alternate}}
header[data-testid="stHeader"]{{background:transparent}}
.stApp h1,.stApp h2,.stApp h3,.stApp p,.stApp label,.stApp button,.stApp .stat,.stApp .logo{{font-family:'Fredoka',system-ui,sans-serif}}
.stApp p,.stApp label,.stApp span,.stApp h1,.stApp h2,.stApp h3,.stApp li,.stApp small{{color:{tx}!important}}
.stApp .pt{{color:{ac}!important}}
.pt{{position:fixed;bottom:-40px;left:var(--l);font-size:var(--s);opacity:.35;z-index:-1;pointer-events:none;animation:pr var(--d) linear infinite;animation-delay:var(--w)}}
.stApp .logo{{font-size:2.2rem;font-weight:600;background:linear-gradient(90deg,{tx},{ac},{tx});background-size:200%;-webkit-background-clip:text;background-clip:text;-webkit-text-fill-color:transparent;animation:sh 4s linear infinite}}
[data-testid="stMainBlockContainer"]{{animation:pin .6s ease-out;max-width:520px;padding-top:2rem;padding-bottom:130px}}
.stButton>button,.stDownloadButton>button{{background:{card};color:{tx};border:1.5px solid {ac};border-radius:16px;min-height:46px;transition:all .25s}}
.stButton>button:hover{{background:{ac};transform:translateY(-3px);box-shadow:0 8px 22px {ac}88}}
.stButton>button:hover p{{color:#021!important}}
.stButton>button:active{{transform:scale(.94)}}
.stButton>button:focus-visible{{outline:3px solid {ac};outline-offset:2px}}
[data-testid="stRadio"]{{position:fixed;left:50%;transform:translateX(-50%);bottom:0;width:min(520px,100%);z-index:100;padding:8px 6px calc(8px + env(safe-area-inset-bottom));background:{navbg};backdrop-filter:blur(20px) saturate(1.4);border-top:1px solid {ac}66;border-radius:24px 24px 0 0;box-shadow:0 -8px 30px #0004}}
[data-testid="stRadio"] [role="radiogroup"]{{flex-wrap:nowrap;gap:2px;width:100%}}
[data-testid="stRadio"] label{{flex:1;justify-content:center;text-align:center;border-radius:16px;padding:6px 2px;min-height:54px;transition:all .25s;cursor:pointer}}
[data-testid="stRadio"] label>div:first-child{{display:none}}
[data-testid="stRadio"] label p{{font-size:.7rem;line-height:1.25;text-align:center}}
[data-testid="stRadio"] label:has(input:checked){{background:{ac};box-shadow:0 0 16px {ac}99}}
[data-testid="stRadio"] label:has(input:checked) *{{color:#021!important}}
.card{{background:{card};border:1px solid {ac}66;border-radius:24px;padding:14px 18px;margin:8px 0;backdrop-filter:blur(14px);box-shadow:0 8px 32px #0003;transition:all .3s;animation:pin .6s both}}
.card:hover{{transform:translateY(-3px);box-shadow:0 10px 30px {ac}44}}
.sg{{display:grid;grid-template-columns:repeat(auto-fit,minmax(110px,1fr));gap:10px}}
.stat{{font-size:1.6rem;font-weight:600}}.stat small{{font-size:.8rem;opacity:.8;font-weight:400}}
.num{{counter-reset:n var(--n);display:inline-block}}.num::after{{content:counter(n)}}
.center{{text-align:center}}.rw{{position:absolute;inset:0;pointer-events:none}}
.rp{{position:absolute;left:50%;top:60%;width:90px;height:90px;margin:-45px;border:3px solid {ac};border-radius:50%;animation:rp 1.1s ease-out forwards}}
.bw{{position:fixed;left:50%;top:45%;z-index:50;pointer-events:none}}
.cf{{position:absolute;width:10px;height:14px;border-radius:3px;animation:cf 1.6s ease-out forwards}}
.eye{{transform-box:fill-box;transform-origin:center;animation:blink 4s infinite}}
.float{{animation:fl 3s ease-in-out infinite}}
@keyframes bgs{{50%{{background-position:100% 50%}}}}@keyframes dr{{to{{transform:translate(6%,4%) scale(1.15)}}}}
@keyframes pr{{to{{transform:translateY(-115vh) rotate(360deg)}}}}@keyframes pin{{from{{opacity:0;transform:translateY(14px)}}}}
@keyframes sh{{to{{background-position:200%}}}}@keyframes blink{{0%,92%,100%{{transform:none}}96%{{transform:scaleY(.1)}}}}
@keyframes rp{{from{{transform:scale(.2);opacity:.9}}to{{transform:scale(2.4);opacity:0}}}}
@keyframes cf{{to{{transform:translate(var(--x),var(--y)) rotate(720deg);opacity:0}}}}
@keyframes fl{{50%{{transform:translateY(-10px)}}}}@keyframes wv{{to{{transform:translateX(-80px)}}}}
@keyframes rise{{from{{transform:translateY(0)}}to{{transform:translateY(-190px);opacity:0}}}}
{prim}{kf}{red}</style><div aria-hidden="true">{waves}{parts}</div>""", unsafe_allow_html=True)


def burst():
    sp = "".join(f'<span class="cf" style="--x:{i * 53 % 420 - 210}px;--y:{-(120 + i * 29 % 260)}px;background:hsl({i * 37 % 360},90%,60%);animation-delay:{i % 5 * .04}s"></span>' for i in range(28))
    return f'<div class="bw">{sp}</div>'


def stat(label, n, prev, k, unit=""):
    return f'<div class="card center stat"><span class="num k{k}" style="--n:{n};--p:{prev}"></span>{unit}<br><small>{label}</small></div>'


def buddy_svg(name, mood="happy", size=140, k=0):
    c1, c2, _ = BUDDIES[name]
    glad = mood in ("cheer", "party")
    eyes = ('<path d="M62 78q6-8 12 0M86 78q6-8 12 0" stroke="#012" stroke-width="3" fill="none"/>' if glad else
            '<circle class="eye" cx="68" cy="78" r="5" fill="#012"/><circle class="eye" cx="92" cy="78" r="5" fill="#012"/>')
    mouth = ('<path d="M68 95q12 16 24 0z" fill="#012"/>' if glad else
             '<path d="M70 96q10 9 20 0" stroke="#012" stroke-width="3" fill="none"/>')
    return (f'<div class="{"b%d" % k if glad else ""}" style="display:inline-block"><svg class="float" width="{size}" height="{size}" viewBox="0 0 160 160" role="img" aria-label="{name} buddy">'
            f'<defs><linearGradient id="g{name}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{c1}"/>'
            f'<stop offset="1" stop-color="{c2}"/></linearGradient></defs>{ACC[name]}'
            f'<path d="M80 18C80 18 30 74 30 105a50 50 0 0 0 100 0C130 74 80 18 80 18z" fill="url(#g{name})"/>'
            f'{eyes}{mouth}<ellipse cx="52" cy="95" rx="6" ry="4" fill="#fff" opacity=".4"/></svg></div>')


def bottle_svg(f, prev=0.0, k=0):
    y = 40 + 230 * (1 - f / 100)
    dy = 230 * (f - prev) / 100
    bub = "".join(f'<circle cx="{x}" cy="262" r="{r}" fill="#fff" opacity=".6" style="animation:rise {d}s linear {w}s infinite"/>'
                  for x, r, d, w in ((55, 4, 4, 0), (75, 3, 5, 1), (95, 5, 6, 2), (110, 3, 4.5, 3), (65, 2, 3.5, 1.5), (100, 4, 5.5, .5)))
    glow = "filter:drop-shadow(0 0 14px var(--ac))" if f >= 100 else ""
    return (f'<svg viewBox="0 0 160 300" width="170" style="{glow}" role="img" aria-label="Bottle {f:.0f}% full"><defs><clipPath id="b">'
            f'<rect x="30" y="40" width="100" height="230" rx="28"/></clipPath></defs>'
            f'<rect x="62" y="8" width="36" height="34" rx="8" fill="var(--ac)"/><g clip-path="url(#b)"><g class="f{k}" style="--d:{dy:.1f}px">'
            f'<rect x="0" y="{y}" width="200" height="300" fill="var(--ac)" opacity=".7"/>'
            f'<path d="M-80 {y}q20-10 40 0t40 0t40 0t40 0t40 0t40 0t40 0t40 0V{y + 14}H-80z" fill="var(--ac)" style="animation:wv 3s linear infinite"/></g>{bub}</g>'
            f'<rect x="40" y="62" width="8" height="150" rx="4" fill="#fff" opacity=".22"/>'
            f'<rect x="30" y="40" width="100" height="230" rx="28" fill="none" stroke="var(--tx)" stroke-width="3" opacity=".7"/></svg>')


def ring_svg(p, f, prev=0.0, k=0):
    c = 2 * math.pi * 52
    return (f'<svg viewBox="0 0 140 140" width="170" role="img" aria-label="{p:.0f} percent of goal">'
            f'<circle cx="70" cy="70" r="52" stroke="var(--tx)" opacity=".2" stroke-width="12" fill="none"/>'
            f'<circle class="r{k}" cx="70" cy="70" r="52" stroke="var(--ac)" stroke-width="12" fill="none" stroke-linecap="round" '
            f'stroke-dasharray="{c * f / 100:.1f} {c:.1f}" transform="rotate(-90 70 70)" style="--f:{c * prev / 100:.1f};filter:drop-shadow(0 0 6px var(--ac))"/>'
            f'<text x="70" y="78" text-anchor="middle" font-size="24" font-weight="700" fill="var(--tx)">{p:.0f}%</text></svg>')


def swatch(name):
    bg, card, tx, ac = THEMES[name]
    return (f'<div style="background:{bg};border:3px solid {ac};border-radius:14px;padding:10px;color:{tx};text-align:center;font-weight:600">'
            f'{name}<div style="height:8px;border-radius:6px;background:{ac};margin-top:6px"></div></div>')


# ---------- screens ----------
def onboarding():
    s = st.session_state
    if s.step == 0:
        st.markdown(f'<div class="center">{buddy_svg(s.buddy, "cheer", 190)}<h1>WaterBuddy</h1><h3>Make every sip an adventure.</h3>'
                    '<p>Meet your water buddy, track your progress, and turn hydration into a habit.</p></div>', unsafe_allow_html=True)
        st.button("Start", on_click=lambda: s.update(step=1), use_container_width=True)
    elif s.step == 1:
        st.header("Who is using WaterBuddy?")
        for a in calc.AGE_GROUPS:
            st.button(("✅ " if a == s.age else "") + a, key="age" + a, use_container_width=True,
                      on_click=lambda a=a: s.update(age=a, goal=calc.AGE_GROUPS[a]))
        st.button("Next", on_click=lambda: s.update(step=2), use_container_width=True)
    elif s.step == 2:
        st.header("Your daily tracking goal")
        st.write("This is a starting point for tracking, not a medical recommendation. Needs vary with health, activity and weather. "
                 "Younger users should choose a goal with a parent or guardian. Follow a doctor's advice if you have one.")
        g = st.number_input("Daily goal (ml)", 500, 6000, int(s.goal), 50)
        s.goal = int(g)
        st.caption(f"{s.goal} ml = {s.goal / 1000:.2f} L. You can change this in Settings any time.")
        st.button("Next", on_click=lambda: s.update(step=3), use_container_width=True)
    else:
        st.header("Choose your buddy")
        buddy_grid(True)
        st.button("Enter WaterBuddy", on_click=lambda: s.update(step=4, msg=f"Hi! {s.buddy} is ready."), use_container_width=True)


def buddy_grid(show_desc=False):
    s = st.session_state
    cols = st.columns(3)
    for i, n in enumerate(BUDDIES):
        with cols[i % 3]:
            st.markdown(f'<div class="center">{buddy_svg(n, "cheer" if n == s.buddy else "happy", 90)}</div>', unsafe_allow_html=True)
            st.button(("✅ " if n == s.buddy else "") + n, key="b" + n, on_click=pick_buddy, args=(n,), use_container_width=True)
            if show_desc:
                st.caption(BUDDIES[n][2])


def theme_grid():
    s = st.session_state
    cols = st.columns(3)
    for i, n in enumerate(THEMES):
        with cols[i % 3]:
            st.markdown(swatch(n), unsafe_allow_html=True)
            st.button(("✅ Active: " if n == s.theme else "Use ") + n, key="t" + n, on_click=pick_theme, args=(n,), use_container_width=True)


def dashboard():
    s = st.session_state
    t = calc.total(s.entries)
    p = calc.percent(t, s.goal)
    f = calc.fill(p)
    ms = calc.reached(p)
    pv = s.get("prev", dict(t=0, f=0.0, n=0))
    k = s.tick % 2
    mood, s.mood = s.mood, "happy"
    hr = datetime.now().hour
    gr = "Good morning" if hr < 12 else "Good afternoon" if hr < 18 else "Good evening"
    st.markdown(f'<div class="logo">💧 WaterBuddy</div><p style="margin:-4px 0 8px;opacity:.9">{gr}! {calc.remaining(t, s.goal)} ml to go today.</p>', unsafe_allow_html=True)
    if s.burst and not s.reduced:
        st.markdown(burst(), unsafe_allow_html=True)
    rp = '<div class="rw"><span class="rp"></span><span class="rp" style="animation-delay:.25s"></span></div>' if s.ripple and not s.reduced else ""
    s.burst = s.ripple = False
    c1, c2, c3 = st.columns(3)
    c1.markdown(f'<div class="center">{buddy_svg(s.buddy, mood, 140, k)}</div>', unsafe_allow_html=True)
    c2.markdown(f'<div class="center" style="position:relative">{rp}{bottle_svg(f, pv["f"], k)}</div>', unsafe_allow_html=True)
    c3.markdown(f'<div class="center">{ring_svg(p, f, pv["f"], k)}</div>', unsafe_allow_html=True)
    if not s.entries:
        st.info(f"Hi, I'm {s.buddy}! Log your first drink whenever you're ready.")
    cards = (stat("logged", t, pv["t"], k, " ml") + stat("goal", s.goal, s.goal, k, " ml")
             + stat("remaining", calc.remaining(t, s.goal), calc.remaining(pv["t"], s.goal), k, " ml")
             + stat("drinks", len(s.entries), pv["n"], k)
             + f'<div class="card center stat">{ms[-1] if ms else "–"}{"%" if ms else ""}<br><small>milestone</small></div>')
    s.prev = dict(t=t, f=f, n=len(s.entries))
    if p > 100:
        st.caption(f"You've logged {p:.0f}% of your goal. Goal reached. There's no need to drink more.")
    st.button("💧  Drink 250 ml", key="cta", type="primary", on_click=log, args=(250,), use_container_width=True)
    q = st.columns(4)
    for col, ml in zip(q, (100, 150, 350, 500)):
        col.button(f"+{ml}", key=f"q{ml}", on_click=log, args=(ml,), use_container_width=True)
    with st.expander("Custom amount"):
        amt = st.number_input("Amount (ml)", calc.MIN_ML, calc.MAX_ML, 200, 10)
        st.button("Add custom", on_click=log, args=(amt,), use_container_width=True)
    if s.entries:
        st.button("↩ Undo last drink", on_click=remove, args=(s.entries[-1]["id"],), use_container_width=True)
    st.markdown(f'<div class="sg">{cards}</div>', unsafe_allow_html=True)
    st.subheader("Today's timeline")
    for e in reversed(s.entries):
        r = st.columns([1, 2, 1])
        r[0].write(e["time"])
        r[1].write(f"{e['ml']} ml")
        r[2].button("Remove", key=f"d{e['id']}", on_click=remove, args=(e["id"],))
    if not s.entries:
        st.caption("No drinks logged yet.")
    reminder_check()


def reminder_check():
    s = st.session_state
    if not s.remind:
        return
    now = datetime.now()
    if not (s.h_start <= now.hour < s.h_end):
        return
    last = s.entries[-1]["time"] if s.entries else None
    mins = (now.hour * 60 + now.minute) - (int(last[:2]) * 60 + int(last[3:])) if last else s.interval
    if mins >= s.interval:
        st.info("Gentle nudge: it's been a little while since your last drink. Only if you feel like it!")


def adventure():
    s = st.session_state
    ms = missions()
    if s.dest is None:
        st.header("Adventure map")
        st.caption("Every destination is open. Rewards are optional.")
        cols = st.columns(2)
        for i, (n, blurb, th, mid) in enumerate(DESTS):
            _, cur, need = ms[mid]
            with cols[i % 2]:
                st.markdown(swatch(th), unsafe_allow_html=True)
                st.button(f"Open {n} ({cur}/{need})", key="dest" + n, on_click=lambda n=n: s.update(dest=n), use_container_width=True)
    else:
        n, blurb, th, mid = next(d for d in DESTS if d[0] == s.dest)
        title, cur, need = ms[mid]
        st.header(n)
        st.markdown(swatch(th), unsafe_allow_html=True)
        st.write(blurb)
        st.markdown(f'<div class="card"><b>Mission: {title}</b><br>{cur} of {need} complete</div>', unsafe_allow_html=True)
        st.progress(min(cur / need, 1.0))
        st.button("Back to map", on_click=lambda: s.update(dest=None))


def fun_zone():
    s = st.session_state
    st.header("Pick a buddy")
    buddy_grid()
    st.header("Pick a theme")
    theme_grid()
    st.header("Missions and badges")
    for k, (title, cur, need) in missions().items():
        st.write(("🏅 " if k in s.badges else "▫️ ") + f"{title}: {cur} of {need}")
        st.progress(min(cur / need, 1.0))


def bar_chart(vals, labels, goals=None, every=1):
    """Animated SVG bar chart. goals draws a tick per bar at that day's goal."""
    W, H, pl, pb, top = 340, 200, 8, 26, 22
    mx = max(max(vals, default=0), max(goals or [0]), 1) * 1.1
    n = max(len(vals), 1)
    bw = (W - 2 * pl) / n
    out = ['<style>.bar{transform-box:fill-box;transform-origin:bottom;animation:grow .8s ease-out both}@keyframes grow{from{transform:scaleY(0)}}</style>']
    for i, (v, lab) in enumerate(zip(vals, labels)):
        h = (H - pb - top) * v / mx
        x = pl + i * bw + bw * .15
        w = bw * .7
        out.append(f'<rect class="bar" x="{x:.1f}" y="{H - pb - h:.1f}" width="{w:.1f}" height="{max(h, 0):.1f}" rx="4" fill="var(--ac)" opacity=".85" style="animation-delay:{i * .05:.2f}s"/>')
        if v > 0 and n <= 14:
            out.append(f'<text x="{x + w / 2:.1f}" y="{H - pb - h - 4:.1f}" text-anchor="middle" font-size="9" fill="var(--tx)">{v}</text>')
        if i % every == 0:
            out.append(f'<text x="{x + w / 2:.1f}" y="{H - 8}" text-anchor="middle" font-size="9" fill="var(--tx)" opacity=".8">{lab}</text>')
        if goals:
            gy = H - pb - (H - pb - top) * goals[i] / mx
            out.append(f'<line x1="{x - 2:.1f}" x2="{x + w + 2:.1f}" y1="{gy:.1f}" y2="{gy:.1f}" stroke="var(--tx)" stroke-width="2" stroke-dasharray="3 2"/>')
    out.append(f'<line x1="{pl}" x2="{W - pl}" y1="{H - pb}" y2="{H - pb}" stroke="var(--tx)" opacity=".3"/>')
    return f'<div class="card"><svg viewBox="0 0 {W} {H}" width="100%" role="img" aria-label="Bar chart">{"".join(out)}</svg></div>'


def progress_page():
    s = st.session_state
    st.header("Progress and history")
    days = s.history[-13:] + [snapshot()]
    st.subheader("Daily totals")
    st.markdown(bar_chart([d["total"] for d in days], [d["date"][5:] for d in days], [d["goal"] for d in days]), unsafe_allow_html=True)
    st.caption("Bars show ml logged each day. Dashed ticks mark each day's goal. The last bar is today.")
    st.subheader("Hour by hour")
    idx = st.selectbox("Day", list(range(len(days)))[::-1], format_func=lambda i: days[i]["date"] + (" (today)" if i == len(days) - 1 else ""))
    hrs = days[idx].get("hours")
    if hrs:
        st.markdown(bar_chart([hrs.get(h, 0) for h in range(24)], [str(h) for h in range(24)], every=3), unsafe_allow_html=True)
        st.caption("ml logged in each hour of the day (24-hour clock).")
    else:
        st.info("No hourly data for this day yet." if idx == len(days) - 1 else "Hourly detail wasn't recorded for this day.")
    with st.expander("Daily list"):
        if not s.history:
            st.write("Finished days appear here after you start a new day.")
        for h in reversed(s.history):
            st.write(f'{h["date"]}: {h["total"]} of {h["goal"]} ml ({h["percent"]}%), {h["drinks"]} drinks')


def summary_page():
    s = st.session_state
    if "summary" not in s.flags:
        s.flags.append("summary")
        check_badges()
    d = snapshot()
    st.header("Daily summary")
    st.markdown(f'<div class="card">Total: <b>{d["total"]} ml</b> of {d["goal"]} ml ({d["percent"]}%)<br>Entries: {d["drinks"]}<br>'
                f'Milestones: {", ".join(f"{m}%" for m in d["milestones"]) or "none yet"}<br>Badges: {len(d["badges"])}</div>', unsafe_allow_html=True)
    st.write("Every day is a fresh start. Thanks for taking care of yourself." if d["percent"] < 100 else "Goal reached. Great job today!")
    if s.confirm != "day":
        st.button("Start a new day", on_click=lambda: s.update(confirm="day"))
    else:
        st.warning("This saves today to History and clears today's drinks. Theme, buddy and reminders are kept.")
        st.button("Yes, start new day", on_click=lambda: (archive_day(), s.update(msg="New day started.")))


def settings():
    s = st.session_state
    st.header("Settings")
    ages = list(calc.AGE_GROUPS)
    a = st.selectbox("Age group", ages, ages.index(s.age))
    if a != s.age:
        s.age = a
    st.button(f"Use suggested goal ({calc.AGE_GROUPS[s.age]} ml)", on_click=lambda: s.update(goal=calc.AGE_GROUPS[s.age]))
    s.goal = int(st.number_input("Daily goal (ml)", 500, 6000, int(s.goal), 50))
    s.buddy = st.selectbox("Buddy", list(BUDDIES), list(BUDDIES).index(s.buddy))
    t = st.selectbox("Theme", list(THEMES), list(THEMES).index(s.theme))
    if t != s.theme:
        pick_theme(t)
        st.rerun()
    s.reduced = st.toggle("Reduced motion", s.reduced)
    st.subheader("Reminders")
    s.remind = st.toggle("Enable in-app reminders", s.remind)
    s.interval = st.selectbox("Interval (minutes)", [30, 60, 90, 120], [30, 60, 90, 120].index(s.interval))
    s.h_start, s.h_end = st.slider("Active hours (server time)", 0, 24, (s.h_start, s.h_end))
    components.html("""<button id=b style="padding:10px 16px;border-radius:12px;font-size:16px">Enable and test browser notification</button>
<span id=m style="font-family:sans-serif;margin-left:8px"></span><script>
const m=document.getElementById('m');m.textContent='Permission: '+(window.Notification?Notification.permission:'unsupported');
document.getElementById('b').onclick=async()=>{if(!window.Notification){m.textContent='Not supported here';return}
const p=await Notification.requestPermission();m.textContent='Permission: '+p;if(p==='granted')new Notification('WaterBuddy',{body:'Time for a sip, only if you like!'})}
</script>""", height=60)
    st.caption("Browser notifications only work while the page is open. Reliable background reminders need a service worker on a secure hosted site.")
    st.subheader("Data")
    st.download_button("Export data (JSON)", json.dumps(dict(today=snapshot(), history=s.history), indent=2), "waterbuddy.json")
    if s.confirm != "all":
        st.button("Reset all data", on_click=lambda: s.update(confirm="all"))
    else:
        st.error("Deletes today's drinks, history, badges and preferences for this session.")
        st.button("Yes, delete everything", on_click=lambda: (st.session_state.clear(),))
    st.subheader("Privacy and guidance")
    st.caption("WaterBuddy stores progress only in this browser session (st.session_state). It resets when the session ends and is not synced across devices. "
               "It is a habit tracker, not a medical device. Hydration needs vary; follow your healthcare professional's advice.")


def main():
    init()
    s = st.session_state
    css()
    if s.msg:
        st.toast(s.msg)
        s.msg = ""
    if s.celebrate:
        st.balloons()
        s.celebrate = False
    if s.step < 4:
        return onboarding()
    st.radio("Navigate", PAGES, horizontal=True, key="page", label_visibility="collapsed", format_func=lambda p: NAV[p])
    {"Dashboard": dashboard, "Hydration Adventure": adventure, "Fun Zone": fun_zone, "Progress": progress_page,
     "Daily Summary": summary_page, "Settings": settings}[s.page]()


main()
