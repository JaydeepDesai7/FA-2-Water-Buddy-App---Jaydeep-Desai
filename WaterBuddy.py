import streamlit as st
from datetime import date, datetime
import json
from pathlib import Path

st.set_page_config(page_title="WaterBuddy | Hydration Adventure", page_icon="💧", layout="wide")

AGE_GROUPS = {
    "Children (4–8)": {"goal": 1200, "emoji": "🧒", "note": "A playful start for little explorers."},
    "Kids & tweens (9–13)": {"goal": 1700, "emoji": "🧑", "note": "Small sips, steady habits."},
    "Teens (14–17)": {"goal": 2000, "emoji": "🌊", "note": "Build a routine that works for you."},
    "Adults (18–64)": {"goal": 2200, "emoji": "🧑‍💻", "note": "Keep your day flowing."},
    "Seniors (65+)": {"goal": 1800, "emoji": "🌼", "note": "Gentle, consistent reminders to check in."},
}
BUDDIES = {"Splash": "💧", "Bubbles": "🫧", "Coral": "🪸", "Fin": "🐬", "Turtle": "🐢", "Star": "⭐"}
THEMES = {
    "Ocean Adventure": ("#071b32", "#0c3652", "#55ddf6", "#a4f4e6"),
    "Neon Arcade": ("#100b25", "#29164a", "#bb86fc", "#ff77c8"),
    "Pastel Reef": ("#17233b", "#31405c", "#ffb4d2", "#a7f3d0"),
    "Premium Midnight": ("#080e1b", "#17263b", "#64e4e8", "#9ae6b4"),
    "Sunny Lagoon": ("#15263a", "#25475b", "#ffd166", "#72e6c1"),
    "Arctic Glow": ("#071d2a", "#14384b", "#a5f3fc", "#dbeafe"),
}

if "day" not in st.session_state:
    st.session_state.day = str(date.today())
    st.session_state.age_group = "Teens (14–17)"
    st.session_state.goal = AGE_GROUPS[st.session_state.age_group]["goal"]
    st.session_state.intake = 0
    st.session_state.logs = []
    st.session_state.history = []
    st.session_state.buddy = "Splash"
    st.session_state.theme = "Ocean Adventure"
    st.session_state.experience = "Adventure mode"
    st.session_state.missions = {"Log your first drink": False, "Check your progress": False, "Explore the Fun Zone": False}
    st.session_state.reduced_motion = False
    st.session_state.last_milestone = 0
    st.session_state.show_summary = False

# A daily rollover keeps the current count separate from the previous day.
if st.session_state.day != str(date.today()):
    st.session_state.history.append({"date": st.session_state.day, "intake": st.session_state.intake, "goal": st.session_state.goal})
    st.session_state.day = str(date.today())
    st.session_state.intake = 0
    st.session_state.logs = []
    st.session_state.last_milestone = 0
    st.session_state.missions = {"Log your first drink": False, "Check your progress": False, "Explore the Fun Zone": False}

bg, panel, accent, accent2 = THEMES[st.session_state.theme]
motion_css = "" if st.session_state.reduced_motion else """
@keyframes floaty {0%,100%{transform:translateY(0) rotate(-3deg)}50%{transform:translateY(-13px) rotate(3deg)}}
@keyframes shimmer {0%{background-position:0% 50%}100%{background-position:200% 50%}}
@keyframes bubble-rise {0%{transform:translateY(24px) scale(.75);opacity:0}20%{opacity:.6}100%{transform:translateY(-110px) scale(1.15);opacity:0}}
@keyframes pop {0%{transform:scale(.65);opacity:.25}65%{transform:scale(1.08)}100%{transform:scale(1);opacity:1}}
@keyframes wave {0%{background-position:0 0}100%{background-position:120px 0}}
@keyframes glow {0%,100%{box-shadow:0 0 14px #55ddf644}50%{box-shadow:0 0 28px #55ddf699}}
"""
st.markdown(f"""<style>
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800;900&display=swap');
:root{{--wb-bg:{bg};--wb-panel:{panel};--wb-accent:{accent};--wb-accent2:{accent2};}}
html,body,[class*="css"]{{font-family:'Nunito',sans-serif;}}
.stApp{{background:radial-gradient(ellipse at 82% 0%,{panel} 0%,transparent 38%),linear-gradient(145deg,{bg},#07192b);color:#f4fbff;}}
.block-container{{max-width:1320px;padding-top:1.25rem;padding-bottom:3rem;}}
{motion_css}
.hero{{position:relative;overflow:hidden;border:1px solid #ffffff22;border-radius:28px;padding:30px 32px;background:linear-gradient(115deg,{panel}ee,{bg}dd);box-shadow:0 18px 55px #0003;}}
.hero:after{{content:' ';position:absolute;right:-40px;top:-95px;width:300px;height:300px;border-radius:50%;background:{accent}12;border:1px solid {accent}22;}}
.eyebrow{{font-size:.76rem;font-weight:900;letter-spacing:.18em;text-transform:uppercase;color:{accent};}}
.hero-title{{font-size:clamp(2rem,4vw,3.25rem);line-height:1.05;font-weight:900;letter-spacing:-.045em;margin:.5rem 0;}}
.hero-copy{{color:#c1d7e5;max-width:650px;font-size:1.02rem;}}
.mascot{{font-size:5.8rem;display:inline-block;filter:drop-shadow(0 12px 14px #00152288);{'' if st.session_state.reduced_motion else 'animation:floaty 3s ease-in-out infinite;'}}}
.glass{{background:linear-gradient(145deg,{panel}ee,#0a2942ee);border:1px solid #ffffff20;border-radius:22px;padding:20px;box-shadow:0 12px 32px #0002;height:100%;}}
.metric-label{{color:#b8d1e2;font-size:.84rem;font-weight:700;}}
.metric-value{{font-size:2rem;font-weight:900;letter-spacing:-.04em;margin-top:.25rem;}}
.metric-foot{{color:#b8d1e2;font-size:.78rem;}}
.pill{{display:inline-block;border:1px solid {accent}66;background:{accent}18;color:{accent};padding:6px 11px;border-radius:999px;font-weight:800;font-size:.78rem;}}
.speech{{display:inline-block;background:#e7fbff;color:#0b2a40;padding:11px 16px;border-radius:16px;font-weight:800;max-width:350px;{'' if st.session_state.reduced_motion else 'animation:pop .4s ease both;'}}}
.reward{{border:1px solid {accent}55;border-radius:16px;padding:14px;background:linear-gradient(120deg,{accent}19,{accent2}12);{'' if st.session_state.reduced_motion else 'animation:pop .4s ease both;'}}}
.bottle{{height:210px;width:92px;margin:10px auto 15px;border:4px solid #b8efff;border-radius:24px 24px 28px 28px;position:relative;overflow:hidden;background:#ffffff09;box-shadow:0 0 20px {accent}22;}}
.bottle:before{{content:'';position:absolute;top:-15px;left:24px;width:36px;height:18px;border:4px solid #b8efff;border-radius:7px 7px 0 0;background:{panel};}}
.water{{position:absolute;bottom:0;left:0;right:0;background:linear-gradient(180deg,{accent}cc,{accent2}aa);height:var(--fill);transition:height .85s cubic-bezier(.2,.8,.2,1);}}
.water:before{{content:'';position:absolute;top:-8px;left:-20%;width:140%;height:16px;border-radius:50%;background:{accent}cc;{'' if st.session_state.reduced_motion else 'animation:wave 2.8s linear infinite;'}}}
.bubble{{position:absolute;bottom:10px;left:18%;width:11px;height:11px;border-radius:50%;border:1px solid #ffffff99;{'' if st.session_state.reduced_motion else 'animation:bubble-rise 2.8s infinite;'}}}
.bubble.b2{{left:65%;width:7px;height:7px;animation-delay:1s;}}
.stButton>button{{border-radius:13px;border:1px solid #ffffff24;font-weight:900;transition:transform .15s,box-shadow .2s;}}
.stButton>button:hover{{transform:translateY(-2px);box-shadow:0 8px 22px {accent}2c;border-color:{accent}88;}}
section[data-testid="stSidebar"]{{background:#071526;border-right:1px solid #ffffff17;}}
section[data-testid="stSidebar"] *{{color:#f4fbff;}}
div[data-testid="stProgressBar"]>div>div>div>div{{background:linear-gradient(90deg,{accent},{accent2});}}
hr{{border-color:#ffffff1c;}}
.small-muted{{color:#b8d1e2;font-size:.84rem;}}
@media(prefers-reduced-motion:reduce){{*{{animation:none!important;transition:none!important;}}}}
</style>""", unsafe_allow_html=True)

# Sidebar settings / navigation
with st.sidebar:
    st.markdown(f"<div style='font-size:2.5rem'>💧</div><div style='font-size:1.55rem;font-weight:900'>Water<span style='color:{accent}'>Buddy</span></div><div class='small-muted'>Small sips. Big adventures.</div>", unsafe_allow_html=True)
    st.divider()
    page = st.radio("Explore", ["🏠 Dashboard", "💧 Water Log", "🗺️ Fun Zone", "📈 Progress", "⚙️ Settings"], label_visibility="collapsed")
    st.divider()
    st.markdown(f"<div class='glass' style='padding:14px'><div class='eyebrow'>TODAY'S BUDDY</div><div style='font-size:2.4rem'>{BUDDIES[st.session_state.buddy]}</div><b>{st.session_state.buddy}</b><p class='small-muted'>Here for every little win.</p></div>", unsafe_allow_html=True)
    st.caption("Hydration needs vary. This app is a habit tracker, not medical advice.")

pct = min(100, round(st.session_state.intake / max(1, st.session_state.goal) * 100))
remaining = max(0, st.session_state.goal - st.session_state.intake)
if pct >= 100:
    message = "Goal reached! You showed up for your routine. 🌟"
elif pct >= 75:
    message = "You're making waves! Keep listening to your body. 🌊"
elif pct >= 50:
    message = "Halfway through your target—nice steady progress! ✨"
elif pct >= 25:
    message = "Look at you go! Every logged sip helps build awareness. 💙"
elif st.session_state.intake > 0:
    message = "A lovely start. Your buddy is cheering you on! 🫧"
else:
    message = "Ready when you are. Let's make today flow!"

if page == "🏠 Dashboard":
    c1,c2 = st.columns([1.55,.8], gap="large")
    with c1:
        st.markdown(f"<div class='hero'><div class='eyebrow'>YOUR DAILY HYDRATION ADVENTURE</div><div class='hero-title'>Small sips.<br><span style='color:{accent}'>Big adventures.</span></div><p class='hero-copy'>A little water journal, a cheerful companion, and a fresh reason to celebrate the habits you're building.</p><span class='pill'>{AGE_GROUPS[st.session_state.age_group]['emoji']} {st.session_state.age_group}</span>&nbsp; <span class='pill'>✨ {st.session_state.experience}</span></div>", unsafe_allow_html=True)
    with c2:
        st.markdown(f"<div class='glass' style='text-align:center'><div class='mascot'>{BUDDIES[st.session_state.buddy]}</div><div style='font-size:1.35rem;font-weight:900'>{st.session_state.buddy} says…</div><div class='speech'>{message}</div><div style='margin-top:14px'><span class='pill'>Buddy level {1 + len(st.session_state.history) + pct//50}</span></div></div>", unsafe_allow_html=True)
    st.write("")
    a,b,c = st.columns(3)
    for col,label,value,foot in [
        (a,"💧 DRANK TODAY",f"{st.session_state.intake:,} ml","Your logged water so far"),
        (b,"🎯 STILL TO GO",f"{remaining:,} ml" if remaining else "Goal reached!","Compared with your daily target"),
        (c,"🌟 GOAL ACHIEVED",f"{pct}%","Live progress · capped at 100%")]:
        with col: st.markdown(f"<div class='glass'><div class='metric-label'>{label}</div><div class='metric-value'>{value}</div><div class='metric-foot'>{foot}</div></div>",unsafe_allow_html=True)
    st.write("")
    left,right = st.columns([1,1], gap="large")
    with left:
        st.markdown("<div class='glass'><div class='eyebrow'>YOUR WATER LEVEL</div><h3 style='margin:.2rem 0'>Watch your bottle fill</h3>",unsafe_allow_html=True)
        st.markdown(f"<div class='bottle' style='--fill:{pct}%'><div class='water' style='--fill:{pct}%'></div><div class='bubble'></div><div class='bubble b2'></div></div><div style='text-align:center;font-size:1.8rem;font-weight:900'>{pct}%</div><div style='text-align:center;color:#b8d1e2'>{st.session_state.intake:,} of {st.session_state.goal:,} ml</div></div>",unsafe_allow_html=True)
        st.progress(pct/100, text=f"{pct}% of daily goal")
    with right:
        st.markdown("<div class='glass'><div class='eyebrow'>QUICK LOG</div><h3 style='margin:.2rem 0'>What did you drink?</h3><p class='small-muted'>Choose a serving to update your dashboard instantly.</p>",unsafe_allow_html=True)
        q1,q2,q3 = st.columns(3)
        chosen = None
        if q1.button("🥤 100 ml", use_container_width=True): chosen=100
        if q2.button("💧 250 ml", use_container_width=True): chosen=250
        if q3.button("🧴 500 ml", use_container_width=True): chosen=500
        custom = st.number_input("Or enter an amount (ml)", min_value=0, max_value=5000, step=50, value=0)
        if st.button("＋ Add water", type="primary", use_container_width=True):
            amount = chosen if chosen else int(custom)
            if amount > 0:
                st.session_state.intake += amount
                st.session_state.logs.insert(0,{"time":datetime.now().strftime("%H:%M"),"amount":amount})
                st.session_state.missions["Log your first drink"] = True
                st.session_state.last_milestone = max(st.session_state.last_milestone, pct//25)
                st.rerun()
            else: st.warning("Choose a quick amount or enter a number greater than zero.")
        st.markdown("</div>",unsafe_allow_html=True)
    st.write("")
    st.markdown(f"<div class='reward'><b>✨ Your next little win</b><br><span class='small-muted'>{'You reached your daily goal—amazing consistency!' if pct>=100 else f'Your next progress milestone is {min(100, ((pct//25)+1)*25)}%. Log water whenever you drink it.'}</span></div>",unsafe_allow_html=True)
    if pct in (25,50,75,100) and st.session_state.intake > 0:
        st.balloons() if not st.session_state.reduced_motion else None
        st.success(f"Milestone reached: {pct}%! {BUDDIES[st.session_state.buddy]} {st.session_state.buddy} is celebrating with you.")
    st.markdown("#### Recent sips")
    if st.session_state.logs:
        for log in st.session_state.logs[:4]: st.markdown(f"<div class='reward' style='margin-bottom:8px'>{BUDDIES[st.session_state.buddy]} &nbsp; <b>{log['amount']} ml</b> <span style='float:right;color:#b8d1e2'>{log['time']}</span></div>",unsafe_allow_html=True)
    else: st.info("Your water journal is ready. Log your first drink whenever you're ready.")

elif page == "💧 Water Log":
    st.markdown("<div class='eyebrow'>YOUR WATER JOURNAL</div><h1>Every sip adds up 💧</h1><p class='small-muted'>Log water you actually drink. You can also review today's entries below.</p>",unsafe_allow_html=True)
    x,y = st.columns([1,1],gap="large")
    with x:
        st.markdown("<div class='glass'><h3>Quick log</h3>",unsafe_allow_html=True)
        amount = st.radio("Choose a serving",[100,250,350,500,750],horizontal=True,format_func=lambda x:f"{x} ml")
        custom = st.number_input("Custom amount (ml)",min_value=0,max_value=5000,step=50,value=0)
        if st.button("＋ Record water",type="primary",use_container_width=True):
            v=int(custom or amount); st.session_state.intake += v; st.session_state.logs.insert(0,{"time":datetime.now().strftime("%H:%M"),"amount":v}); st.session_state.missions["Log your first drink"]=True; st.rerun()
        st.markdown("</div>",unsafe_allow_html=True)
    with y:
        st.markdown(f"<div class='glass'><div class='metric-label'>TODAY'S TOTAL</div><div class='metric-value'>{st.session_state.intake:,} ml</div><div class='metric-foot'>{pct}% of {st.session_state.goal:,} ml target · {remaining:,} ml remaining</div></div>",unsafe_allow_html=True)
        if st.button("↺ Reset today's intake",use_container_width=True):
            st.session_state.intake=0;st.session_state.logs=[];st.session_state.last_milestone=0;st.rerun()
    st.subheader("Today's entries")
    if st.session_state.logs:
        for log in st.session_state.logs: st.markdown(f"<div class='reward' style='margin-bottom:8px'>{BUDDIES[st.session_state.buddy]} &nbsp; <b>{log['amount']} ml</b><span style='float:right;color:#b8d1e2'>{log['time']}</span></div>",unsafe_allow_html=True)
    else: st.info("No entries yet. Add your first drink above.")

elif page == "🗺️ Fun Zone":
    st.markdown("<div class='eyebrow'>PLAY YOUR WAY</div><h1>Fun Zone ✨</h1><p class='small-muted'>Choose your companion, change the atmosphere, and complete gentle habit missions.</p>",unsafe_allow_html=True)
    st.subheader("Choose your buddy")
    cols=st.columns(6)
    for i,(name,emoji) in enumerate(BUDDIES.items()):
        with cols[i]:
            st.markdown(f"<div class='glass' style='text-align:center;padding:12px'><div style='font-size:2.4rem'>{emoji}</div><b>{name}</b></div>",unsafe_allow_html=True)
            if st.button("Select" if name != st.session_state.buddy else "✓ Selected",key=f"buddy_{name}",use_container_width=True): st.session_state.buddy=name;st.rerun()
    st.subheader("Theme studio 🎨")
    cols=st.columns(3)
    for i,(name,colors) in enumerate(THEMES.items()):
        with cols[i%3]:
            st.markdown(f"<div class='glass'><div style='height:46px;border-radius:12px;background:linear-gradient(110deg,{colors[0]},{colors[2]},{colors[3]})'></div><b>{name}</b></div>",unsafe_allow_html=True)
            if st.button("Apply theme" if name != st.session_state.theme else "✓ Current theme",key=f"theme_{name}",use_container_width=True): st.session_state.theme=name;st.rerun()
    st.subheader("Daily missions")
    for mission in list(st.session_state.missions):
        checked=st.checkbox(mission,value=st.session_state.missions[mission],key=f"mission_{mission}")
        st.session_state.missions[mission]=checked
    completed=sum(st.session_state.missions.values())
    st.progress(completed/len(st.session_state.missions),text=f"{completed} of {len(st.session_state.missions)} missions checked")
    st.markdown(f"<div class='reward'><b>🏅 Buddy points: {st.session_state.intake//100 + completed*10}</b><br><span class='small-muted'>Points celebrate logging and exploring—not drinking beyond your needs.</span></div>",unsafe_allow_html=True)

elif page == "📈 Progress":
    st.markdown("<div class='eyebrow'>LITTLE STEPS ADD UP</div><h1>Your progress 📈</h1><p class='small-muted'>A snapshot of your hydration log. Previous days appear when recorded.</p>",unsafe_allow_html=True)
    records=st.session_state.history+[ {"date":str(date.today()),"intake":st.session_state.intake,"goal":st.session_state.goal} ]
    goals=sum(1 for r in records if r['intake']>=r['goal'])
    avg=round(sum(min(100,r['intake']/max(1,r['goal'])*100) for r in records)/len(records))
    a,b,c=st.columns(3)
    for col,label,val,foot in [(a,"📅 DAYS RECORDED",len(records),"Current and saved days"),(b,"🏆 GOALS REACHED",goals,"Days at 100% or more"),(c,"📊 AVERAGE PROGRESS",f"{avg}%","Capped at 100% per day")]:
        with col: st.markdown(f"<div class='glass'><div class='metric-label'>{label}</div><div class='metric-value'>{val}</div><div class='metric-foot'>{foot}</div></div>",unsafe_allow_html=True)
    st.subheader("Daily summaries")
    for r in reversed(records):
        rp=min(100,round(r['intake']/max(1,r['goal'])*100))
        st.markdown(f"<div class='glass' style='margin-bottom:10px'><b>{r['date']}</b><span style='float:right'>{r['intake']:,} / {r['goal']:,} ml</span><div style='margin-top:10px;background:#ffffff18;height:10px;border-radius:9px;overflow:hidden'><div style='height:100%;width:{rp}%;background:linear-gradient(90deg,{accent},{accent2});border-radius:9px'></div></div><div class='metric-foot' style='margin-top:6px'>{rp}% of goal</div></div>",unsafe_allow_html=True)
    if st.button("🌅 Finish day & save summary",type="primary"):
        st.session_state.history.append({"date":str(date.today()),"intake":st.session_state.intake,"goal":st.session_state.goal})
        st.session_state.show_summary=True
    if st.session_state.show_summary:
        st.balloons() if not st.session_state.reduced_motion else None
        st.success(f"Today's summary: {st.session_state.intake:,} ml logged — {pct}% of your tracking target. Tomorrow is a fresh start!")
        if st.button("Start a fresh day"):
            st.session_state.intake=0;st.session_state.logs=[];st.session_state.day=str(date.today());st.session_state.show_summary=False;st.session_state.last_milestone=0;st.rerun()

elif page == "⚙️ Settings":
    st.markdown("<div class='eyebrow'>MAKE IT YOURS</div><h1>Settings ⚙️</h1><p class='small-muted'>Personalise your experience and daily tracking target.</p>",unsafe_allow_html=True)
    age=st.selectbox("Age group",list(AGE_GROUPS),index=list(AGE_GROUPS).index(st.session_state.age_group))
    if age != st.session_state.age_group:
        old_goal=st.session_state.goal; old_pct=st.session_state.intake/max(1,old_goal)
        st.session_state.age_group=age;st.session_state.goal=AGE_GROUPS[age]["goal"];st.rerun()
    st.caption(AGE_GROUPS[st.session_state.age_group]["note"])
    st.session_state.goal=st.number_input("Daily tracking goal (ml)",min_value=500,max_value=5000,step=100,value=int(st.session_state.goal),help="Example tracking target only. It is not a universal medical recommendation.")
    st.session_state.experience=st.selectbox("Experience style",["Adventure mode","Teen mode","Calm mode"],index=["Adventure mode","Teen mode","Calm mode"].index(st.session_state.experience))
    st.session_state.reduced_motion=st.toggle("Reduce animations",value=st.session_state.reduced_motion,help="Switch this on if you prefer less movement.")
    st.info("Daily goals are illustrative tracking targets. Hydration needs vary with age, activity, climate, diet, and health. Follow a healthcare professional's advice for medical conditions or fluid restrictions.")
    if st.button("↺ Reset today's intake",type="secondary"):
        st.session_state.intake=0;st.session_state.logs=[];st.session_state.last_milestone=0;st.rerun()
    export={"day":st.session_state.day,"age_group":st.session_state.age_group,"goal_ml":st.session_state.goal,"intake_ml":st.session_state.intake,"logs":st.session_state.logs,"history":st.session_state.history,"buddy":st.session_state.buddy,"theme":st.session_state.theme}
    st.download_button("⬇️ Export my data (JSON)",data=json.dumps(export,indent=2),file_name="waterbuddy-data.json",mime="application/json")
    if st.button("Reset all app data",type="secondary"):
        for key in list(st.session_state.keys()): del st.session_state[key]
        st.rerun()

st.divider()
st.markdown(f"<div style='text-align:center;color:#a9c4d9;font-size:.82rem'>Made with 💧 and a little ocean magic · WaterBuddy · {date.today().strftime('%B %d, %Y')}<br>Habit tracking only — not medical advice.</div>",unsafe_allow_html=True)
