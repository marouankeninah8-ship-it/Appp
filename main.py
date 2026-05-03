import streamlit as st
import json
import os
from datetime import datetime, timedelta
import random

# ========== إعداد الصفحة ==========
st.set_page_config(
    page_title="مذكرات الأبطال",
    page_icon="🦸",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ========== دوال نظام اللعبة ==========
def load_or_create_user(username):
    """تحميل بيانات المستخدم أو إنشاء جديد"""
    file_path = f"hero_data/{username}.json"
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        return {
            "username": username,
            "level": 1,
            "xp": 0,
            "streak": 0,
            "last_entry_date": None,
            "avatar_mood": "😐",
            "avatar_stage": 1,
            "achievements": [],
            "total_entries": 0,
            "story_unlocked": 0  # أجزاء القصة المفتوحة
        }

def save_user(data):
    """حفظ بيانات المستخدم"""
    if not os.path.exists("hero_data"):
        os.makedirs("hero_data")
    file_path = f"hero_data/{data['username']}.json"
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def analyze_mood(text):
    """تحليل المزاج من النص"""
    positive = ["سعيد", "فرح", "رائع", "جميل", "حب", "نجاح", "ممتن", "إيجابي", 
                "حمد", "شكر", "أمل", "تفاؤل", "قوة", "صحة", "مرح"]
    negative = ["حزين", "متعب", "سيء", "غاضب", "خوف", "قلق", "فشل", "سلبي",
                "ألم", "ضجر", "ملل", "غضب", "يأس", "ضعف", "تعب"]
    
    text_lower = text.lower()
    pos_score = sum(1 for word in positive if word in text_lower)
    neg_score = sum(1 for word in negative if word in text_lower)
    
    if pos_score > neg_score:
        return "إيجابي", "😊✨"
    elif neg_score > pos_score:
        return "سلبي", "😔💧"
    else:
        return "محايد", "😐"

def get_avatar_art(stage, mood):
    """إرجاع شكل الشخصية"""
    if stage == 1:
        base = "🧑"
    elif stage == 2:
        base = "🧙"
    else:
        base = "🦸"
    return f"{base}{mood}"

def add_xp(data, amount):
    """إضافة XP وتحديث المستوى"""
    data['xp'] += amount
    xp_needed = data['level'] * 50
    
    if data['xp'] >= xp_needed:
        data['xp'] -= xp_needed
        data['level'] += 1
        
        # تطور الشكل
        if data['level'] >= 10 and data['avatar_stage'] < 3:
            data['avatar_stage'] = 3
            data['story_unlocked'] = 3
            st.balloons()
            st.success("✨ شخصيتك تطورت لشكلها الأسطوري! 🦸")
        elif data['level'] >= 5 and data['avatar_stage'] < 2:
            data['avatar_stage'] = 2
            data['story_unlocked'] = 2
            st.snow()
            st.success("🌟 شخصيتك تطورت للمحارب! 🧙")
        
        return True
    return False

def update_streak(data):
    """تحديث الستريك"""
    today = datetime.now().date()
    
    if data['last_entry_date']:
        last_date = datetime.strptime(data['last_entry_date'], "%Y-%m-%d").date()
        diff = (today - last_date).days
        
        if diff == 1:
            data['streak'] += 1
        elif diff == 0:
            return []
        else:
            data['streak'] = 1
    else:
        data['streak'] = 1
    
    data['last_entry_date'] = today.strftime("%Y-%m-%d")
    
    # الإنجازات المرتبطة بالستريك
    new_achievements = []
    if data['streak'] == 3 and "🟢 أول 3 أيام متتالية" not in data['achievements']:
        new_achievements.append("🟢 أول 3 أيام متتالية")
    elif data['streak'] == 7 and "🔥 بطل الأسبوع" not in data['achievements']:
        new_achievements.append("🔥 بطل الأسبوع")
        data['xp'] += 30  # مكافأة إضافية
    elif data['streak'] == 10 and "💪 المقاتل المثابر" not in data['achievements']:
        new_achievements.append("💪 المقاتل المثابر")
    
    for achievement in new_achievements:
        if achievement not in data['achievements']:
            data['achievements'].append(achievement)
    
    return new_achievements

def save_entry(username, content, mood):
    """حفظ المذكرة"""
    if not os.path.exists("diary_entries"):
        os.makedirs("diary_entries")
    
    today_str = datetime.now().strftime("%Y-%m-%d")
    filename = f"diary_entries/{username}_{today_str}.txt"
    
    with open(filename, 'a', encoding='utf-8') as f:
        f.write(f"[{mood}] {datetime.now().strftime('%H:%M')}\n")
        f.write(content + "\n\n")

def get_story_segment(level):
    """قصة تتكشف مع التقدم"""
    stories = {
        1: "تبدأ رحلتك... أنت مجرد مسافر في عالم الذكريات.",
        2: "تكتشف أن للكلمات قوة سحرية... تبدأ في فهم مشاعرك.",
        3: "تظهر بوادر القوة... ذكرياتك تصبح أكثر وضوحاً.",
        5: "تصل إلى بوابة الحكمة... شخصيتك تتغير نحو الأفضل.",
        7: "تواجه تحدي الذكريات المؤلمة... لكنك تصبح أقوى.",
        10: "تصبح سيد الذكريات... قصتك تلهم الآخرين."
    }
    
    return stories.get(level, "مغامرتك مستمرة... استمر في الكتابة!")

# ========== واجهة المستخدم ==========
def main():
    # Sidbar للشخصية والمعلومات
    with st.sidebar:
        st.title("⚔️ مذكرات الأبطال")
        
        # تسجيل الدخول
        if 'user_data' not in st.session_state:
            username = st.text_input("👤 أدخل اسمك:", key="username_input")
            if username:
                st.session_state.user_data = load_or_create_user(username)
                st.rerun()
        else:
            user = st.session_state.user_data
            
            # عرض الشخصية
            st.markdown("---")
            avatar = get_avatar_art(user['avatar_stage'], user['avatar_mood'])
            st.markdown(f"# {avatar}")
            st.markdown(f"### {user['username']}")
            
            # شريط التقدم
            xp_needed = user['level'] * 50
            progress = user['xp'] / xp_needed
            st.progress(progress)
            st.caption(f"⚡ المستوى {user['level']} | XP: {user['xp']}/{xp_needed}")
            
            # الستريك
            st.markdown(f"🔥 الأيام المتتالية: **{user['streak']}**")
            
            # الإنجازات
            if user['achievements']:
                st.markdown("### 🏆 الإنجازات")
                for achievement in user['achievements']:
                    st.success(achievement)
            
            # تسجيل الخروج
            if st.button("🚪 تسجيل الخروج"):
                del st.session_state.user_data
                st.rerun()

    # المحتوى الرئيسي
    if 'user_data' not in st.session_state:
        st.title("🌟 مرحباً بك في مذكرات الأبطال")
        st.markdown("""
        ### حوّل يومياتك إلى مغامرة!
        - 📝 أكتب يومياتك
        - 🎮 تطور شخصيتك
        - 🏆 احصل على إنجازات
        - 📖 اكتشف قصتك الخاصة
        
        **أدخل اسمك في الشريط الجانبي للبدء!**
        """)
    else:
        user = st.session_state.user_data
        
        # تبويبات
        tab1, tab2, tab3 = st.tabs(["📝 كتابة", "📊 الإحصائيات", "📖 القصة"])
        
        with tab1:
            st.header("✍️ اكتب يوميتك")
            
            # محرر النصوص
            entry_text = st.text_area(
                "ماذا حدث اليوم؟ كيف تشعر؟",
                height=200,
                placeholder="اكتب بحرية... شخصيتك تتأثر بكلماتك!"
            )
            
            col1, col2, col3 = st.columns([2, 1, 1])
            with col1:
                if st.button("💾 احفظ يوميتي", use_container_width=True):
                    if entry_text.strip():
                        # تحليل المزاج
                        mood, mood_emoji = analyze_mood(entry_text)
                        user['avatar_mood'] = mood_emoji
                        
                        # إضافة XP
                        base_xp = 10
                        if mood == "إيجابي":
                            base_xp += 5
                            st.balloons()
                        
                        leveled_up = add_xp(user, base_xp)
                        
                        # تحديث الستريك
                        new_achievements = update_streak(user)
                        
                        # حفظ المذكرة
                        save_entry(user['username'], entry_text, mood)
                        user['total_entries'] += 1
                        
                        # حفظ البيانات
                        save_user(user)
                        
                        # رسائل التأكيد
                        st.success(f"تم حفظ يوميتك! المزاج: {mood} {mood_emoji}")
                        st.info(f"+{base_xp} XP")
                        
                        if leveled_up:
                            st.balloons()
                            st.success(f"🎉 تهانينا! وصلت للمستوى {user['level']}!")
                        
                        for achievement in new_achievements:
                            st.success(f"🏆 إنجاز جديد: {achievement}")
                            st.balloons()
                    else:
                        st.warning("اكتب شيئاً أولاً!")
        
        with tab2:
            st.header("📊 إحصائيات البطل")
            
            # بطاقات الإحصائيات
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("المستوى", user['level'])
            with col2:
                st.metric("إجمالي XP", user['xp'])
            with col3:
                st.metric("الأيام المتتالية", f"🔥 {user['streak']}")
            with col4:
                st.metric("عدد اليوميات", user['total_entries'])
            
            # شريط تقدم كبير
            st.markdown("### ⚡ التقدم للمستوى التالي")
            xp_needed = user['level'] * 50
            progress = user['xp'] / xp_needed
            st.progress(progress, text=f"{user['xp']}/{xp_needed} XP")
            
            # الإنجازات
            if user['achievements']:
                st.markdown("### 🏆 إنجازاتك")
                cols = st.columns(len(user['achievements']))
                for i, achievement in enumerate(user['achievements']):
                    with cols[i]:
                        st.success(achievement)
        
        with tab3:
            st.header("📖 قصتك الملحمية")
            
            # عرض القصة حسب المرحلة
            st.markdown(f"### {get_story_segment(user['avatar_stage'])}")
            
            # شخصيتك الحالية
            avatar = get_avatar_art(user['avatar_stage'], user['avatar_mood'])
            st.markdown(f"# {avatar}")
            
            # وصف الشخصية
            if user['avatar_stage'] == 1:
                st.info("أنت في بداية رحلتك... كل يومية تقويك!")
            elif user['avatar_stage'] == 2:
                st.success("أنت محارب الذكريات! قوتك تزداد.")
            else:
                st.balloons()
                st.success("أنت أسطورة! ذكرياتك تشكل عالمك.")
            
            # نصائح تحفيزية
            quotes = [
                "كل كلمة هي خطوة نحو القوة...",
                "ذكرياتك هي كنزك الحقيقي...",
                "في كل يوم جديد، قصة جديدة...",
                "أنت بطل قصتك... لا تنسى ذلك!"
            ]
            st.caption(f"💭 {random.choice(quotes)}")

if __name__ == "__main__":
    main()
