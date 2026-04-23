import streamlit as st
import itertools
from collections import Counter
import pandas as pd
import math

# ==========================================
# 1. إعدادات الصفحة والتنسيق
# ==========================================
st.set_page_config(page_title="المحلل الكمومي التعليمي V5.4", layout="wide")

L_TO_LETTER = {0: 'S', 1: 'P', 2: 'D', 3: 'F', 4: 'G', 5: 'H', 6: 'I', 7: 'K', 8: 'L', 9: 'M', 10: 'N', 11: 'O'}

def get_l_from_letter(letter):
    if letter == "لا يوجد": return -1
    for k, v in L_TO_LETTER.items():
        if v == letter.upper(): return k
    return -1

def format_spin(s):
    return str(int(s)) if float(s).is_integer() else f"{int(s*2)}/2"

# دالة مخصصة لإنتاج كود LaTeX نقي (للمعادلات المستقلة)
def get_pure_latex_term(L, S, J=None):
    multi = int(2 * S + 1)
    letter = L_TO_LETTER.get(int(L), '?')
    if J is not None:
        return f"^{{{multi}}}\mathrm{{{letter}}}_{{{format_spin(J)}}}"
    return f"^{{{multi}}}\mathrm{{{letter}}}"

# دالة مخصصة للجداول (HTML)
def get_html_term(L, S, J=None):
    multi = int(2 * S + 1)
    letter = L_TO_LETTER.get(int(L), '?')
    if J is not None:
        return f"<sup>{multi}</sup>{letter}<sub>{format_spin(J)}</sub>"
    return f"<sup>{multi}</sup>{letter}"

# ==========================================
# 2. المحرك الرياضي والمنطقي
# ==========================================
def get_equivalent_terms(l, num_electrons):
    max_e = (2 * l + 1) * 2
    if num_electrons == 0 or l == -1: return [{'L': 0, 'S': 0}], []
    if num_electrons == max_e: return [{'L': 0, 'S': 0}], []

    ml_values = list(range(l, -l - 1, -1))
    seats = [(ml, 0.5) for ml in ml_values] + [(ml, -0.5) for ml in ml_values]
    combinations = list(itertools.combinations(seats, num_electrons))
    
    microstates = []
    for state in combinations:
        formatted = " | ".join([f"({e[0]},{'↑' if e[1]>0 else '↓'})" for e in state])
        microstates.append({'التوزيع (ml,s)': formatted, 'ML': sum(e[0] for e in state), 'MS': sum(e[1] for e in state)})
        
    states_map = Counter((round(s['ML'], 1), round(s['MS'], 1)) for s in microstates)
    terms = []
    while sum(states_map.values()) > 0:
        max_L = max([ml for (ml, ms), count in states_map.items() if count > 0])
        max_S = max([ms for (ml, ms), count in states_map.items() if count > 0 and ml == max_L])
        terms.append({'L': max_L, 'S': max_S})
        for ml in [max_L - i for i in range(int(max_L * 2 + 1))]:
            for ms in [max_S - i for i in range(int(max_S * 2 + 1))]:
                key = (round(ml, 1), round(ms, 1))
                if states_map[key] > 0: states_map[key] -= 1
    return terms, microstates

def couple_two_terms(t1, t2):
    coupled = []
    l_min, l_max = abs(t1['L'] - t2['L']), t1['L'] + t2['L']
    s_min, s_max = abs(t1['S'] - t2['S']), t1['S'] + t2['S']
    cl = l_min
    while cl <= l_max + 0.1:
        cs = s_min
        while cs <= s_max + 0.1:
            coupled.append({'L': cl, 'S': cs})
            cs += 1.0
        cl += 1.0
    return coupled

def couple_term_lists(list1, list2):
    final = []
    for t1 in list1:
        for t2 in list2:
            final.extend(couple_two_terms(t1, t2))
    return final

def calculate_J_values(term):
    L, S = term['L'], term['S']
    j_min, j_max = abs(L - S), L + S
    j_vals, cj = [], j_min
    while cj <= j_max + 0.1:
        j_vals.append(cj); cj += 1.0
    return j_vals

def check_transition(gs, target):
    if gs == target: return "N/A", "نفس الحالة"
    dL, dS, dJ = abs(gs['L'] - target['L']), abs(gs['S'] - target['S']), abs(gs['J'] - target['J'])
    if dS != 0: return "Forbidden (ممنوع)", "ΔS ≠ 0"
    if dL > 1: return "Forbidden (ممنوع)", "ΔL > 1"
    if dJ > 1: return "Forbidden (ممنوع)", "ΔJ > 1"
    if gs['J'] == 0 and target['J'] == 0: return "Forbidden (ممنوع)", "0 → 0"
    return "Allowed (مسموح)", "يحقق شروط ΔS, ΔL, ΔJ"

# ==========================================
# 3. واجهة المستخدم
# ==========================================
st.title("⚛️ المحلل الكمومي التعليمي V5.4")
st.markdown("أداة متقدمة لتحليل الأطياف الذرية، By Hayyano.")

with st.sidebar:
    st.header("⚙️ إعدادات النظام")
    orb1 = st.selectbox("المدار 1:", ["s", "p", "d", "f"], index=1)
    e1 = st.number_input("إلكترونات المدار 1:", 1, 14, 2)
    orb2 = st.selectbox("المدار 2 (اختياري):", ["لا يوجد", "s", "p", "d", "f"], index=2)
    e2 = st.number_input("إلكترونات المدار 2:", 0, 14, 3) if orb2 != "لا يوجد" else 0
    orb3 = st.selectbox("المدار 3 (اختياري):", ["لا يوجد", "s", "p", "d", "f"], index=0)
    e3 = st.number_input("إلكترونات المدار 3:", 0, 14, 0) if orb3 != "لا يوجد" else 0

if st.button("تحليل النظام وعرض خطوات الحل التفصيلية 🚀", use_container_width=True):
    active = [(get_l_from_letter(orb1), e1, orb1)]
    if orb2 != "لا يوجد" and e2 > 0: active.append((get_l_from_letter(orb2), e2, orb2))
    if orb3 != "لا يوجد" and e3 > 0: active.append((get_l_from_letter(orb3), e3, orb3))
    
    is_eq = len(active) == 1
    
    # =========================================================
    # مسار الإلكترونات المتكافئة
    # =========================================================
    if is_eq:
        l, e, name = active[0]
        st.header(f"📘 مسار الإلكترونات المتكافئة: المدار {name}")
        
        with st.expander("الخطوة 1: الحساب الإحصائي للميزانية (Total States)", expanded=True):
            max_c = (2*l+1)*2
            total = math.comb(max_c, e)
            st.latex(r"N_{Microstates} = \frac{(2(2l+1))!}{e! (2(2l+1)-e)!}")
            st.info(f"لدينا {max_c} مقعد متاح، اخترنا منها {e}. إجمالي الاحتمالات المسموحة لباولي هو: {total} حالة.")

        terms, ms_list = get_equivalent_terms(l, e)
        with st.expander("الخطوة 2: تكوين جدول التوافيق", expanded=True):
            st.write(f"وضعنا الإلكترونات في غرف المدار وجمعنا قيم الزخم المداري والمغزلي للحصول على (ML, MS):")
            st.dataframe(pd.DataFrame(ms_list), use_container_width=True)

        with st.expander("الخطوة 3: خوارزمية استخراج الرموز (طريقة الإلغاء/الشطب)", expanded=True):
            st.write("**المبدأ الأساسي:** كل رمز طيفي يمثل 'عائلة' من الحالات. هدفنا إيجاد هذه الرموز وحذف حالاتها من الجدول حتى يفرغ.")
            st.markdown("""
            * **1. البحث عن القمة:** ننظر في الجدول ونبحث عن أكبر رقم لـ $M_L$. إذا وجدنا أكثر من حالة لها نفس هذا الرقم، نختار الحالة التي تمتلك أكبر $M_S$.
            * **2. ترجمة القمة لرمز:** أكبر $M_L$ اخترناه هو حرف الرمز ($L$)، وأكبر $M_S$ هو المغزل ($S$). نحسب التعددية ($2S+1$) ونكتب الرمز.
            * **3. عملية الشطب:** الرمز الذي اكتشفناه يمتد أثره من $+L$ إلى $-L$ ومن $+S$ إلى $-S$. نعود للجدول ونشطب (نحذف) حالة واحدة لكل توافق بين هذه القيم.
            * **4. التكرار:** بعد عملية الشطب، ستقل الحالات في الجدول. نكرر الخطوات (نبحث عن قمة جديدة في الحالات المتبقية) ونستخرج رمزاً جديداً ونشطب حالاته، وهكذا حتى يختفي الجدول تماماً!
            """)
            st.markdown("---")
            st.write("**الرموز الناتجة النهائية بعد تصفية الجدول:**")
            
            # طباعة الرموز باستخدام LaTeX نقي لتجنب الخطأ الأحمر
            latex_terms = " \quad , \quad ".join([get_pure_latex_term(t['L'], t['S']) for t in terms])
            st.latex(latex_terms)

    # =========================================================
    # مسار الإلكترونات غير المتكافئة
    # =========================================================
    else:
        st.header("📗 مسار الإلكترونات غير المتكافئة (Vector Coupling)")
        
        subshell_data = []
        for l, e, name in active:
            t_list, _ = get_equivalent_terms(l, e)
            subshell_data.append({'name': name, 'e': e, 'terms': t_list})
            
        terms = subshell_data[0]['terms']
        for i in range(1, len(subshell_data)):
            terms = couple_term_lists(terms, subshell_data[i]['terms'])
            
        with st.expander("شرح مفصل: كيف تم حساب L و S والتعددية (Multiplicity)؟", expanded=True):
            st.write("بما أن الإلكترونات في مدارات مختلفة، نستخدم الجمع الاتجاهي المباشر لكل مدار على حدة.")
            
            st.markdown("#### 1️⃣ الرموز الطيفية لكل مدار بشكل منفصل:")
            for data in subshell_data:
                st.write(f"المدار **{data['name']}** ينتج عنه الرموز:")
                latex_sub_terms = " \quad , \quad ".join([get_pure_latex_term(t['L'], t['S']) for t in data['terms']])
                st.latex(latex_sub_terms)
                
            st.markdown("#### 2️⃣ استخراج L و S للحالة الأرضية:")
            st.write("لإيجاد الحالة الأرضية للنظام المدمج، نسحب الرمز ذو أعلى طاقة من كل مدار:")
            
            gs_parts = []
            for data in subshell_data:
                m_s = max(t['S'] for t in data['terms'])
                gs_t = max([t for t in data['terms'] if t['S'] == m_s], key=lambda x: x['L'])
                gs_parts.append(gs_t)
                st.write(f"الرمز الأعلى طاقة في المدار **{data['name']}** يمتلك القيم:")
                # عزل تام للمعادلات لتجنب تداخل الـ LTR/RTL
                st.latex(f"L = {gs_t['L']} \quad , \quad S = {format_spin(gs_t['S'])}")

            total_s_max = sum(p['S'] for p in gs_parts)
            total_l_max = sum(p['L'] for p in gs_parts)
            multiplicity = int(2 * total_s_max + 1)
            letter = L_TO_LETTER.get(int(total_l_max), '?')

            st.markdown("#### 3️⃣ حساب التعددية (Multiplicity) والزخم النهائي:")
            st.write("نطبق الجمع المباشر للمتجهات:")
            st.latex(f"S_{{sys}} = S_1 + S_2 \\dots = {format_spin(total_s_max)}")
            
            st.info(f"**التعددية (Multiplicity):** $2S + 1 = 2({format_spin(total_s_max)}) + 1 = \mathbf{{{multiplicity}}}$")
            
            st.latex(f"L_{{sys}} = L_1 + L_2 \\dots = {total_l_max}")
            
            st.success(f"الرقم ( L = {total_l_max} ) يعادل الحرف ( {letter} ). إذن الرمز الأساسي هو:")
            st.latex(get_pure_latex_term(total_l_max, total_s_max))

    # =========================================================
    # الجزء المشترك (J والحالة الأرضية والانتقالات)
    # =========================================================
    all_j_states = []
    for t in terms:
        for j in calculate_J_values(t):
            all_j_states.append({'L': t['L'], 'S': t['S'], 'J': j})
    
    unique_j = [dict(t) for t in {tuple(d.items()) for d in all_j_states}]
    
    st.divider()
    st.subheader("🎯 الحالة الأرضية وقواعد الانتقال")
    
    col_a, col_b = st.columns([1, 2])
    
    with col_a:
        st.write("**تحديد الحالة الأرضية (Hund's Rules):**")
        max_s = max(t['S'] for t in terms)
        gs_t = max([t for t in terms if t['S'] == max_s], key=lambda x: x['L'])
        if is_eq:
            l, e, _ = active[0]
            j_gs = abs(gs_t['L']-gs_t['S']) if e <= (2*l+1) else gs_t['L']+gs_t['S']
        else:
            j_gs = abs(gs_t['L']-gs_t['S']) 
            
        gs_final = {'L': gs_t['L'], 'S': gs_t['S'], 'J': j_gs}
        st.write(f"- أعلى تعددية متاحة للنظام: **{int(2*gs_t['S']+1)}**")
        st.write(f"- أعلى حرف مترافق معها: **{L_TO_LETTER[int(gs_t['L'])]}**")
        
        st.markdown("<br>", unsafe_allow_html=True)
        # تكبير الرمز النهائي وعرضه في المنتصف
        st.latex(r"\Huge " + get_pure_latex_term(gs_final['L'], gs_final['S'], gs_final['J']))

    with col_b:
        st.write("**جدول الانتقالات المسموحة من الحالة الأرضية:**")
        trans_list = []
        for target in unique_j:
            stat, msg = check_transition(gs_final, target)
            trans_list.append({
                "الحالة الهدف": get_html_term(target['L'], target['S'], target['J']), 
                "ΔS": abs(gs_final['S']-target['S']), 
                "ΔL": abs(gs_final['L']-target['L']), 
                "ΔJ": abs(gs_final['J']-target['J']), 
                "النتيجة": stat, 
                "السبب": msg
            })
        
        df_t = pd.DataFrame(trans_list)
        st.markdown(df_t.to_html(escape=False, index=False, justify='center'), unsafe_allow_html=True)

st.divider()
st.caption("تم تطوير هذا البرنامج لدعم البحث العلمي - قسم الكيمياء.")