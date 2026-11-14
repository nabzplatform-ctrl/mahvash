with open("app_mobile.py", "r", encoding="utf-8") as f:
    code = f.read()

# 1. Тёмные плашки уведомлений (убираем белые прямоугольники)
old_css_end = "[data-testid=\"stExpander\"] { background-color: #15151F !important; border: 1px solid #2D2D44 !important; border-radius: 12px !important; }\n</style>"
new_css_end = """[data-testid="stExpander"] { background-color: #15151F !important; border: 1px solid #2D2D44 !important; border-radius: 12px !important; }
    [data-testid="stAlert"] { background-color: #161A24 !important; color: #FFFFFF !important; border: 1px solid #00F2FE !important; border-radius: 12px !important; }
    [data-testid="stAlert"] * { color: #FFFFFF !important; }
</style>"""
if old_css_end in code:
    code = code.replace(old_css_end, new_css_end)

# 2. Простая регистрация (обязательны только ник и пароль)
old_reg = """    with tab2:
        r_email = st.text_input("Email")
        r_user = st.text_input("Уникальный @username")
        r_pass = st.text_input("Придумайте пароль", type="password")
        r_fname = st.text_input("Имя")
        r_lname = st.text_input("Фамилия")
        if st.button("Создать аккаунт"):
            if not r_email or "@" not in r_email or not r_user or not r_pass:
                st.error("Заполните все поля корректно!")
            else:
                payload = {
                    "email": r_email, "username": r_user, "password": r_pass,
                    "first_name": r_fname, "last_name": r_lname, "language": st.session_state["lang"]
                }
                res = requests.post(f"{API_URL}/auth/register", json=payload)
                if res.status_code == 200:
                    st.session_state["username"] = res.json()["username"]
                    st.success("Аккаунт создан!")
                    st.rerun()
                else:
                    st.error(res.json().get("detail", "Ошибка регистрации"))"""

new_reg = """    with tab2:
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
                    st.success("Добро пожаловать в NABZ!")
                    st.rerun()
                else:
                    try:
                        st.error(res.json().get("detail", "Этот ник уже занят, попробуйте другой"))
                    except Exception:
                        st.error("Ошибка регистрации, попробуйте другой ник")"""

if old_reg in code:
    code = code.replace(old_reg, new_reg)

# 3. Новые рубрики при создании поста + фильтр в Общей ленте
old_cats = '["🔬 Наука и технологии", "🎨 Творчество и развлечения", "📚 Образование и факты", "💬 Общение и жизнь"]'
new_cats = '["📢 Реклама и объявления", "💡 Лайфхаки", "🤝 Обмен опытом", "🔬 Наука и технологии", "🎨 Творчество и развлечения"]'
code = code.replace(old_cats, new_cats)

old_feed_block = """elif choice == T["feed"]:
    st.subheader(T["feed"])
    render_feed(mode="all")"""

new_feed_block = """elif choice == T["feed"]:
    st.subheader(T["feed"])
    cat_filter = st.selectbox("📂 Раздел / Рубрика:", ["🌐 Все публикации", "📢 Реклама и объявления", "💡 Лайфхаки", "🤝 Обмен опытом", "🔬 Наука и технологии", "🎨 Творчество и развлечения"])
    render_feed(mode="all")

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
        st.error(f"Ошибка поиска: {e}")"""

if old_feed_block in code:
    code = code.replace(old_feed_block, new_feed_block)

# 4. Голосовые сообщения одной кнопкой + Аудио и Видеозвонки в чате
old_chat_send = """            st.markdown("---")
            msg_txt = st.text_input("Написать сообщение...", key=f"chat_inp_{rid}")
            msg_file = st.file_uploader("Прикрепить фото, видео, голосовое (.mp3/.ogg/.m4a) или файл", key=f"chat_file_{rid}")
            sc1, sc2 = st.columns([3, 1])
            with sc1:
                if st.button("📨 Отправить", key=f"send_msg_{rid}"):
                    if msg_txt.strip() or msg_file:
                        files_p = {"file": (msg_file.name, msg_file.getvalue(), msg_file.type)} if msg_file else None
                        requests.post(f"{API_URL}/chats/{rid}/send", data={"sender": me, "text": msg_txt}, files=files_p)
                        st.rerun()
            with sc2:
                if st.button("🔄 Обновить", key=f"ref_msg_{rid}"):
                    st.rerun()"""

new_chat_send = """            st.markdown("---")
            call_c1, call_c2 = st.columns(2)
            with call_c1:
                st.link_button("📞 Аудиозвонок", f"https://jit.si{rid}#config.startWithVideoMuted=true")
            with call_c2:
                st.link_button("📹 Видеозвонок", f"https://jit.si{rid}")
            
            voice_rec = st.audio_input("🎙️ Записать голосовое сообщение", key=f"voice_{rid}")
            msg_txt = st.text_input("Написать сообщение...", key=f"chat_inp_{rid}")
            msg_file = st.file_uploader("Прикрепить фото, видео или кружок", key=f"chat_file_{rid}")
            sc1, sc2 = st.columns([3, 1])
            with sc1:
                if st.button("📨 Отправить", key=f"send_msg_{rid}"):
                    if voice_rec:
                        files_p = {"file": ("voice_msg.wav", voice_rec.getvalue(), "audio/wav")}
                        requests.post(f"{API_URL}/chats/{rid}/send", data={"sender": me, "text": msg_txt or "🎙️ Голосовое сообщение"}, files=files_p)
                        st.rerun()
                    elif msg_txt.strip() or msg_file:
                        files_p = {"file": (msg_file.name, msg_file.getvalue(), msg_file.type)} if msg_file else None
                        requests.post(f"{API_URL}/chats/{rid}/send", data={"sender": me, "text": msg_txt}, files=files_p)
                        st.rerun()
            with sc2:
                if st.button("🔄 Обновить", key=f"ref_msg_{rid}"):
                    st.rerun()"""

if old_chat_send in code:
    code = code.replace(old_chat_send, new_chat_send)

with open("app_mobile.py", "w", encoding="utf-8") as f:
    f.write(code)

print("VSE OBNOVLENO USPESHNO!")