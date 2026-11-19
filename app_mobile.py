import streamlit as st
import os
import requests
API_URL = os.getenv("API_URL", "http://localhost:8000")
# Responsive interface for desktop browsers, tablets and mobile browsers.

def ai_translate_text(text, target_lang="ru"):
    if not text or not text.strip():
        return text
    lang_map = {"tj": "tg", "ru": "ru", "en": "en", "uz": "uz", "kz": "kk", "kg": "ky", "fa": "fa", "ar": "ar", "tr": "tr", "zh": "zh-CN", "es": "es", "de": "de", "fr": "fr"}
    tgt = lang_map.get(target_lang, target_lang)
    try:
        from deep_translator import GoogleTranslator
        return GoogleTranslator(source="auto", target=tgt).translate(text)
    except Exception:
        pass
    try:
        r = requests.get(
            "https://googleapis.com",
            params={"client": "gtx", "sl": "auto", "tl": tgt, "dt": "t", "q": text},
            timeout=6
        )
        if r.status_code == 200:
            data = r.json()
            return "".join([x[0] for x in data[0] if x[0]])
    except Exception:
        pass
    return text

st.set_page_config(page_title="NABZ — Social Network", page_icon="⚡", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
    .stApp, [data-testid="stSidebar"], [data-testid="stSidebar"] > div:first-child { background-color: #0E0E14 !important; color: #FFFFFF !important; }
    header[data-testid="stHeader"] { background-color: #0E0E14 !important; }
    header[data-testid="stHeader"] svg, [data-testid="collapsedControl"] svg { fill: #00F2FE !important; color: #00F2FE !important; }
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] span, [data-testid="stSidebar"] label, .stApp h1, .stApp h2, .stApp h3, .stApp h4, label, [data-testid="stWidgetLabel"] p { color: #FFFFFF !important; }
    [role="tab"], [role="tab"] p, [role="tab"] span, [data-baseweb="tab"], [data-baseweb="tab"] p, [data-baseweb="tab"] span { color: #D8D8EC !important; font-weight: 600 !important; font-size: 16px !important; }
    [role="tab"][aria-selected="true"], [role="tab"][aria-selected="true"] p, [data-baseweb="tab"][aria-selected="true"], [data-baseweb="tab"][aria-selected="true"] p { color: #00F2FE !important; }
    input, textarea, [data-baseweb="select"] > div { background-color: #1A1A26 !important; color: #FFFFFF !important; border: 1px solid #3A3A55 !important; border-radius: 10px !important; }
    div.stButton > button, div.stButton > button p { background-color: #00F2FE !important; color: #000000 !important; font-weight: 700 !important; border-radius: 20px !important; border: none !important; }
    .phone-header { text-align: center; color: #00F2FE; font-size: 28px; font-weight: bold; margin-bottom: 2px; }
    .phone-slogan { text-align: center; color: #A0AEC0; font-size: 14px; margin-bottom: 15px; }
    .comment-box { background-color: #1A1A24; color: #FFFFFF; padding: 10px; border-radius: 10px; margin-bottom: 6px; border-left: 3px solid #00F2FE; }
    .reply-box { background-color: #15151E; color: #E2E8F0; padding: 8px; border-radius: 8px; margin-left: 25px; margin-bottom: 6px; border-left: 2px solid #8F9CAF; }
    .repost-badge { background-color: #1E2430; padding: 5px 10px; border-radius: 8px; color: #00F2FE; font-size: 13px; margin-bottom: 8px; }
    [data-testid="stExpander"] { background-color: #15151F !important; border: 1px solid #2D2D44 !important; border-radius: 12px !important; }
    [data-testid="stAlert"] { background-color: #161A24 !important; color: #FFFFFF !important; border: 1px solid #00F2FE !important; border-radius: 12px !important; }
    [data-testid="stAlert"] * { color: #FFFFFF !important; }
    [data-testid="stAlert"], [data-testid="stAlert"] > div, div[role="alert"], div[role="alert"] > div { background-color: #181C28 !important; color: #FFFFFF !important; border-color: #00F2FE !important; border-radius: 12px !important; }
    [data-testid="stAlert"] *, div[role="alert"] * { color: #FFFFFF !important; }

    /* Скрываем лишние системные элементы Streamlit (Fork, GitHub, меню, красную корону) */
    #MainMenu, footer, .stDeployButton, [data-testid="stToolbar"], [data-testid="stDecoration"], [data-testid="stStatusWidget"] {
        display: none !important;
        visibility: hidden !important;
    }
    /* Делаем кнопку открытия бокового меню яркой и заметной на телефоне */
    [data-testid="collapsedControl"], button[kind="header"] {
        background-color: #00F2FE !important;
        color: #000000 !important;
        border-radius: 50% !important;
        width: 40px !important;
        height: 40px !important;
        margin: 8px !important;
        box-shadow: 0 0 12px rgba(0, 242, 254, 0.7) !important;
    }
    [data-testid="collapsedControl"] svg {
        fill: #000000 !important;
        color: #000000 !important;
    }
    /* Каскадные облачка сообщений в чате */
    .chat-row-me {
        display: flex;
        justify-content: flex-start;
        margin-bottom: 10px;
    }
    .chat-row-other {
        display: flex;
        justify-content: flex-end;
        margin-bottom: 10px;
    }
    .bubble-me {
        background: linear-gradient(135deg, #0D3B4C 0%, #114B5F 100%);
        border: 1px solid #00F2FE;
        color: #FFFFFF;
        padding: 10px 14px;
        border-radius: 18px 18px 18px 4px;
        max-width: 82%;
        box-shadow: 0 2px 8px rgba(0, 242, 254, 0.15);
    }
    .bubble-other {
        background: #1E1E2E;
        border: 1px solid #3A3A52;
        color: #FFFFFF;
        padding: 10px 14px;
        border-radius: 18px 18px 4px 18px;
        max-width: 82%;
    }
    .chat-header-card {
        background: #161622;
        border: 1px solid #2D2D44;
        border-radius: 16px;
        padding: 12px;
        margin-bottom: 12px;
        display: flex;
        align-items: center;
        gap: 12px;
    }

    details, summary, [data-testid="stExpander"] summary { background-color: #161622 !important; color: #FFFFFF !important; }

    /* NABZ responsive refresh: desktop, tablet and mobile */
    :root {
        color-scheme: dark;
        --nabz-bg: #0b1017;
        --nabz-panel: #151e29;
        --nabz-panel-soft: #1b2734;
        --nabz-border: #293847;
        --nabz-cyan: #00d9e8;
        --nabz-text: #edf4f8;
        --nabz-muted: #9aabba;
    }
    .stApp {
        background:
          radial-gradient(ellipse at 50% -20%, rgba(0,217,232,.09), transparent 48%),
          var(--nabz-bg) !important;
        color: var(--nabz-text) !important;
    }
    [data-testid="stMain"] > div {
        padding-top: 1.1rem;
    }
    [data-testid="stMainBlockContainer"] {
        max-width: 1500px !important;
        padding-left: clamp(1rem, 3vw, 2.6rem) !important;
        padding-right: clamp(1rem, 3vw, 2.6rem) !important;
        padding-bottom: 5.5rem !important;
    }
    [data-testid="stSidebar"] {
        background: #101923 !important;
        border-right: 1px solid var(--nabz-border);
    }
    [data-testid="stSidebar"] > div:first-child {
        background: #101923 !important;
    }
    [data-testid="stSidebar"] [data-testid="stRadio"] label {
        border-radius: 12px;
        padding: .28rem .45rem;
        transition: background .18s ease;
    }
    [data-testid="stSidebar"] [data-testid="stRadio"] label:hover {
        background: #1b2a37;
    }
    .phone-header {
        text-align: left !important;
        font-size: clamp(1.7rem, 3vw, 2.25rem) !important;
        letter-spacing: -.06em;
        font-weight: 850 !important;
        margin: 0 auto .1rem !important;
        max-width: 1100px;
    }
    .phone-slogan {
        text-align: left !important;
        max-width: 1100px;
        margin: 0 auto 1.25rem !important;
        color: var(--nabz-muted) !important;
    }
    .stButton > button, .stDownloadButton > button, .stLinkButton > a {
        min-height: 2.55rem;
        border-radius: 999px !important;
        padding: .45rem 1rem !important;
        transition: transform .15s ease, filter .15s ease;
    }
    .stButton > button:hover, .stDownloadButton > button:hover,
    .stLinkButton > a:hover {
        transform: translateY(-1px);
        filter: brightness(1.08);
    }
    input, textarea, [data-baseweb="select"] > div {
        border-radius: 13px !important;
    }
    [data-testid="stExpander"] {
        background: var(--nabz-panel) !important;
        border: 1px solid var(--nabz-border) !important;
        border-radius: 16px !important;
        overflow: hidden;
    }
    [data-testid="stVerticalBlock"] > [data-testid="stHorizontalBlock"] {
        gap: 1rem;
    }
    [data-testid="stImage"] img, [data-testid="stVideo"] video {
        border-radius: 14px;
    }
    .comment-box, .reply-box {
        border-radius: 12px !important;
    }
    .repost-badge {
        border: 1px solid #2d5360;
    }
    .nabz-bottom-bar {
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        background: rgba(13, 22, 31, .94) !important;
        border-top: 1px solid rgba(0,217,232,.35) !important;
        box-shadow: 0 -8px 28px rgba(0,0,0,.28) !important;
    }
    .nabz-bottom-bar a {
        min-width: 42px;
        text-align: center;
        color: #eafaff !important;
        border: 1px solid #2b4350 !important;
        background: #182632 !important;
    }
    @media (min-width: 900px) {
        .nabz-bottom-bar { display: none !important; }
        [data-testid="stMainBlockContainer"] {
            padding-top: 1.6rem !important;
            padding-bottom: 2rem !important;
        }
        [data-testid="stSidebar"] {
            min-width: 265px !important;
            width: 265px !important;
        }
        .phone-header, .phone-slogan {
            max-width: 1180px;
        }
    }
    @media (min-width: 600px) and (max-width: 899px) {
        [data-testid="stMainBlockContainer"] {
            padding-left: 1.2rem !important;
            padding-right: 1.2rem !important;
        }
        .nabz-bottom-bar a {
            font-size: 21px !important;
            padding: 6px 10px !important;
        }
    }
    @media (max-width: 599px) {
        [data-testid="stMainBlockContainer"] {
            padding-left: .8rem !important;
            padding-right: .8rem !important;
            padding-top: .55rem !important;
            padding-bottom: 5.8rem !important;
        }
        .phone-header { text-align: center !important; font-size: 1.75rem !important; }
        .phone-slogan { text-align: center !important; margin-bottom: .8rem !important; }
        [data-testid="stHorizontalBlock"] {
            flex-wrap: wrap !important;
            gap: .45rem !important;
        }
        [data-testid="stHorizontalBlock"] > [data-testid="column"] {
            min-width: min(100%, 125px) !important;
        }
        .nabz-bottom-bar {
            height: 60px !important;
            padding-bottom: env(safe-area-inset-bottom);
        }
        .nabz-bottom-bar a {
            font-size: 20px !important;
            padding: 7px 9px !important;
            min-width: 39px;
        }
        div.stButton > button {
            width: 100%;
            white-space: normal !important;
            min-height: 2.65rem;
        }
        [data-testid="stImage"] img, [data-testid="stVideo"] video {
            max-width: 100%;
        }
    }

</style>

""", unsafe_allow_html=True)

LANG_TEXT = {
    "ru": {
        "slogan": "Пульс твоего мира",
        "nav": "Навигация по NABZ",
        "login": "🔐 Вход / Регистрация",
        "feed": "🎬 Общая лента",
        "subs": "👥 Мои подписки",
        "bookmarks": "🔖 Избранное",
        "create": "➕ Создать пост",
        "drafts": "📝 Черновики",
        "profile": "👤 Мой профиль",
        "notifs": "🔔 Уведомления",
        "chat": "💬 Чат",
        "search": "🔍 Поиск по тексту, #хэштегам или @авторам",
        "follow": "➕ Подписаться",
        "unfollow": "✓ Вы подписаны",
        "repost": "🔁 Репост",
        "bookmark": "🔖 В закладки",
        "report": "⚠️ Жалоба",
        "block": "🚫 Заблокировать автора",
        "logout": "🚪 Выйти из аккаунта"
    },
    "tj": {
        "slogan": "Набзи ҷаҳони ту",
        "nav": "Менюи NABZ",
        "login": "🔐 Вуруд / Бақайдгирӣ",
        "feed": "🎬 Лентаи умумӣ",
        "subs": "👥 Обунаҳои ман",
        "bookmarks": "🔖 Захирашудаҳо",
        "create": "➕ Нашри нав",
        "drafts": "📝 Сиёҳнависҳо",
        "profile": "👤 Профили ман",
        "notifs": "🔔 Огоҳиномаҳо",
        "chat": "💬 Чат",
        "search": "🔍 Ҷустуҷӯ бо матн, #ҳэштег ё @муаллиф",
        "follow": "➕ Обуна шудан",
        "unfollow": "✓ Обуна ҳастед",
        "repost": "🔁 Бознашр",
        "bookmark": "🔖 Захира кардан",
        "report": "⚠️ Шикоят",
        "block": "🚫 Маҳкам кардан",
        "logout": "🚪 Баромадан"
    },
    "en": {
        "slogan": "Pulse of your world",
        "nav": "NABZ Navigation",
        "login": "🔐 Login / Sign Up",
        "feed": "🎬 Global Feed",
        "subs": "👥 Following",
        "bookmarks": "🔖 Bookmarks",
        "create": "➕ Create Post",
        "drafts": "📝 Drafts",
        "profile": "👤 My Profile",
        "notifs": "🔔 Notifications",
        "chat": "💬 Chat",
        "search": "🔍 Search text, #hashtags or @authors",
        "follow": "➕ Follow",
        "unfollow": "✓ Following",
        "repost": "🔁 Repost",
        "bookmark": "🔖 Bookmark",
        "report": "⚠️ Report",
        "block": "🚫 Block user",
        "logout": "🚪 Logout"
    }
}

if "username" not in st.session_state:
    st.session_state["username"] = st.query_params.get("u", None)
if "lang" not in st.session_state:
    st.session_state["lang"] = "ru"
if "feed_limit" not in st.session_state:
    st.session_state["feed_limit"] = 10

lang_choice = st.sidebar.selectbox("🌐 Язык / Забон / Language", ["ru", "tj", "en"], index=["ru", "tj", "en"].index(st.session_state["lang"]))
if lang_choice != st.session_state["lang"]:
    st.session_state["lang"] = lang_choice
    st.rerun()

T = LANG_TEXT[st.session_state["lang"]]

st.markdown('<div class="phone-header">⚡ NABZ</div>', unsafe_allow_html=True)
st.markdown(f'<div class="phone-slogan">{T["slogan"]}</div>', unsafe_allow_html=True)

# Жёстко закреплённая нижняя панель навигации (в 1 ряд внизу экрана)
if st.session_state["username"]:
    u_now = st.session_state["username"]
    st.markdown(f"""
    <style>
        .block-container {{ padding-bottom: 85px !important; }}
        details, summary, [data-testid="stExpander"] summary {{ background-color: #161622 !important; color: #FFFFFF !important; }}
        .nabz-bottom-bar {{
            position: fixed; bottom: 0; left: 0; right: 0; height: 58px;
            background: #12121A; border-top: 2px solid #00F2FE;
            display: flex; flex-direction: row; justify-content: space-around; align-items: center;
            z-index: 999999; box-shadow: 0 -4px 15px rgba(0,0,0,0.9);
        }}
        .nabz-bottom-bar a {{
            text-decoration: none; font-size: 22px; padding: 6px 12px;
            border-radius: 12px; background: #1B1B26; border: 1px solid #2D2D44;
        }}
    </style>
    <div class="nabz-bottom-bar">
        <a href="?u={u_now}&p=feed" target="_self">🏠</a>
        <a href="?u={u_now}&p=reels" target="_self">🎞️</a>
        <a href="?u={u_now}&p=create" target="_self">➕</a>
        <a href="?u={u_now}&p=chat" target="_self">💬</a>
        <a href="?u={u_now}&p=profile" target="_self">👤</a>
    </div>
    """, unsafe_allow_html=True)

unread_count = 0
if st.session_state["username"]:
    try:
        n_res = requests.get(f"{API_URL}/notifications/{st.session_state['username']}")
        if n_res.status_code == 200:
            notifs = n_res.json().get("notifications", [])
            unread_count = sum(1 for n in notifs if not n.get("is_read"))
    except:
        pass

notif_label = f"{T['notifs']} ({unread_count})" if unread_count > 0 else T["notifs"]
if st.session_state["username"]:
    try:
        requests.post(f"{API_URL}/users/ping/{st.session_state['username']}")
    except:
        pass

menu = [T["login"], T["feed"], "🎯 Для вас", "🎞️ Reels", "🔥 Explore", "🔍 Поиск людей", T["subs"], T["bookmarks"], T["create"], T["drafts"], T["profile"], notif_label, T["chat"]]
p_param = st.query_params.get("p", "")
page_map = {"feed": T["feed"], "reels": "🎞️ Reels", "create": T["create"], "chat": T["chat"], "profile": T["profile"]}
if p_param in page_map and page_map[p_param] in menu:
    choice = st.sidebar.radio(T["nav"], menu, index=menu.index(page_map[p_param]))
else:
    choice = st.sidebar.radio(T["nav"], menu)

if st.session_state["username"]:
    st.sidebar.success(f"@{st.session_state['username']}")
    if st.sidebar.button(T["logout"]):
        st.session_state["username"] = None
        st.query_params.clear()
        st.rerun()
else:
    st.sidebar.warning("Guest Mode / Режим гостя")

def render_feed(mode="all", bookmarked_only=False, selected_cat="🌐 Все публикации"):
    search_query = st.text_input(T["search"], key=f"search_{mode}_{bookmarked_only}")
    
    params = {"limit": st.session_state["feed_limit"], "offset": 0, "feed_mode": mode}
    if st.session_state["username"]:
        params["viewer"] = st.session_state["username"]
    if search_query:
        params["search"] = search_query.strip()
    if bookmarked_only:
        params["bookmarked_by"] = st.session_state["username"]
        
    try:
        response = requests.get(f"{API_URL}/posts/list", params=params)
        if response.status_code == 200:
            posts = response.json().get("posts", [])
            if selected_cat != "🌐 Все публикации":
                posts = [p for p in posts if p.get("category") == selected_cat]
            if not posts:
                st.info("Публикаций пока нет / Ҳоло нашре нест.")
                return
                
            for post in posts:
                post_id = post.get("id")
                user_name = post.get("username", "Пользователь")
                created_at = post.get("created_at", "")
                updated_at = post.get("updated_at")
                avatar_url = post.get("author_avatar", "")
                
                if post.get("repost_author"):
                    st.markdown(f'<div class="repost-badge">🔁 Репост от <b>@{post.get("repost_author")}</b></div>', unsafe_allow_html=True)
                
                head_c1, head_c2 = st.columns([3, 1])
                with head_c1:
                    if avatar_url:
                        st.image(avatar_url, width=45)
                    st.markdown(f"### 👤 @{user_name}")
                with head_c2:
                    if st.session_state["username"] and st.session_state["username"] != user_name and mode != "drafts":
                        is_fol = post.get("is_following_author", False)
                        f_lbl = T["unfollow"] if is_fol else T["follow"]
                        if st.button(f_lbl, key=f"fol_{post_id}_{mode}_{bookmarked_only}"):
                            requests.post(f"{API_URL}/users/follow", json={"follower": st.session_state["username"], "following": user_name})
                            st.rerun()
                            
                time_label = f"📅 {created_at}" + (f" (ред. {updated_at})" if updated_at else "")
                st.caption(f"{time_label}  |  👁️ {post.get('views_count', 0)}")
                
                if st.session_state.get(f"edit_mode_{post_id}", False):
                    new_text = st.text_area("Редактировать текст:", value=post.get("text", ""), key=f"edit_txt_{post_id}")
                    c_save, c_cancel = st.columns(2)
                    with c_save:
                        if st.button("💾 Сохранить", key=f"save_edit_{post_id}"):
                            e_res = requests.put(f"{API_URL}/posts/edit/{post_id}", json={"text": new_text, "username": st.session_state["username"]})
                            if e_res.status_code == 200:
                                st.session_state[f"edit_mode_{post_id}"] = False
                                st.rerun()
                    with c_cancel:
                        if st.button("❌ Отмена", key=f"cancel_edit_{post_id}"):
                            st.session_state[f"edit_mode_{post_id}"] = False
                            st.rerun()
                else:
                    st.write(post.get("text"))
                
                media_urls_str = post.get("media_urls", "")
                if media_urls_str:
                    urls = media_urls_str.split(",")
                    for idx, url in enumerate(urls):
                        if url.lower().endswith(('.mp4', '.mov', '.avi', '.mkv')):
                            st.video(url)
                        else:
                            st.image(url, use_container_width=True)
                        st.link_button(f"💾 Скачать медиа №{idx+1}", url)
                
                if mode == "drafts":
                    dc1, dc2 = st.columns(2)
                    with dc1:
                        if st.button("🚀 Опубликовать сейчас", key=f"pub_dr_{post_id}"):
                            requests.post(f"{API_URL}/posts/publish_draft/{post_id}")
                            st.rerun()
                    with dc2:
                        if st.button("🗑️ Удалить черновик", key=f"del_dr_{post_id}"):
                            requests.delete(f"{API_URL}/posts/delete/{post_id}")
                            st.rerun()
                    st.markdown("---")
                    continue
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    if st.button(f"❤️ {post.get('likes_count', 0)}", key=f"like_{post_id}_{mode}_{bookmarked_only}"):
                        if not st.session_state["username"]:
                            st.warning("Войдите в аккаунт!")
                        else:
                            requests.post(f"{API_URL}/posts/like", json={"post_id": post_id, "username": st.session_state["username"]})
                            st.rerun()
                with col2:
                    if st.button(T["repost"], key=f"rep_{post_id}_{mode}_{bookmarked_only}"):
                        if not st.session_state["username"]:
                            st.warning("Войдите в аккаунт!")
                        else:
                            requests.post(f"{API_URL}/posts/repost", json={"post_id": post_id, "username": st.session_state["username"]})
                            st.toast("Репост опубликован в вашей ленте!")
                            st.rerun()
                with col3:
                    if st.button(T["bookmark"], key=f"bm_{post_id}_{mode}_{bookmarked_only}"):
                        if not st.session_state["username"]:
                            st.warning("Войдите в аккаунт!")
                        else:
                            bm_res = requests.post(f"{API_URL}/posts/bookmark", json={"post_id": post_id, "username": st.session_state["username"]})
                            if bm_res.status_code == 200:
                                st.toast("Избранное обновлено!")
                                if bookmarked_only:
                                    st.rerun()
                with col4:
                    if st.session_state["username"] == "admin1" or st.session_state["username"] == user_name:
                        if st.button("✏️ Изм.", key=f"btn_edit_{post_id}_{mode}_{bookmarked_only}"):
                            st.session_state[f"edit_mode_{post_id}"] = True
                            st.rerun()
                        if st.button("🗑️ Удал.", key=f"del_{post_id}_{mode}_{bookmarked_only}"):
                            requests.delete(f"{API_URL}/posts/delete/{post_id}")
                            st.rerun()
                    else:
                        if st.button("⚙️ Ещё", key=f"more_act_{post_id}_{mode}_{bookmarked_only}"):
                            st.session_state[f"show_act_{post_id}"] = not st.session_state.get(f"show_act_{post_id}", False)
                if st.session_state.get(f"show_act_{post_id}", False) and st.session_state["username"]:
                    ac1, ac2 = st.columns(2)
                    with ac1:
                        if st.button(T["report"], key=f"s_rep_{post_id}_{mode}"):
                            requests.post(f"{API_URL}/reports/create", json={"reporter": st.session_state["username"], "post_id": post_id, "target_username": user_name, "reason": "Нарушение правил NABZ"})
                            st.success("Жалоба отправлена администратору!")
                    with ac2:
                        if st.button(T["block"], key=f"s_blk_{post_id}_{mode}"):
                            requests.post(f"{API_URL}/users/block", json={"blocker": st.session_state["username"], "blocked": user_name})
                            st.rerun()
                
                comments = post.get("comments", [])
                with st.expander(f"💬 Комментарии ({len(comments)})"):
                    if st.session_state["username"]:
                        new_c = st.text_input("Написать комментарий...", key=f"new_c_{post_id}_{mode}_{bookmarked_only}")
                        if st.button("Отправить", key=f"send_c_{post_id}_{mode}_{bookmarked_only}"):
                            if new_c.strip():
                                add_c = requests.post(f"{API_URL}/posts/comment", json={"post_id": post_id, "username": st.session_state["username"], "text": new_c.strip()})
                                if add_c.status_code == 200:
                                    st.rerun()
                                elif add_c.status_code == 429:
                                    st.error(add_c.json().get("detail"))
                    top_comments = [c for c in comments if not c.get("parent_id")]
                    replies = [c for c in comments if c.get("parent_id")]
                    for c in top_comments:
                        cid = c["id"]
                        st.markdown(f'<div class="comment-box"><b>@{c["username"]}</b> <small>({c["created_at"]})</small><br>{c["text"]}</div>', unsafe_allow_html=True)
                        if st.session_state["username"]:
                            rc1, rc2, rc3 = st.columns(3)
                            with rc1:
                                if st.button("↩️ Ответить", key=f"rep_btn_{cid}_{mode}_{bookmarked_only}"):
                                    st.session_state[f"reply_to_{cid}"] = not st.session_state.get(f"reply_to_{cid}", False)
                            if st.session_state["username"] == c["username"] or st.session_state["username"] == "admin1":
                                with rc2:
                                    if st.button("✏️", key=f"ed_c_btn_{cid}_{mode}_{bookmarked_only}"):
                                        st.session_state[f"edit_c_{cid}"] = not st.session_state.get(f"edit_c_{cid}", False)
                                with rc3:
                                    if st.button("🗑️", key=f"del_c_btn_{cid}_{mode}_{bookmarked_only}"):
                                        requests.delete(f"{API_URL}/comments/delete/{cid}")
                                        st.rerun()
                            if st.session_state.get(f"edit_c_{cid}", False):
                                ed_txt = st.text_input("Исправить:", value=c["text"], key=f"ed_c_inp_{cid}_{mode}_{bookmarked_only}")
                                if st.button("Сохранить", key=f"ed_c_save_{cid}_{mode}_{bookmarked_only}"):
                                    requests.put(f"{API_URL}/comments/edit/{cid}", json={"text": ed_txt, "username": st.session_state["username"]})
                                    st.session_state[f"edit_c_{cid}"] = False
                                    st.rerun()
                            if st.session_state.get(f"reply_to_{cid}", False):
                                rep_txt = st.text_input(f"Ответ для @{c['username']}:", key=f"rep_inp_{cid}_{mode}_{bookmarked_only}")
                                if st.button("Отправить ответ", key=f"rep_send_{cid}_{mode}_{bookmarked_only}"):
                                    if rep_txt.strip():
                                        requests.post(f"{API_URL}/posts/comment", json={"post_id": post_id, "username": st.session_state["username"], "text": rep_txt.strip(), "parent_id": cid})
                                        st.session_state[f"reply_to_{cid}"] = False
                                        st.rerun()
                        for r in [x for x in replies if x.get("parent_id") == cid]:
                            rid = r["id"]
                            st.markdown(f'<div class="reply-box">↳ <b>@{r["username"]}</b> <small>({r["created_at"]})</small><br>{r["text"]}</div>', unsafe_allow_html=True)
                            if st.session_state["username"] == r["username"] or st.session_state["username"] == "admin1":
                                if st.button("🗑️ Удалить ответ", key=f"del_r_{rid}_{mode}_{bookmarked_only}"):
                                    requests.delete(f"{API_URL}/comments/delete/{rid}")
                                    st.rerun()
                st.markdown("---")
                
            if len(posts) >= st.session_state["feed_limit"]:
                if st.button("⬇️ Загрузить ещё посты", key=f"more_{mode}_{bookmarked_only}"):
                    st.session_state["feed_limit"] += 10
                    st.rerun()
        else:
            st.error("Ошибка загрузки ленты с сервера.")
    except Exception as e:
        st.error(f"Ошибка подключения: {e}")

if choice == T["login"]:
    st.subheader("Авторизация / Воридшавӣ / Auth")
    tab1, tab2, tab3 = st.tabs(["Вход по паролю", "Регистрация", "Сброс пароля"])
    
    with tab1:
        l_user = st.text_input("Ваш @username (например: admin1)")
        l_pass = st.text_input("Пароль (по умолчанию для старых: 12345)", type="password")
        if st.button("Войти"):
            if l_user:
                res = requests.post(f"{API_URL}/auth/login", json={"username": l_user, "password": l_pass or "12345"})
                if res.status_code == 200 and res.text.strip():
                    prof = res.json()["profile"]
                    st.session_state["username"] = prof["username"]
                    st.query_params["u"] = prof["username"]
                    st.query_params["u"] = prof["username"]
                    if prof.get("language") in ["ru", "tj", "en"]:
                        st.session_state["lang"] = prof["language"]
                    st.rerun()
                else:
                    try:
                        err_msg = res.json().get("detail", "Ошибка входа")
                    except Exception:
                        err_msg = f"Сервер не отвечает (код {res.status_code}). Проверьте API_URL."
                    st.error(err_msg)
                    
    with tab2:
        st.caption("⚡ Быстрая регистрация: обязательно указать только ник и пароль")
        r_user = st.text_input("Придумайте @username (например: farzona)")
        r_pass = st.text_input("Придумайте пароль (минимум 4 символа)", type="password")
        r_fname = st.text_input("Ваше имя (необязательно)")
        r_email = st.text_input("Email для восстановления пароля (необязательно)")
        if st.button("🚀 Создать аккаунт"):
            clean_u = r_user.strip().lstrip("@")
            if len(clean_u) < 2 or len(r_pass) < 3:
                st.error("Придумайте ник (от 2 букв) и пароль (от 3 символов)!")
            else:
                final_email = r_email.strip() if ("@" in r_email) else f"{clean_u}@nabz.app"
                payload = {
                    "email": final_email, "username": clean_u, "password": r_pass,
                    "first_name": r_fname.strip() or clean_u, "last_name": "", "language": st.session_state["lang"]
                }
                res = requests.post(f"{API_URL}/auth/register", json=payload)
                if res.status_code == 200:
                    st.session_state["username"] = res.json()["username"]
                    st.query_params["u"] = res.json()["username"]
                    st.query_params["u"] = res.json()["username"]
                    st.success("Добро пожаловать в NABZ!")
                    st.rerun()
                else:
                    try:
                        st.error(res.json().get("detail", "Этот ник уже занят, попробуйте другой"))
                    except Exception:
                        st.error("Ошибка регистрации, попробуйте другой ник")
                    
    with tab3:
        rs_user = st.text_input("Ваш @username для сброса")
        rs_email = st.text_input("Привязанный Email")
        rs_new = st.text_input("Новый пароль", type="password")
        if st.button("Обновить пароль"):
            res = requests.post(f"{API_URL}/auth/reset_password", json={"username": rs_user, "email": rs_email, "new_password": rs_new})
            if res.status_code == 200:
                st.success("Пароль обновлён! Войдите во вкладке Вход.")
            else:
                st.error(res.json().get("detail", "Ошибка сброса"))

elif choice == T["feed"]:
    st.subheader(T["feed"])
    cat_filter = st.selectbox("📂 Раздел / Рубрика:", ["🌐 Все публикации", "📢 Реклама и объявления", "💡 Лайфхаки", "🤝 Обмен опытом", "🔬 Наука и технологии", "🎨 Творчество и развлечения"])
    render_feed(mode="all", selected_cat=cat_filter)

elif choice == "🎯 Для вас":
    st.subheader("🎯 Для вас — Персональная лента")
    render_feed(mode="for_you")

elif choice == "🔍 Поиск людей":
    st.subheader("🔍 Поиск людей в NABZ")
    q_user = st.text_input("Введите @username или имя человека:")
    try:
        ex_u = requests.get(f"{API_URL}/explore/data", params={"viewer": st.session_state["username"]})
        if ex_u.status_code == 200:
            users_list = ex_u.json().get("recommended_users", [])
            if q_user.strip():
                users_list = [u for u in users_list if q_user.lower() in u.get("username", "").lower() or q_user.lower() in u.get("first_name", "").lower()]
            if not users_list:
                st.info("Пользователи не найдены. Попробуйте другой запрос.")
            for u in users_list:
                uc1, uc2 = st.columns([3, 1])
                with uc1:
                    st.markdown(f"### 👤 @{u['username']}")
                    st.caption("🟢 Онлайн" if u.get("is_online") else "⚪ Был(а) недавно")
                with uc2:
                    if st.session_state["username"] and st.session_state["username"] != u["username"]:
                        if st.button("➕ Подписаться", key=f"srch_f_{u['username']}"):
                            requests.post(f"{API_URL}/users/follow", json={"follower": st.session_state["username"], "following": u["username"]})
                            st.toast(f"Вы подписались на @{u['username']}!")
                st.markdown("---")
    except Exception as e:
        st.error(f"Ошибка поиска: {e}")

elif choice == T["subs"]:
    st.subheader(T["subs"])
    if not st.session_state["username"]:
        st.warning("Войдите в аккаунт!")
    else:
        render_feed(mode="following")

elif choice == T["bookmarks"]:
    st.subheader(T["bookmarks"])
    if not st.session_state["username"]:
        st.warning("Войдите в аккаунт!")
    else:
        render_feed(mode="all", bookmarked_only=True)

elif choice == T["create"]:
    st.subheader(T["create"])
    if not st.session_state["username"]:
        st.warning("Войдите в аккаунт!")
    else:
        text = st.text_area("Текст поста (#хэштеги, @упоминания)...")
        files = st.file_uploader("Фото или видео", type=["jpg", "png", "mp4", "mov", "avi", "mkv"], accept_multiple_files=True)
        post_cat = st.selectbox("Выберите рубрику:", ["📢 Реклама и объявления", "💡 Лайфхаки", "🤝 Обмен опытом", "🔬 Наука и технологии", "🎨 Творчество и развлечения"])
        post_subs = st.text_input("Субтитры или описание к видео (необязательно):")
        c_pub, c_dr = st.columns(2)
        with c_pub:
            if st.button("🚀 Опубликовать"):
                f_pay = [("files", (f"media_{idx}.{f.name.split('.')[-1]}", f.getvalue(), f.type)) for idx, f in enumerate(files)] if files else []
                res = requests.post(f"{API_URL}/posts/create_with_media", data={"text": text, "username": st.session_state["username"], "is_draft": False}, files=f_pay)
                if res.status_code == 200:
                    latest_p = requests.get(f"{API_URL}/posts/list", params={"limit": 1, "feed_mode": "all"}).json().get("posts", [])
                    if latest_p:
                        requests.post(f"{API_URL}/posts/update_meta/{latest_p[0]['id']}", data={"category": post_cat, "subtitles": post_subs})
                    st.success("Опубликовано!")
                else:
                    st.error(res.json().get("detail", "Ошибка публикации"))
        with c_dr:
            if st.button("📝 В черновики"):
                f_pay = [("files", (f"media_{idx}.{f.name.split('.')[-1]}", f.getvalue(), f.type)) for idx, f in enumerate(files)] if files else []
                res = requests.post(f"{API_URL}/posts/create_with_media", data={"text": text, "username": st.session_state["username"], "is_draft": True}, files=f_pay)
                if res.status_code == 200:
                    latest_p = requests.get(f"{API_URL}/posts/list", params={"limit": 1, "feed_mode": "drafts", "viewer": st.session_state["username"]}).json().get("posts", [])
                    if latest_p:
                        requests.post(f"{API_URL}/posts/update_meta/{latest_p[0]['id']}", data={"category": post_cat, "subtitles": post_subs})
                    st.info("Сохранено в черновики!")
                else:
                    st.error(res.json().get("detail", "Ошибка сохранения"))

elif choice == T["drafts"]:
    st.subheader(T["drafts"])
    if not st.session_state["username"]:
        st.warning("Войдите в аккаунт!")
    else:
        render_feed(mode="drafts")

elif choice == T["profile"]:
    st.subheader(T["profile"])
    if not st.session_state["username"]:
        st.warning("Войдите в аккаунт!")
    else:
        uname = st.session_state["username"]
        p_res = requests.get(f"{API_URL}/profile/{uname}")
        if p_res.status_code == 200 and p_res.json().get("status") == "success":
            prof = p_res.json()["profile"]
            if prof.get("cover_url"):
                st.image(prof["cover_url"], use_container_width=True)
            pc1, pc2 = st.columns([1, 3])
            with pc1:
                if prof.get("avatar_url"):
                    st.image(prof["avatar_url"], width=90)
                else:
                    st.markdown("## 👤")
            with pc2:
                st.markdown(f"### {prof.get('first_name', '')} {prof.get('last_name', '')} (@{uname})")
                st.write(prof.get("bio", ""))
                st.caption(f"Подписчики: **{prof.get('followers_count', 0)}**  |  Подписки: **{prof.get('following_count', 0)}**")
                
            with st.expander("⚙️ Настройки профиля, фото и приватность"):
                av_file = st.file_uploader("Загрузить новый Аватар", type=["jpg", "png"], key="up_av")
                if av_file and st.button("Сохранить Аватар"):
                    requests.post(f"{API_URL}/profile/{uname}/media", data={"media_type": "avatar"}, files={"file": (av_file.name, av_file.getvalue(), av_file.type)})
                    st.rerun()
                cv_file = st.file_uploader("Загрузить Обложку профиля", type=["jpg", "png"], key="up_cv")
                if cv_file and st.button("Сохранить Обложку"):
                    requests.post(f"{API_URL}/profile/{uname}/media", data={"media_type": "cover"}, files={"file": (cv_file.name, cv_file.getvalue(), cv_file.type)})
                    st.rerun()
                st.markdown("---")
                fn = st.text_input("Имя", value=prof.get("first_name", ""))
                ln = st.text_input("Фамилия", value=prof.get("last_name", ""))
                mood_presets = ["Свой текст (из поля ниже)", "😊 В отличном настроении", "💼 Занят / На работе", "🚀 Развиваю NABZ", "☕ Отдыхаю", "✈️ В дороге", "📚 Учусь"]
                quick_mood = st.selectbox("✨ Быстрое настроение (видно в чате):", mood_presets, key="quick_mood_sel")
                bio = st.text_area("О себе / Своё настроение", value=prof.get("bio", ""))
                if quick_mood != "Свой текст (из поля ниже)":
                    bio = quick_mood
                priv = st.checkbox("🔒 Закрытый (приватный) аккаунт — посты видят только подписчики", value=prof.get("is_private", False))
                if st.button("💾 Сохранить настройки"):
                    requests.put(f"{API_URL}/profile/{uname}", json={"first_name": fn, "last_name": ln, "bio": bio, "language": st.session_state["lang"], "is_private": priv})
                    st.success("Профиль обновлён!")
                    st.rerun()
                    
            with st.expander("🚫 Чёрный список (заблокированные пользователи)"):
                b_res = requests.get(f"{API_URL}/users/blocked/{uname}")
                b_list = b_res.json().get("blocked", []) if b_res.status_code == 200 else []
                if not b_list:
                    st.info("Чёрный список пуст.")
                for bu in b_list:
                    bc1, bc2 = st.columns([3, 1])
                    bc1.write(f"🚫 @{bu}")
                    if bc2.button("Разблокировать", key=f"unblk_{bu}"):
                        requests.post(f"{API_URL}/users/block", json={"blocker": uname, "blocked": bu})
                        st.rerun()
                        
            if uname == "admin1":
                with st.expander("🛡️ Панель модератора: Жалобы пользователей"):
                    rep_res = requests.get(f"{API_URL}/reports/list")
                    reps = rep_res.json().get("reports", []) if rep_res.status_code == 200 else []
                    if not reps:
                        st.info("Новых жалоб нет.")
                    for r in reps:
                        st.warning(f"Жалоба #{r['id']} от @{r['reporter_username']} на @{r['target_username']} (Пост #{r['target_post_id']}): {r['reason']} — {r['created_at']}")

elif choice.startswith(T["notifs"]):
    if st.session_state["username"]:
        try: requests.post(f"{API_URL}/notifications/read_all/{st.session_state['username']}")
        except: pass
    st.subheader(T["notifs"])
    if not st.session_state["username"]:
        st.warning("Войдите в аккаунт!")
    else:
        if st.button("✅ Отметить все прочитанными"):
            requests.post(f"{API_URL}/notifications/read_all/{st.session_state['username']}")
            st.rerun()
        n_res = requests.get(f"{API_URL}/notifications/{st.session_state['username']}")
        if n_res.status_code == 200:
            notifs = n_res.json().get("notifications", [])
            if not notifs:
                st.info("Уведомлений пока нет.")
            for n in notifs:
                icon = "🔵" if not n.get("is_read") else "⚪"
                st.markdown(f"{icon} **{n['message']}** — *{n['created_at']}*")

elif choice == T["chat"]:
    st.subheader("💬 Мессенджер NABZ (Direct и Группы)")
    if not st.session_state["username"]:
        st.warning("Войдите в аккаунт, чтобы пользоваться чатом!")
    else:
        me = st.session_state["username"]
        with st.expander("➕ Начать новый диалог или создать группу"):
            c_type = st.radio("Тип чата:", ["Личный чат (Direct)", "Групповой чат"], horizontal=True)
            if c_type == "Личный чат (Direct)":
                target_u = st.text_input("Введите @username собеседника:")
                if st.button("Открыть диалог"):
                    if target_u.strip():
                        res = requests.post(f"{API_URL}/chats/create", json={"creator": me, "members": [target_u.strip()], "is_group": False})
                        if res.status_code == 200:
                            st.session_state["active_room"] = res.json()["room"]
                            st.rerun()
            else:
                g_name = st.text_input("Название группы:")
                g_users = st.text_input("Участники через запятую (например: user1, user2):")
                if st.button("Создать группу"):
                    u_list = [x.strip() for x in g_users.split(",") if x.strip()]
                    res = requests.post(f"{API_URL}/chats/create", json={"creator": me, "members": u_list, "name": g_name, "is_group": True})
                    if res.status_code == 200:
                        st.session_state["active_room"] = res.json()["room"]
                        st.rerun()
                        
        r_res = requests.get(f"{API_URL}/chats/user/{me}")
        rooms = r_res.json().get("rooms", []) if r_res.status_code == 200 else []
        
        if not rooms:
            st.info("У вас пока нет активных чатов. Создайте первый диалог выше!")
        else:
            room_options = {}
            for r in rooms:
                if r.get("is_group"):
                    label = f"👥 {r.get('name') or 'Группа'} ({r['members']})"
                else:
                    others = [m for m in r["members"].split(",") if m != me]
                    partner = others[0] if others else me
                    label = f"👤 @{partner}"
                room_options[label] = r
                
            selected_label = st.selectbox("Выберите чат:", list(room_options.keys()))
            active_room = room_options[selected_label]
            rid = active_room["id"]
            
            # ЗАКРЕПЛЁННАЯ ШАПКА СОБЕСЕДНИКА (НЕ ПРОКРУЧИВАЕТСЯ)
            if not active_room.get("is_group"):
                others = [x for x in active_room["members"].split(",") if x != me]
                partner_name = others[0] if others else me
                p_avatar = "https://flaticon.com"
                p_mood = "😊 На связи в NABZ"
                try:
                    p_info = requests.get(f"{API_URL}/profile/{partner_name}", timeout=3)
                    if p_info.status_code == 200 and p_info.json().get("status") == "success":
                        pdata = p_info.json()["profile"]
                        if pdata.get("avatar_url"):
                            p_avatar = pdata["avatar_url"]
                        if pdata.get("bio"):
                            p_mood = pdata["bio"][:55]
                except Exception:
                    pass
                st.markdown(f"""
                <div class="chat-header-card">
                    <img src="{p_avatar}" style="width:46px; height:46px; border-radius:50%; object-fit:cover; border:2px solid #00F2FE;">
                    <div>
                        <div style="font-weight:bold; font-size:16px; color:#FFFFFF;">@{partner_name}</div>
                        <div style="font-size:12px; color:#00F2FE;">✨ {p_mood}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            # КНОПКИ ЗВОНКОВ ЗАКРЕПЛЕНЫ СВЕРХУ
            call_c1, call_c2, call_c3 = st.columns([2, 2, 1])
            with call_c1:
                st.link_button("📞 Аудиозвонок", f"https://jit.si_{rid}#config.startWithVideoMuted=true")
            with call_c2:
                st.link_button("📹 Видеозвонок", f"https://jit.si_{rid}")
            with call_c3:
                if st.button("🔄", key=f"ref_top_{rid}"):
                    st.rerun()

            # ОКНО ПЕРЕПИСКИ С СОБСТВЕННОЙ ПРОКРУТКОЙ
            m_res = requests.get(f"{API_URL}/chats/{rid}/messages", params={"viewer": me})
            msgs = m_res.json().get("messages", []) if m_res.status_code == 200 else []
            chat_box = st.container(height=360)
            with chat_box:
                if not msgs:
                    st.caption("Сообщений пока нет. Напишите первым!")
                group_palette = ["#2A1B3D", "#1B3B36", "#3D2B1F", "#1F2A44", "#3B1E32", "#263829"]
                for m in msgs:
                    sender = m["sender_username"]
                    is_me = (sender == me)
                    read_mark = " ✓✓" if (is_me and m.get("is_read")) else (" ✓" if is_me else "")
                    msg_text = m.get("text", "")
                    if is_me:
                        st.markdown(f"""
                        <div class="chat-row-me">
                            <div class="bubble-me">
                                <div style="font-size:11px; color:#00F2FE; margin-bottom:2px;"><b>Вы</b> • {m["created_at"]}{read_mark}</div>
                                <div style="font-size:15px;">{msg_text}</div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        g_color = group_palette[sum(ord(ch) for ch in sender) % len(group_palette)]
                        st.markdown(f"""
                        <div class="chat-row-other">
                            <div class="bubble-other" style="background:{g_color}; border-color:#5A5A7A;">
                                <div style="font-size:11px; color:#FFD166; margin-bottom:2px;"><b>@{sender}</b> • {m["created_at"]}</div>
                                <div style="font-size:15px;">{msg_text}</div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

                    if msg_text:
                        with st.popover("🌐"):
                            langs_menu = {"🇹🇯 Тоҷикӣ": "tg", "🇷🇺 Русский": "ru", "🇺🇸 English": "en", "🇹🇷 Türkçe": "tr", "🇺🇿 Oʻzbek": "uz", "🇮🇷 فارسی": "fa", "🇦🇪 العربية": "ar", "🇨🇳 中文": "zh-CN"}
                            chosen_l = st.selectbox("Перевести на:", list(langs_menu.keys()), key=f"psel_{m['id']}")
                            if st.button("✅ Перевести", key=f"pgo_{m['id']}"):
                                st.session_state[f"tr_out_{m['id']}"] = ai_translate_text(msg_text, langs_menu[chosen_l])
                        if st.session_state.get(f"tr_out_{m['id']}"):
                            st.caption(f"🌐 {st.session_state[f'tr_out_{m['id']}']}")

                    if m.get("media_url"):
                        mtype = m.get("media_type")
                        if mtype == "image":
                            st.image(m["media_url"], width=240)
                        elif mtype == "video":
                            st.video(m["media_url"])
                        elif mtype == "audio":
                            st.audio(m["media_url"])
                        else:
                            st.link_button("📎 Скачать файл", m["media_url"])

            if st.session_state.pop(f"clear_inp_{rid}", False):
                st.session_state[f"chat_inp_{rid}"] = ""
                st.session_state[f"v_key_{rid}"] = st.session_state.get(f"v_key_{rid}", 0) + 1

            if f"pending_txt_{rid}" in st.session_state:
                st.session_state[f"chat_inp_{rid}"] = st.session_state.pop(f"pending_txt_{rid}")
            msg_txt = st.text_input("Сообщение...", placeholder="Напишите сообщение...", label_visibility="collapsed", key=f"chat_inp_{rid}")

            b1, b2, b3, b4 = st.columns(4)
            voice_rec = None
            msg_file = None

            with b1:
                with st.popover("😊"):
                    all_emojis = [
                        "❤️","🔥","👍","😂","😍","🙏","🎉","🤝","😊","🥰",
                        "😎","🤩","🥳","😢","😭","😡","🤔","🫡","👏","💪",
                        "🌹","💐","🌸","✨","⭐","🌙","☀️","⚡","💎","👑",
                        "🇹🇯","🇷🇺","🇺🇸","🇺🇿","🇰🇿","🇰🇬","🇹🇷","🇦🇪","🌍","✈️"
                    ]
                    for row in range(0, len(all_emojis), 5):
                        ecols = st.columns(5)
                        for idx, em in enumerate(all_emojis[row:row+5]):
                            if ecols[idx].button(em, key=f"em_{rid}_{row}_{idx}"):
                                st.session_state[f"pending_txt_{rid}"] = st.session_state.get(f"chat_inp_{rid}", "") + em
                                st.rerun()

            with b2:
                with st.popover("🎙️"):
                    v_idx = st.session_state.get(f"v_key_{rid}", 0)
                    voice_rec = st.audio_input("Запись голоса", label_visibility="collapsed", key=f"voice_{rid}_{v_idx}")

            with b3:
                with st.popover("📎"):
                    msg_file = st.file_uploader("Медиа", type=["jpg", "jpeg", "png", "mp4", "mov", "mp3", "ogg", "wav"], label_visibility="collapsed", key=f"chat_file_{rid}")
                    st.checkbox("🎨 ИИ-улучшение фото", value=True, key=f"ai_ph_{rid}")

            with b4:
                with st.popover("✨ ИИ"):
                    ai_draft = st.text_input("Черновик:", placeholder="Например: чихели корот зурай", label_visibility="collapsed", key=f"ai_dr_{rid}")
                    ai_lang = st.selectbox("Язык:", ["Тоҷикӣ (TJ)", "Русский (RU)", "English (EN)", "Oʻzbek (UZ)", "فارسی (FA)", "العربية (AR)", "Türkçe (TR)", "中文 (ZH)"], label_visibility="collapsed", key=f"ai_lg_{rid}")
                    ai_style = st.selectbox("Стиль:", ["Вежливый", "Деловой", "Дружеский", "Только перевод"], label_visibility="collapsed", key=f"ai_st_{rid}")
                    if st.button("🪄 Вставить в чат", key=f"ai_btn_{rid}"):
                        raw = ai_draft.strip()
                        if raw:
                            l_code = "tg" if "TJ" in ai_lang else ("ru" if "RU" in ai_lang else ("en" if "EN" in ai_lang else ("uz" if "UZ" in ai_lang else ("fa" if "FA" in ai_lang else ("ar" if "AR" in ai_lang else ("tr" if "TR" in ai_lang else "zh-CN"))))))
                            if ai_style == "Только перевод":
                                res_txt = ai_translate_text(raw, l_code)
                            elif "TJ" in ai_lang:
                                base = ai_translate_text(raw, "tg")
                                res_txt = f"Ассалому алайкум! {base} Хеле шодам аз ҳамсуҳбатӣ бо шумо." if ai_style == "Вежливый" else (f"Салом. {base} Биёед тафсилотро муҳокима кунем." if ai_style == "Деловой" else f"Салом! 😊 {base} Аҳволат чӣ хел?")
                            elif "RU" in ai_lang:
                                base = ai_translate_text(raw, "ru")
                                res_txt = f"Здравствуйте! {base} Буду рад продолжить общение." if ai_style == "Вежливый" else (f"Добрый день. {base} Давайте обсудим детали." if ai_style == "Деловой" else f"Привет! 😊 {base} Как дела?")
                            else:
                                res_txt = ai_translate_text(raw, l_code)
                            st.session_state[f"pending_txt_{rid}"] = res_txt
                            st.rerun()

            auto_tr = st.selectbox("🌐 Перевод при отправке:", ["Без перевода (как написано)", "Перевести на English (EN)", "Перевести на Тоҷикӣ (TJ)", "Перевести на Русский (RU)", "Перевести на Türkçe (TR)", "Перевести на العربية (AR)", "Перевести на 中文 (ZH)"], label_visibility="collapsed", key=f"auto_tr_lang_{rid}")
            sc1, sc2 = st.columns([3, 1])
            with sc1:
                if st.button("📨 Отправить", key=f"send_msg_{rid}"):
                    if voice_rec is not None:
                        v_data = voice_rec.getvalue()
                        files_p = {"file": ("voice_msg.wav", v_data, "audio/wav")}
                        requests.post(f"{API_URL}/chats/{rid}/send", data={"sender": me, "text": msg_txt.strip() or "🎙️ Голосовое сообщение"}, files=files_p)
                        st.session_state[f"clear_inp_{rid}"] = True
                        st.rerun()
                    elif msg_txt.strip() or msg_file is not None:
                        files_p = None
                        if msg_file is not None:
                            f_bytes = msg_file.getvalue()
                            if st.session_state.get(f"ai_ph_{rid}", True) and msg_file.type.startswith("image/"):
                                try:
                                    from PIL import Image, ImageEnhance
                                    import io
                                    im = Image.open(io.BytesIO(f_bytes)).convert("RGB")
                                    im = ImageEnhance.Sharpness(im).enhance(1.35)
                                    im = ImageEnhance.Contrast(im).enhance(1.12)
                                    im = ImageEnhance.Color(im).enhance(1.15)
                                    buf = io.BytesIO()
                                    im.save(buf, format="JPEG", quality=92)
                                    f_bytes = buf.getvalue()
                                except Exception:
                                    pass
                            files_p = {"file": (msg_file.name, f_bytes, msg_file.type)}
                        requests.post(f"{API_URL}/chats/{rid}/send", data={"sender": me, "text": (ai_translate_text(msg_txt.strip(), "en" if "EN" in auto_tr else ("tg" if "TJ" in auto_tr else ("ru" if "RU" in auto_tr else ("tr" if "TR" in auto_tr else ("ar" if "AR" in auto_tr else "zh-CN"))))) if auto_tr != "Без перевода (как написано)" else msg_txt.strip())}, files=files_p)
                        st.session_state[f"clear_inp_{rid}"] = True
                        st.rerun()
            with sc2:
                if st.button("🔄 Обновить", key=f"ref_msg_{rid}"):
                    st.rerun()

elif choice == "🔥 Explore":
    st.subheader("🔥 Explore: Тренды и Рекомендации NABZ")
    try:
        ex_res = requests.get(f"{API_URL}/explore/data", params={"viewer": st.session_state["username"]})
        if ex_res.status_code == 200:
            data = ex_res.json()
            tags = data.get("trending_tags", [])
            users = data.get("recommended_users", [])
            pop_posts = data.get("popular_posts", [])
            
            if tags:
                st.markdown("#### 📈 Трендовые #хэштеги")
                tag_line = "  ".join([f"`{t}` ({cnt})" for t, cnt in tags])
                st.markdown(tag_line)
                
            if users:
                st.markdown("#### 🌟 Рекомендуемые авторы")
                u_cols = st.columns(min(len(users), 3))
                for idx, u in enumerate(users[:3]):
                    with u_cols[idx]:
                        status_dot = "🟢 Онлайн" if u.get("is_online") else "⚪ Офлайн"
                        if u.get("avatar_url"):
                            st.image(u["avatar_url"], width=60)
                        st.markdown(f"**@{u['username']}**")
                        st.caption(status_dot)
                        if st.session_state["username"]:
                            if st.button("➕ Подписаться", key=f"ex_fol_{u['username']}"):
                                requests.post(f"{API_URL}/users/follow", json={"follower": st.session_state["username"], "following": u["username"]})
                                st.toast(f"Вы подписались на @{u['username']}!")
                                
            st.markdown("---")
            st.markdown("#### 🏆 Популярные публикации")
            for p in pop_posts:
                st.markdown(f"**👤 @{p['username']}** — ❤️ {p.get('likes_count', 0)} | 👁️ {p.get('views_count', 0)}")
                st.write(p.get("text", ""))
                if p.get("media_urls"):
                    first_url = p["media_urls"].split(",")[0]
                    if first_url.lower().endswith((".mp4", ".mov", ".avi", ".mkv")):
                        st.video(first_url)
                    else:
                        st.image(first_url, use_container_width=True)
                st.markdown("---")
    except Exception as e:
        st.error(f"Ошибка загрузки Explore: {e}")

elif choice == "🎞️ Reels":
    st.subheader("⭕ Stories (исчезают через 24 часа)")
    with st.expander("➕ Опубликовать новую Story на 24 часа"):
        if not st.session_state["username"]:
            st.warning("Войдите в аккаунт, чтобы добавлять Stories!")
        else:
            st_cap = st.text_input("Подпись к Story (необязательно):", key="st_cap_inp")
            st_file = st.file_uploader("Фото или короткое видео для Story", type=["jpg", "png", "mp4", "mov"], key="st_file_up")
            if st.button("🚀 Выложить Story на 24ч"):
                if st_file:
                    res = requests.post(
                        f"{API_URL}/stories/create",
                        data={"username": st.session_state["username"], "caption": st_cap},
                        files={"file": (st_file.name, st_file.getvalue(), st_file.type)}
                    )
                    if res.status_code == 200:
                        st.success("Story опубликована на 24 часа!")
                        st.rerun()
                else:
                    st.warning("Выберите фото или видео файл!")
                    
    try:
        s_res = requests.get(f"{API_URL}/stories/active")
        if s_res.status_code == 200:
            stories = s_res.json().get("stories", [])
            if not stories:
                st.info("Активных Stories за последние 24 часа пока нет.")
            else:
                s_cols = st.columns(min(len(stories), 4))
                for idx, st_item in enumerate(stories[:4]):
                    with s_cols[idx]:
                        st.caption(f"👤 @{st_item['username']}")
                        if st_item.get("media_type") == "video":
                            st.video(st_item["media_url"])
                        else:
                            st.image(st_item["media_url"], use_container_width=True)
                        if st_item.get("caption"):
                            st.write(st_item["caption"])
                        st.caption(f"👁️ {st_item.get('views_count', 0)} | 🕒 {st_item['created_at']}")
                        if st.button("👁️ Смотреть", key=f"vw_st_{st_item['id']}"):
                            requests.post(f"{API_URL}/stories/view/{st_item['id']}")
                            st.rerun()
                        if st.session_state["username"] in [st_item["username"], "admin1"]:
                            if st.button("🗑️", key=f"del_st_{st_item['id']}"):
                                requests.delete(f"{API_URL}/stories/delete/{st_item['id']}")
                                st.rerun()
    except:
        st.error("Ошибка загрузки Stories")
        
    st.markdown("---")
    st.subheader("🎞️ Лента Reels и Видео NABZ")
    
    with st.expander("🎬 Загрузить новый Reel / Видео с обложкой"):
        if not st.session_state["username"]:
            st.warning("Войдите в аккаунт!")
        else:
            r_text = st.text_area("Описание видео (#хэштеги)...", key="reel_txt")
            r_vid = st.file_uploader("Выберите видеофайл (.mp4, .mov)", type=["mp4", "mov", "avi", "mkv"], key="reel_vid")
            r_cov = st.file_uploader("Выберите обложку / превью (необязательно)", type=["jpg", "png"], key="reel_cov")
            if st.button("🔥 Опубликовать Reel"):
                if r_vid:
                    files_data = {"video_file": (f"reel.{r_vid.name.split('.')[-1]}", r_vid.getvalue(), r_vid.type)}
                    if r_cov:
                        files_data["cover_file"] = (f"cover.{r_cov.name.split('.')[-1]}", r_cov.getvalue(), r_cov.type)
                    res = requests.post(
                        f"{API_URL}/posts/create_reel",
                        data={"text": r_text, "username": st.session_state["username"], "is_reel": True},
                        files=files_data
                    )
                    if res.status_code == 200:
                        st.success("Reel успешно опубликован!")
                        st.rerun()
                else:
                    st.warning("Пожалуйста, выберите видеофайл!")
                    
    try:
        p_res = requests.get(f"{API_URL}/posts/list", params={"limit": 20, "viewer": st.session_state["username"]})
        if p_res.status_code == 200:
            all_p = p_res.json().get("posts", [])
            reels = [p for p in all_p if p.get("is_reel") or (p.get("media_urls") and any(p["media_urls"].lower().endswith(ext) for ext in [".mp4", ".mov", ".avi", ".mkv"]))]
            if not reels:
                st.info("Видеороликов пока нет. Загрузите первый Reel выше!")
            for r in reels:
                st.markdown(f"### 🎬 @{r['username']}")
                st.caption(f"📅 {r['created_at']}  |  👁️ {r.get('views_count', 0)} просмотров")
                if r.get("cover_url"):
                    with st.expander("🖼️ Посмотреть обложку видео"):
                        st.image(r["cover_url"], use_container_width=True)
                st.write(r.get("text", ""))
                if r.get("media_urls"):
                    st.video(r["media_urls"].split(",")[0])
                rc1, rc2 = st.columns(2)
                with rc1:
                    if st.button(f"❤️ {r.get('likes_count', 0)}", key=f"reel_like_fixed_{r['id']}"):
                        if st.session_state["username"]:
                            requests.post(f"{API_URL}/posts/like", json={"post_id": r["id"], "username": st.session_state["username"]})
                            st.rerun()
                with rc2:
                    if st.session_state["username"] in [r["username"], "admin1"]:
                        if st.button("🗑️ Удалить видео", key=f"rl_del_{r['id']}"):
                            requests.delete(f"{API_URL}/posts/delete/{r['id']}")
                            st.rerun()
                st.markdown("---")
    except Exception as e:
        st.error(f"Ошибка загрузки Reels: {e}")

with st.sidebar.expander("📜 Правила и Конфиденциальность"):
    st.markdown("""
    **1. Пользовательское соглашение NABZ**
    Платформа NABZ создана для научно-познавательного, творческого, развлекательного контента и дружелюбного общения. Регистрируясь на платформе, пользователь соглашается соблюдать нормы уважительного общения.
    
    **2. Правила публикации и модерации**
    На платформе строго запрещены: политическая агитация, экстремизм, порнография и материалы 18+, нецензурная лексика, пропаганда азартных игр и нарушение авторских прав. Нарушающий контент удаляется, а аккаунт нарушителя блокируется.
    
    **3. Политика конфиденциальности и защита данных**
    Мы храним только данные, необходимые для работы аккаунта (email, никнейм, настройки профиля). Пароли хранятся в зашифрованном виде (SHA-256). Доступ к базе данных защищён политиками безопасности RLS. Пользователь вправе в любой момент удалить свои публикации или запросить полное удаление аккаунта через службу поддержки.
    
    **4. Поддержка и обратная связь**
    По вопросам работы платформы, авторских прав и удаления данных обращайтесь к администратору **`@admin1`** через личные сообщения NABZ.
    """)

   
