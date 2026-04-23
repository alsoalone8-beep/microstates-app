import streamlit as st
import itertools
from collections import Counter
import pandas as pd
import math

st.set_page_config(page_title="المحلل الكمومي V6.0", layout="wide")

L_TO_LETTER = {0: 'S', 1: 'P', 2: 'D', 3: 'F', 4: 'G', 5: 'H', 6: 'I', 7: 'K', 8: 'L', 9: 'M'}

def get_l_from_letter(letter):
    for k, v in L_TO_LETTER.items():
        if v == letter.upper(): return k
    return -1

def format_spin(s):
    return str(int(s)) if float(s).is_integer() else f"{int(s*2)}/2"

def get_pure_latex_term(L, S, J=None):
    multi = int(2 * S + 1)
    letter = L_TO_LETTER.get(int(L), '?')
    if J is not None:
        return f"^{{{multi}}}\mathrm{{{letter}}}_{{{format_spin(J)}}}"
    return f"^{{{multi}}}\mathrm{{{letter}}}"

# ---------------------------------------------------------
# دالة جديدة: توليد رسم الـ HTML لغرف المدارات (الصناديق)
# ---------------------------------------------------------
def draw_orbital_boxes(l, config_dict, title, explanation):
    html = f"<h5>{title}</h5><p style='color:gray;'>{explanation}</p>"
    html += "<div style='display: flex; justify-content: center; gap: 10px; margin-bottom: 20px; direction: ltr;'>"
    
    ml_values = list(range(l, -l - 1, -1))
    for ml in ml_values:
        arrows = config_dict.get(ml, "")
        color = "#1e3d59" if arrows else "#2b2b2b"
        html += f"""
        <div style='text-align: center;'>
            <div style='margin-bottom: 5px; font-weight: bold; color: #ffeb3b;'>{ml}</div>
            <div style='width: 60px; height: 60px; border: 2px solid #8fce00; border-radius: 8px; 
                        background-color: {color}; display: flex; align-items: center; 
                        justify-content: center; font-size: 30px; color: white;'>
                {arrows}
            </div>
        </div>
        """
    html += "</div><hr>"
    return html

# ---------------------------------------------------------
# المحرك الرياضي
# ---------------------------------------------------------
def get_equivalent_terms(l, num_electrons):
    max_e = (2 * l + 1) * 2
    if num_electrons == 0 or num_electrons == max_e: return [{'L': 0, 'S': 0}]
    ml_values = list(range(l, -l - 1, -1))
    seats = [(ml, 0.5) for ml in ml_values] + [(ml, -0.5) for ml in ml_values]
    combinations = list(itertools.combinations(seats, num_electrons))
    states_map = Counter((round(sum(e[0] for e in s), 1), round(sum(e[1] for e in s), 1)) for s in combinations)
    terms = []
    while sum(states_map.values()) > 0:
        max_L = max([ml for (ml, ms), count in states_map.items() if count > 0])
        max_S = max([ms for (ml, ms), count in states_map.items() if count > 0 and ml == max_L])
        terms.append({'L': max_L, 'S': max_S})
        for ml in [max_L - i for i in range(int(max_L * 2 + 1))]:
            for ms in [max_S - i for i in range(int(max_S * 2 + 1))]:
                key = (round(ml, 1), round(ms, 1))
                if states_map[key] > 0: states_map[key] -= 1
    return terms

def calculate_J_values(term):
    L, S = term['L'], term['S']
    j_min, j_max = abs(L - S), L + S
    j_vals, cj = [], j_min
    while cj <= j_max + 0.1:
        j_vals.append(cj); cj += 1.0
    return j_vals

# ---------------------------------------------------------
# واجهة المستخدم
# ---------------------------------------------------------
st.title("⚛️ المحلل الكمومي V6.0 (المحاكاة الذهنية)")
st.markdown("تمت إضافة **طريقة المربعات والأسهم (الحل اليدوي)** لمحاكاة طريقة التفكير البشري دون جداول.")

with st.sidebar:
    st.header("إعدادات النظام")
    orb1 = st.selectbox("المدار:", ["s", "p", "d", "f"], index=2)
    e1 = st.number_input("عدد الإلكترونات:", 1, 14, 2)

if st.button("تحليل النظام وعرض الحل الذهني 🚀", use_container_width=True):
    l = get_l_from_letter(orb1)
    max_cap = (2*l+1)*2
    
    if e1 > max_cap:
        st.error("عدد الإلكترونات يتجاوز سعة المدار!")
        st.stop()
        
    st.header(f"📘 مسار الحل اليدوي (طريقة المربعات): المدار ${orb1}^{{{e1}}}$")
    
    # ========================================================
    # محاكاة الورقة المكتوبة بخط اليد (رسم الغرف)
    # ========================================================
    with st.expander("الخطوة 1: استخراج الرموز ذهنياً (طريقة رسم الغرف والأسهم)", expanded=True):
        st.write("بدلاً من بناء جدول يحتوي على كل الحالات، سنقوم بملء الغرف $m_l$ للحصول على 'القمم' (Highest $M_L$ and $M_S$) مباشرة، تماماً كما نفعل بالورقة والقلم:")
        
        # 1. محاكاة أعلى غزل (Max S) -> للحصول على ^3F في حالة d2
        config_max_s = {}
        e_temp = e1
        ml_vals = list(range(l, -l - 1, -1))
        # توزيع مفرد أولاً (أقصى غزل)
        for ml in ml_vals:
            if e_temp > 0:
                config_max_s[ml] = "↑"
                e_temp -= 1
        
        S_max = e1 * 0.5 if e1 <= (2*l+1) else ((2*l+1)*0.5) - ((e1-(2*l+1))*0.5)
        L_max_s = sum(ml_vals[:e1]) if e1 <= (2*l+1) else sum(ml_vals) + sum(ml_vals[:e1-(2*l+1)])
        
        html_boxes = draw_orbital_boxes(l, config_max_s, 
                                      f"1. استخراج الرمز الأساسي (أعلى غزل وأعلى زخم):", 
                                      f"نقوم بتوزيع الإلكترونات فرادى وبنفس اتجاه الغزل (↑) بدءاً من أعلى غرفة (+{l}).")
        st.markdown(html_boxes, unsafe_allow_html=True)
        
        multiplicity_1 = int(2*S_max + 1)
        st.latex(rf"L = {L_max_s} \quad , \quad S = {format_spin(S_max)} \implies \text{{الرمز الأول هو: }} {get_pure_latex_term(L_max_s, S_max)}")
        
        # 2. محاكاة أعلى زخم (Max L) -> للحصول على ^1G في حالة d2
        if e1 >= 2 and e1 <= (2*l+1):
            config_max_l = {l: "↑↓"} # إجبار إلكترونين في أعلى غرفة
            html_boxes_2 = draw_orbital_boxes(l, config_max_l, 
                                          f"2. استخراج الرمز الثاني (إجبار التزاوج للحصول على أعلى L):", 
                                          f"للحصول على أعلى قيمة $L$ ممكنة، نجبر إلكترونين على السكن في أعلى غرفة (+{l}). وبسبب مبدأ باولي يجب أن يكون الغزل متعاكساً (↑↓) مما يجعل $S=0$.")
            st.markdown(html_boxes_2, unsafe_allow_html=True)
            
            L_max_l = l * 2
            st.latex(rf"L = {L_max_l} \quad , \quad S = 0 \implies \text{{الرمز الثاني هو: }} {get_pure_latex_term(L_max_l, 0)}")

        st.info("💡 **ملاحظة:** العقل البشري يدرك أن الرمز الأول ابتلع جزءاً من الحالات، والرمز الثاني ابتلع جزءاً آخر. وتستمر بتبديل أماكن الأسهم ذهنياً لاستخراج باقي الرموز (مثل $^1D, ^3P, ^1S$) دون الحاجة لكتابة 45 حالة!")

    # ========================================================
    # الانقسام الدقيق والحالة الأرضية
    # ========================================================
    terms = get_equivalent_terms(l, e1)
    
    with st.expander("الخطوة 2: الانقسام الدقيق (حساب J لكل الرموز المكتشفة)", expanded=True):
        st.write("بعد استخراج جميع الرموز الرئيسية، نحسب الانقسام الدقيق لها باستخدام $J = |L - S| \dots L + S$")
        all_j_states = []
        for t in terms:
            for j in calculate_J_values(t):
                all_j_states.append({'L': t['L'], 'S': t['S'], 'J': j})
        
        unique_j = [dict(t) for t in {tuple(d.items()) for d in all_j_states}]
        latex_fine = " \quad , \quad ".join([get_pure_latex_term(s['L'], s['S'], s['J']) for s in unique_j])
        st.latex(latex_fine)

    with st.expander("الخطوة 3: تحديد الحالة الأرضية (Hund's Rules)", expanded=True):
        max_s = max(t['S'] for t in terms)
        gs_t = max([t for t in terms if t['S'] == max_s], key=lambda x: x['L'])
        j_gs = abs(gs_t['L']-gs_t['S']) if e1 <= (2*l+1) else gs_t['L']+gs_t['S']
        
        st.write(f"- نبحث عن أعلى تعددية (Max S) وأعلى حرف مترافق (Max L).")
        st.write(f"- المدار $d^{e1}$ {'نصف ممتلئ أو أقل (نأخذ أصغر J)' if e1 <= (2*l+1) else 'أكثر من نصف ممتلئ (نأخذ أكبر J)'}.")
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.latex(r"\Huge \text{Ground State: } " + get_pure_latex_term(gs_t['L'], gs_t['S'], j_gs))
