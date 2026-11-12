"""Махваш — мобильный прототип на Streamlit.

Сервер API: python -m uvicorn main:app --reload
Этот экран:  python -m streamlit run app.py
"""

from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path

import httpx
import streamlit as st

API_BASE = os.environ.get("MAHVASH_API", "http://127.0.0.1:8000")
SCREENS = ("Лента", "Загрузить", "Подписки")
MEDIA_TYPES = {
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".webp": "image/webp",
    ".mp4": "video/mp4",
    ".webm": "video/webm",
    ".mov": "video/quicktime",
}


class ApiError(Exception):
    """Ошибка, которую можно показать на экране."""


def message_from(response: httpx.Response) -> str:
    try:
        payload = response.json()
    except ValueError:
        return response.text or f"Ошибка {response.status_code}"
    detail = payload.get("detail", payload)
    if isinstance(detail, list):
        parts: list[str] = []
        for item in detail:
            if isinstance(item, dict):
                loc = ".".join(str(bit) for bit in item.get("loc", []) if bit != "body")
                text = item.get("msg", "")
                parts.append(f"{loc}: {text}" if loc else text)
            else:
                parts.append(str(item))
        return "; ".join(part for part in parts if part) or "Проверьте поля формы"
    return str(detail)


def call(method: str, path: str, *, auth: bool = True, timeout: float = 30, **kwargs) -> httpx.Response:
    headers = dict(kwargs.pop("headers", {}) or {})
    token = st.session_state.get("token")
    if auth and token:
        headers["Authorization"] = f"Bearer {token}"
    try:
        response = httpx.request(method, f"{API_BASE}{path}", headers=headers, timeout=timeout, **kwargs)
    except httpx.RequestError as exc:
        raise ApiError(f"Сервер не отвечает на {API_BASE}. Запустите main.py.") from exc
    if response.status_code == 401 and auth:
        st.session_state.token = None
        st.session_state.me = None
        st.rerun()
    if response.status_code >= 400:
        raise ApiError(message_from(response))
    return response


def call_json(method: str, path: str, **kwargs):
    response = call(method, path, **kwargs)
    if response.status_code == 204 or not response.content:
        return None
    return response.json()


@st.cache_data(show_spinner=False, ttl=300)
def load_media(token: str, media_name: str) -> bytes:
    response = httpx.get(
        f"{API_BASE}/media/{media_name}",
        headers={"Authorization": f"Bearer {token}"},
        timeout=120,
    )
    if response.status_code >= 400:
        raise ApiError(message_from(response))
    return response.content


def backend_online() -> bool:
    try:
        response = httpx.get(f"{API_BASE}/health", timeout=2)
    except httpx.HTTPError:
        return False
    return response.status_code == 200


def human_size(size: int) -> str:
    if size < 1024 * 1024:
        return f"{max(size / 1024, 0.1):.0f} КБ"
    return f"{size / (1024 * 1024):.1f} МБ"


def format_time(value: str) -> str:
    moment = datetime.fromisoformat(value.replace("Z", "+00:00"))
    return moment.astimezone().strftime("%d.%m %H:%M")


def content_type_of(uploaded) -> str:
    kind = (uploaded.type or "").lower()
    if kind in MEDIA_TYPES.values():
        return kind
    return MEDIA_TYPES.get(Path(uploaded.name).suffix.lower(), kind or "application/octet-stream")


def author_name(user_id: str) -> str:
    me = st.session_state.get("me") or {}
    if user_id == me.get("id"):
        return me.get("display_name") or "Вы"
    names: dict[str, str] = st.session_state.setdefault("names", {})
    if user_id not in names:
        try:
            names[user_id] = call_json("GET", f"/users/{user_id}")["display_name"]
        except ApiError:
            names[user_id] = "Участник"
    return names[user_id]


def open_session(email: str, password: str) -> None:
    token = call_json("POST", "/auth/login", auth=False, json={"email": email, "password": password})
    st.session_state.token = token["access_token"]
    st.session_state.me = call_json("GET", "/users/me")
    st.session_state.feed_index = 0
    st.session_state.screen = "Лента"


def stretch():
    """Ширина виджета на всю колонку в Streamlit 1.66."""
    return {"width": "stretch"}


def apply_theme() -> None:
    st.markdown(
        """
        <style>
          [data-testid="stHeader"],
          [data-testid="stToolbar"],
          [data-testid="stDecoration"],
          footer { display: none; }
          .stApp {
            background:
              radial-gradient(900px 420px at 50% -8%, rgba(228, 179, 74, 0.16), transparent 55%),
              #050508;
          }
          .block-container {
            max-width: 420px;
            min-height: calc(100vh - 2rem);
            margin-top: 0.8rem;
            padding: 0.85rem 1.05rem 1.3rem;
            background: linear-gradient(180deg, #1a1a24 0%, #101016 28%, #0d0d13 100%);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 34px;
            box-shadow: 0 0 0 11px #09090d, 0 36px 90px rgba(0, 0, 0, 0.55);
          }
          .notch {
            width: 118px;
            height: 18px;
            margin: 0 auto 0.7rem;
            border-radius: 0 0 14px 14px;
            background: #09090d;
          }
          .brand {
            font-size: 1.7rem;
            font-weight: 700;
            letter-spacing: -0.04em;
            margin: 0;
          }
          .brand span { color: #e4b34a; }
          .quiet { color: rgba(246, 241, 230, 0.62); font-size: 0.92rem; margin-top: 0.15rem; }
          .who { font-weight: 650; padding-top: 0.35rem; }
          .pill {
            display: inline-block;
            padding: 0.12rem 0.5rem;
            border-radius: 999px;
            background: rgba(228, 179, 74, 0.16);
            color: #e4b34a;
            font-size: 0.75rem;
            letter-spacing: 0.04em;
          }
          .caption { font-size: 1.05rem; line-height: 1.35; margin: 0.7rem 0 0.2rem; }
          .meta { color: rgba(246, 241, 230, 0.55); font-size: 0.82rem; }
          .card {
            background: #16161f;
            border: 1px solid rgba(255, 255, 255, 0.06);
            border-radius: 18px;
            padding: 0.85rem 0.9rem;
            margin-bottom: 0.7rem;
          }
          .card b { display: block; }
          .card span { color: rgba(246, 241, 230, 0.55); font-size: 0.82rem; }
          [data-testid="stVideo"] video,
          [data-testid="stImage"] img {
            border-radius: 22px;
            background: #000;
            max-height: 62vh;
            object-fit: contain;
          }
          [data-testid="stRadio"] {
            background: #12121a;
            border-radius: 16px;
            padding: 0.15rem 0.35rem 0.35rem;
            border: 1px solid rgba(255, 255, 255, 0.06);
          }
          .status-ok { color: #8dcea0; }
          .status-off { color: #e07a7a; }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_auth() -> None:
    st.markdown('<div class="notch"></div>', unsafe_allow_html=True)
    st.markdown('<p class="brand"><span>✦</span> Махваш</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="quiet">Короткие видео и фото для своих. Вход только по почте.</p>',
        unsafe_allow_html=True,
    )
    online = backend_online()
    if online:
        st.markdown('<p class="status-ok">Сервер на связи</p>', unsafe_allow_html=True)
    else:
        st.markdown(
            f'<p class="status-off">Нет ответа от {API_BASE}</p>',
            unsafe_allow_html=True,
        )

    st.radio(
        "Режим",
        ("Регистрация", "Вход"),
        horizontal=True,
        label_visibility="collapsed",
        key="auth_mode",
    )
    if st.session_state.auth_mode == "Регистрация":
        render_register()
    else:
        render_login()


def render_register() -> None:
    with st.form("register"):
        email = st.text_input("Почта", placeholder="you@example.com")
        display_name = st.text_input("Имя", placeholder="Как вас видеть в ленте")
        password = st.text_input("Пароль", type="password", placeholder="Минимум 8 символов")
        submitted = st.form_submit_button("Создать аккаунт", type="primary", **stretch())
    if not submitted:
        return
    email = email.strip()
    display_name = display_name.strip()
    if not email or "@" not in email:
        st.error("Укажите почту.")
        return
    if not display_name:
        st.error("Укажите имя.")
        return
    if len(password) < 8:
        st.error("Пароль должен быть не короче 8 символов.")
        return
    try:
        call_json(
            "POST",
            "/auth/register",
            auth=False,
            json={"email": email, "password": password, "display_name": display_name},
        )
        open_session(email, password)
    except ApiError as exc:
        st.error(str(exc))
        return
    st.rerun()


def render_login() -> None:
    with st.form("login"):
        email = st.text_input("Почта", placeholder="you@example.com")
        password = st.text_input("Пароль", type="password")
        submitted = st.form_submit_button("Войти", type="primary", **stretch())
    if not submitted:
        return
    try:
        open_session(email.strip(), password)
    except ApiError as exc:
        st.error(str(exc))
        return
    st.rerun()


def render_topbar() -> None:
    me = st.session_state.me
    left, right = st.columns([4, 1.3])
    left.markdown(
        f'<div class="who"><span class="pill">Махваш</span> &nbsp; {me["display_name"]}</div>',
        unsafe_allow_html=True,
    )
    if right.button("Выйти", **stretch()):
        try:
            call("POST", "/auth/logout")
        except ApiError:
            pass
        st.session_state.token = None
        st.session_state.me = None
        st.rerun()
    st.radio("Раздел", SCREENS, horizontal=True, label_visibility="collapsed", key="screen")


def render_feed() -> None:
    try:
        posts = list(reversed(call_json("GET", "/feed")))
    except ApiError as exc:
        st.error(str(exc))
        return

    head, refresh = st.columns([4, 1.4])
    head.markdown('<p class="quiet">Свои записи и записи тех, на кого вы подписаны</p>', unsafe_allow_html=True)
    if refresh.button("Обновить", **stretch()):
        load_media.clear()
        st.rerun()

    if not posts:
        st.markdown(
            """
            <div class="card">
              <b>Лента пока пустая</b>
              <span>Загрузите фото или видео — или подпишитесь на человека по его id.</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    index = min(max(int(st.session_state.get("feed_index", 0)), 0), len(posts) - 1)
    st.session_state.feed_index = index
    post = posts[index]
    kind = "Видео" if post["media_kind"] == "video" else "Фото"

    st.markdown(
        f'<p class="meta">{index + 1} / {len(posts)} · <span class="pill">{kind}</span></p>',
        unsafe_allow_html=True,
    )
    try:
        payload = load_media(st.session_state.token, post["media_name"])
    except ApiError as exc:
        st.warning(str(exc))
        payload = None
    if payload is not None:
        if post["media_kind"] == "video":
            st.video(payload)
        else:
            st.image(payload, **stretch())

    caption = post["caption"] or "Без подписи"
    st.markdown(f'<p class="caption">{caption}</p>', unsafe_allow_html=True)
    st.markdown(
        f'<p class="meta">{author_name(post["author_id"])} · {format_time(post["created_at"])} · {human_size(post["size_bytes"])}</p>',
        unsafe_allow_html=True,
    )

    previous, following = st.columns(2)
    if previous.button("Предыдущее", disabled=index == 0, **stretch()):
        st.session_state.feed_index = index - 1
        st.rerun()
    if following.button("Следующее", disabled=index >= len(posts) - 1, **stretch()):
        st.session_state.feed_index = index + 1
        st.rerun()


def render_upload() -> None:
    st.markdown('<p class="quiet">Фото до 8 МБ или короткое видео до 50 МБ.</p>', unsafe_allow_html=True)
    uploaded = st.file_uploader(
        "Файл",
        type=["jpg", "jpeg", "png", "webp", "mp4", "webm", "mov"],
        label_visibility="collapsed",
    )
    caption = st.text_area("Подпись", max_chars=500, placeholder="Пара слов к кадру", height=90)
    if not st.button("Опубликовать", type="primary", disabled=uploaded is None, **stretch()):
        return
    kind = content_type_of(uploaded)
    if kind not in MEDIA_TYPES.values():
        st.error("Нужны jpeg, png, webp, mp4, webm или mov.")
        return
    try:
        with st.spinner("Загружаем…"):
            call_json(
                "POST",
                "/posts",
                timeout=120,
                data={"caption": caption.strip()},
                files={"file": (uploaded.name, uploaded.getvalue(), kind)},
            )
    except ApiError as exc:
        st.error(str(exc))
        return
    load_media.clear()
    st.session_state.feed_index = 0
    st.session_state.screen = "Лента"
    st.rerun()


def person_row(person: dict, *, action: str) -> None:
    info, button = st.columns([3.2, 1.5])
    info.markdown(
        f'<div class="card"><b>{person["display_name"]}</b><span>{person["email"]}</span></div>',
        unsafe_allow_html=True,
    )
    if action == "unfollow" and button.button("Отписаться", key=f"un-{person['id']}", **stretch()):
        try:
            call_json("DELETE", f"/users/{person['id']}/follow")
        except ApiError as exc:
            st.error(str(exc))
            return
        st.rerun()


def render_following() -> None:
    me = st.session_state.me
    st.markdown('<p class="quiet">Ваш id — его можно передать другому аккаунту.</p>', unsafe_allow_html=True)
    st.code(me["id"], language=None)

    with st.form("follow"):
        target = st.text_input("Id человека", placeholder="Вставьте id")
        submitted = st.form_submit_button("Подписаться", type="primary", **stretch())
    if submitted:
        target = target.strip()
        if not target:
            st.error("Вставьте id.")
        else:
            try:
                call_json("POST", f"/users/{target}/follow")
                st.session_state.names.pop(target, None)
            except ApiError as exc:
                st.error(str(exc))
            else:
                st.rerun()

    try:
        following = call_json("GET", f"/users/{me['id']}/following")
        followers = call_json("GET", f"/users/{me['id']}/followers")
    except ApiError as exc:
        st.error(str(exc))
        return

    st.markdown(f"### Подписки · {len(following)}")
    if following:
        for person in following:
            person_row(person, action="unfollow")
    else:
        st.markdown('<p class="meta">Вы пока ни на кого не подписаны.</p>', unsafe_allow_html=True)

    st.markdown(f"### Подписчики · {len(followers)}")
    if followers:
        for person in followers:
            st.markdown(
                f'<div class="card"><b>{person["display_name"]}</b><span>{person["email"]}</span></div>',
                unsafe_allow_html=True,
            )
    else:
        st.markdown('<p class="meta">Пока никто не подписался.</p>', unsafe_allow_html=True)


def main() -> None:
    st.set_page_config(page_title="Махваш", page_icon="✦", layout="centered", initial_sidebar_state="collapsed")
    apply_theme()
    st.session_state.setdefault("token", None)
    st.session_state.setdefault("me", None)
    st.session_state.setdefault("names", {})
    st.session_state.setdefault("feed_index", 0)

    if st.session_state.token and st.session_state.me is None:
        try:
            st.session_state.me = call_json("GET", "/users/me")
        except ApiError as exc:
            st.session_state.token = None
            st.error(str(exc))

    if not st.session_state.token or not st.session_state.me:
        render_auth()
        return

    st.markdown('<div class="notch"></div>', unsafe_allow_html=True)
    render_topbar()
    screen = st.session_state.get("screen", "Лента")
    if screen == "Загрузить":
        render_upload()
    elif screen == "Подписки":
        render_following()
    else:
        render_feed()


if __name__ == "__main__":
    main()
