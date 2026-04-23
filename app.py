import streamlit as st
import itertools
import pandas as pd

# ==========================================
# 1. المحرك الرياضي (الدالة الأساسية)
# ==========================================
def generate_microstates(l, num_electrons):
    # توليد الغرف (قيم m_l من +l إلى -l)
    ml_values = list(range(l, -l - 1, -1))
    
    # توليد الكراسي المتاحة (تطبيق مبدأ باولي)
    available_seats = []
    for ml in ml_values:
        available_seats.append((ml, 0.5))  # إلكترون للأعلى
        available_seats.append((ml, -0.5)) # إلكترون للأسفل
        
    # إيجاد كل التوافيق الممكنة لتوزيع الإلكترونات
    microstates = list(itertools.combinations(available_seats, num_electrons))
    
    # حساب ML و MS لكل حالة وتجهيزها للعرض
    results = []
    for state in microstates:
        ML = sum(electron[0] for electron in state)
        MS = sum(electron[1] for electron in state)
        
        # تنسيق شكل التوزيعة لتكون مقروءة في الجدول
        # مثال: [ (+1, ↑), (0, ↓) ]
        formatted_state = " | ".join([f"({e[0]}, {'↑' if e[1]==0.5 else '↓'})" for e in state])
        
        results.append({
            "توزيع الإلكترونات (ml, Spin)": formatted_state,
            "ML (الزخم المداري)": ML,
            "MS (الزخم المغزلي)": MS
        })
        
    return results, len(available_seats)

# ==========================================
# 2. واجهة المستخدم (Streamlit)
# ==========================================

# إعدادات الصفحة
st.set_page_config(page_title="حاسبة الحالات الدقيقة للأطياف", layout="centered")

# العناوين
st.title("⚛️ برنامج حساب الحالات الدقيقة (Microstates)")
st.markdown("هذا البرنامج يقوم بحساب كافة التوافيق الممكنة للإلكترونات **المتكافئة** (Equivalent Electrons) مع مراعاة مبدأ باولي للاستبعاد.")
st.divider()

# أدوات الإدخال (مقسمة لعمودين لشكل أجمل)
col1, col2 = st.columns(2)

with col1:
    l_input = st.number_input(
        "أدخل رقم الكم المداري (l):", 
        min_value=0, max_value=3, value=1, 
        help="0 = s, 1 = p, 2 = d, 3 = f"
    )

with col2:
    # حساب السعة القصوى للمدار بناءً على قيمة l المدخلة
    max_capacity = (2 * l_input + 1) * 2
    e_input = st.number_input(
        f"أدخل عدد الإلكترونات (الحد الأقصى {max_capacity}):", 
        min_value=1, max_value=max_capacity, value=2
    )

st.divider()

# زر التشغيل
if st.button("احسب الحالات الدقيقة 🚀", use_container_width=True):
    
    # استدعاء دالة الحساب
    results, max_seats = generate_microstates(l_input, e_input)
    
    # عرض ملخص النتائج
    st.success(f"✅ تم اكتشاف **{len(results)}** حالة دقيقة (Microstate) مسموحة من أصل سعة مدارية تبلغ {max_seats} مقعد.")
    
    # تحويل النتائج إلى جدول Pandas لعرضها بشكل احترافي
    df = pd.DataFrame(results)
    
    # عرض الجدول
    st.dataframe(df, use_container_width=True, height=400)
    
    # تلميحة علمية أسفل الجدول
    st.info("💡 **تلميحة:** يمكنك فرز الجدول بالضغط على عناوين الأعمدة (مثلاً اضغط على ML لترتيب القيم تنازلياً لتسهيل استخراج الرموز الطيفية).")