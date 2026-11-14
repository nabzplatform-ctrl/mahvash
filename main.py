import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from supabase import create_client, Client
import time
import hashlib
from datetime import datetime, timezone, timedelta

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL", "https://supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")
if not SUPABASE_KEY:
    raise RuntimeError("КРИТИЧЕСКАЯ ОШИБКА: Не найден SUPABASE_KEY в переменных окружения!")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

app = FastAPI(title="NABZ - International Social Network", version="3.0_SECURE")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

IP_RATE_LIMIT = {}

@app.middleware("http")
async def rate_limit_shield(request: Request, call_next):
    client_ip = request.client.host if request.client else "unknown"
    now = time.time()
    history = [t for t in IP_RATE_LIMIT.get(client_ip, []) if now - t < 60]
    if len(history) >= 60:
        return JSONResponse(status_code=429, content={"detail": "Слишком много запросов. Подождите минуту."})
    history.append(now)
    IP_RATE_LIMIT[client_ip] = history
    return await call_next(request)

def hash_pwd(pwd: str) -> str:
    return hashlib.sha256(pwd.encode("utf-8")).hexdigest()

class UserRegister(BaseModel):
    email: str
    username: str
    password: str
    first_name: str
    last_name: str
    bio: Optional[str] = ""
    language: str = "ru"

class UserLogin(BaseModel):
    username: str
    password: str

class PasswordReset(BaseModel):
    username: str
    email: str
    new_password: str

class ProfileUpdate(BaseModel):
    first_name: str
    last_name: str
    bio: str
    language: str
    is_private: bool

class LikeAction(BaseModel):
    post_id: int
    username: str

class BookmarkAction(BaseModel):
    post_id: int
    username: str

class PostEdit(BaseModel):
    text: str
    username: str

class RepostAction(BaseModel):
    post_id: int
    username: str

class FollowAction(BaseModel):
    follower: str
    following: str

class BlockAction(BaseModel):
    blocker: str
    blocked: str

class ReportCreate(BaseModel):
    reporter: str
    post_id: Optional[int] = None
    target_username: Optional[str] = None
    reason: str

class CommentCreate(BaseModel):
    post_id: int
    username: str
    text: str
    parent_id: Optional[int] = None

class CommentEdit(BaseModel):
    text: str
    username: str

def add_notification(recipient: str, sender: str, n_type: str, post_id: Optional[int], msg: str):
    if not recipient or not sender or recipient == sender or recipient == "Аноним":
        return
    try:
        now_str = datetime.now().strftime("%d.%m.%Y %H:%M")
        supabase.table("notifications").insert({
            "recipient_username": recipient,
            "sender_username": sender,
            "type": n_type,
            "post_id": post_id,
            "message": msg,
            "is_read": False,
            "created_at": now_str
        }).execute()
    except:
        pass

@app.get("/")
def read_root():
    return {"status": "online", "project": "NABZ 2.5"}

@app.post("/auth/register")
def register(user: UserRegister):
    try:
        uname = user.username.strip().lstrip("@")
        check = supabase.table("profiles").select("id").eq("username", uname).execute()
        if check.data:
            raise HTTPException(status_code=400, detail="Этот @username уже занят! Выберите другой.")
            
        auth_res = supabase.auth.sign_up({"email": user.email, "password": user.password})
        if not auth_res.user:
            raise HTTPException(status_code=400, detail="Не удалось создать пользователя")
            
        post_data = {
            "id": auth_res.user.id,
            "username": uname,
            "email": user.email,
            "password_hash": hash_pwd(user.password),
            "first_name": user.first_name,
            "last_name": user.last_name,
            "bio": user.bio,
            "language": user.language,
            "is_verified": True,
            "is_private": False
        }
        supabase.table("profiles").insert(post_data).execute()
        return {"status": "success", "username": uname, "language": user.language}
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/auth/login")
def login(data: UserLogin):
    try:
        uname = data.username.strip().lstrip("@")
        res = supabase.table("profiles").select("*").eq("username", uname).execute()
        if not res.data:
            raise HTTPException(status_code=404, detail="Пользователь с таким @username не найден")
        prof = res.data[0]
        stored_hash = prof.get("password_hash", "12345")
        if stored_hash != "12345" and stored_hash != hash_pwd(data.password):
            raise HTTPException(status_code=401, detail="Неверный пароль!")
        return {"status": "success", "profile": prof}
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/auth/reset_password")
def reset_password(data: PasswordReset):
    try:
        uname = data.username.strip().lstrip("@")
        res = supabase.table("profiles").select("id, email").eq("username", uname).execute()
        if not res.data:
            raise HTTPException(status_code=404, detail="Пользователь не найден")
        if res.data.get("email") and res.data.get("email").lower() != data.email.strip().lower():
            raise HTTPException(status_code=400, detail="Email не совпадает с привязанным к аккаунту")
        supabase.table("profiles").update({"password_hash": hash_pwd(data.new_password)}).eq("username", uname).execute()
        return {"status": "success", "message": "Пароль успешно обновлён!"}
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/profile/{username}")
def get_profile(username: str, viewer: Optional[str] = None):
    try:
        uname = username.strip().lstrip("@")
        res = supabase.table("profiles").select("*").eq("username", uname).execute()
        if not res.data:
            return {"status": "not_found"}
        prof = res.data[0]
        followers = supabase.table("user_follows").select("id").eq("following_username", uname).execute()
        following = supabase.table("user_follows").select("id").eq("follower_username", uname).execute()
        prof["followers_count"] = len(followers.data or [])
        prof["following_count"] = len(following.data or [])
        prof["is_following"] = False
        if viewer:
            f_check = supabase.table("user_follows").select("id").eq("follower_username", viewer).eq("following_username", uname).execute()
            prof["is_following"] = bool(f_check.data)
        return {"status": "success", "profile": prof}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/profile/{username}")
def update_profile(username: str, data: ProfileUpdate):
    try:
        supabase.table("profiles").update({
            "first_name": data.first_name,
            "last_name": data.last_name,
            "bio": data.bio,
            "language": data.language,
            "is_private": data.is_private
        }).eq("username", username).execute()
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/profile/{username}/media")
async def upload_profile_media(username: str, media_type: str = Form(...), file: UploadFile = File(...)):
    try:
        ext = file.filename.split(".")[-1].lower() if "." in file.filename else "jpg"
        file_name = f"prof_{username}_{media_type}_{int(time.time())}.{ext}"
        file_bytes = await file.read()
        supabase.storage.from_("nabz-media").upload(path=file_name, file=file_bytes, file_options={"content-type": file.content_type})
        public_url = supabase.storage.from_("nabz-media").get_public_url(file_name)
        col_name = "avatar_url" if media_type == "avatar" else "cover_url"
        supabase.table("profiles").update({col_name: public_url}).eq("username", username).execute()
        return {"status": "success", "url": public_url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/posts/create_with_media")
async def create_with_media(
    text: str = Form(...), 
    username: Optional[str] = Form(None),
    is_draft: bool = Form(False),
    files: List[UploadFile] = File(default=[])
):
    try:
        author_name = username if username else "Аноним"
        user_res = supabase.table("profiles").select("id").eq("username", author_name).execute()
        real_user_id = user_res.data[0]["id"] if (user_res and user_res.data and len(user_res.data) > 0) else None
        current_time_str = datetime.now().strftime("%d.%m.%Y %H:%M")
        
        uploaded_urls = []
        for file in files:
            if not file.filename:
                continue
            ext = file.filename.split(".")[-1].lower() if "." in file.filename else "jpg"
            file_name = f"post_{int(time.time())}_{file.filename}"
            file_bytes = await file.read()
            supabase.storage.from_("nabz-media").upload(path=file_name, file=file_bytes, file_options={"content-type": file.content_type})
            public_url = supabase.storage.from_("nabz-media").get_public_url(file_name)
            uploaded_urls.append(public_url)
            
        media_urls_str = ",".join(uploaded_urls) if uploaded_urls else ""
        post_data = {
            "user_id": real_user_id,
            "username": author_name,
            "text": text,
            "media_urls": media_urls_str,
            "likes_count": 0,
            "views_count": 0,
            "is_draft": is_draft,
            "created_at": current_time_str
        }
        res = supabase.table("posts").insert(post_data).execute()
        new_post_id = res.data[0]["id"] if res.data else 0
        
        if not is_draft:
            for word in text.split():
                if word.startswith("@") and len(word) > 1:
                    mentioned = word[1:].strip(".,!?")
                    add_notification(mentioned, author_name, "mention", new_post_id, f"@{author_name} упомянул вас в посте")
                    
        return {"status": "success", "message": "Сохранено в черновики!" if is_draft else "Пост опубликован!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/posts/publish_draft/{post_id}")
def publish_draft(post_id: int):
    try:
        now_str = datetime.now().strftime("%d.%m.%Y %H:%M")
        supabase.table("posts").update({"is_draft": False, "created_at": now_str}).eq("id", post_id).execute()
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/posts/list")
def get_posts_list(
    limit: int = 10, 
    offset: int = 0, 
    search: Optional[str] = None, 
    bookmarked_by: Optional[str] = None, 
    viewer: Optional[str] = None,
    feed_mode: str = "all",
    author_filter: Optional[str] = None
):
    try:
        query = supabase.table("posts").select("*").order("id", desc=True)
        
        if feed_mode == "drafts":
            if not viewer:
                return {"status": "success", "posts": []}
            query = query.eq("is_draft", True).eq("username", viewer)
        else:
            query = query.eq("is_draft", False)
            
        if author_filter:
            query = query.eq("username", author_filter)
            
        if bookmarked_by:
            bm_res = supabase.table("post_bookmarks").select("post_id").eq("username", bookmarked_by).execute()
            bm_ids = [item["post_id"] for item in bm_res.data] if bm_res.data else []
            if not bm_ids:
                return {"status": "success", "posts": []}
            query = query.in_("id", bm_ids)
            
        if feed_mode == "following" and viewer:
            f_res = supabase.table("user_follows").select("following_username").eq("follower_username", viewer).execute()
            f_names = [x["following_username"] for x in (f_res.data or [])]
            if not f_names:
                return {"status": "success", "posts": []}
            query = query.in_("username", f_names)
            
        if search:
            query = query.or_(f"text.ilike.%{search}%,username.ilike.%{search}%")
            
        res = query.range(offset, offset + limit - 1).execute()
        raw_posts = res.data or []
        
        blocked_users = set()
        following_users = set()
        if viewer:
            b_res = supabase.table("user_blocks").select("blocked_username").eq("blocker_username", viewer).execute()
            blocked_users = {x["blocked_username"] for x in (b_res.data or [])}
            fl_res = supabase.table("user_follows").select("following_username").eq("follower_username", viewer).execute()
            following_users = {x["following_username"] for x in (fl_res.data or [])}
            
        priv_res = supabase.table("profiles").select("username, avatar_url, is_private").execute()
        prof_map = {p["username"]: p for p in (priv_res.data or [])}
        
        posts = []
        for p in raw_posts:
            au = p.get("username")
            if au in blocked_users and viewer != "admin1":
                continue
            p_info = prof_map.get(au, {})
            if p_info.get("is_private") and au != viewer and au not in following_users and viewer != "admin1":
                continue
            p["author_avatar"] = p_info.get("avatar_url", "")
            p["is_following_author"] = (au in following_users)
            posts.append(p)
            
        if posts:
            post_ids = [p["id"] for p in posts]
            c_res = supabase.table("post_comments").select("*").in_("post_id", post_ids).order("id", desc=False).execute()
            comments_map = {}
            for c in (c_res.data or []):
                comments_map.setdefault(c["post_id"], []).append(c)
            for p in posts:
                p["comments"] = comments_map.get(p["id"], [])
                
            if viewer and viewer != "Аноним":
                v_res = supabase.table("post_views").select("post_id").eq("username", viewer).in_("post_id", post_ids).execute()
                viewed_ids = {v["post_id"] for v in (v_res.data or [])}
                new_views = [{"post_id": pid, "username": viewer} for pid in post_ids if pid not in viewed_ids]
                if new_views:
                    try:
                        supabase.table("post_views").insert(new_views).execute()
                        for p in posts:
                            if p["id"] not in viewed_ids:
                                new_cnt = (p.get("views_count") or 0) + 1
                                p["views_count"] = new_cnt
                                supabase.table("posts").update({"views_count": new_cnt}).eq("id", p["id"]).execute()
                    except:
                        pass
                        
        return {"status": "success", "posts": posts}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/posts/repost")
def repost_post(action: RepostAction):
    try:
        orig_res = supabase.table("posts").select("*").eq("id", action.post_id).execute()
        if not orig_res.data:
            raise HTTPException(status_code=404, detail="Оригинал поста не найден")
        orig = orig_res.data[0]
        now_str = datetime.now().strftime("%d.%m.%Y %H:%M")
        new_post = {
            "username": action.username,
            "text": orig.get("text", ""),
            "media_urls": orig.get("media_urls", ""),
            "likes_count": 0,
            "views_count": 0,
            "is_draft": False,
            "repost_of_id": orig["id"],
            "repost_author": orig.get("username"),
            "created_at": now_str
        }
        supabase.table("posts").insert(new_post).execute()
        add_notification(orig.get("username"), action.username, "repost", orig["id"], f"@{action.username} сделал репост вашей записи 🔁")
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/posts/edit/{post_id}")
def edit_post(post_id: int, data: PostEdit):
    try:
        post_res = supabase.table("posts").select("username").eq("id", post_id).execute()
        if not post_res.data:
            raise HTTPException(status_code=404, detail="Пост не найден")
        author = post_res.data.get("username")
        if data.username != author and data.username != "admin1":
            raise HTTPException(status_code=403, detail="Нет прав на редактирование")
        now_str = datetime.now().strftime("%d.%m.%Y %H:%M")
        supabase.table("posts").update({"text": data.text, "updated_at": now_str}).eq("id", post_id).execute()
        return {"status": "success"}
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/posts/delete/{post_id}")
def delete_post(post_id: int, username: str = ""):
    try:
        post_res = supabase.table("posts").select("username, media_urls, repost_of_id").eq("id", post_id).execute()
        if not post_res.data:
            raise HTTPException(status_code=404, detail="Пост не найден")
        post = post_res.data[0]
        if username != post.get("username") and username != "admin1":
            raise HTTPException(status_code=403, detail="Ошибка безопасности: вы не можете удалить чужую публикацию!")
            
        if post.get("media_urls") and not post.get("repost_of_id"):
            urls = post["media_urls"].split(",")
            for url in urls:
                try:
                    file_name = url.split("/")[-1]
                    supabase.storage.from_("nabz-media").remove([file_name])
                except:
                    pass
        supabase.table("posts").delete().eq("id", post_id).execute()
        return {"status": "success"}
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/posts/like")
def toggle_like(action: LikeAction):
    try:
        existing = supabase.table("post_likes").select("id").eq("post_id", action.post_id).eq("username", action.username).execute()
        post_res = supabase.table("posts").select("likes_count, username").eq("id", action.post_id).execute()
        if not post_res.data:
            raise HTTPException(status_code=404, detail="Пост не найден")
        current_likes = post_res.data.get("likes_count") or 0
        author = post_res.data.get("username")
        
        if existing.data:
            supabase.table("post_likes").delete().eq("id", existing.data["id"]).execute()
            new_likes = max(0, current_likes - 1)
            liked = False
        else:
            supabase.table("post_likes").insert({"post_id": action.post_id, "username": action.username}).execute()
            new_likes = current_likes + 1
            liked = True
            add_notification(author, action.username, "like", action.post_id, f"@{action.username} оценил ваш пост ❤️")
            
        supabase.table("posts").update({"likes_count": new_likes}).eq("id", action.post_id).execute()
        return {"status": "success", "likes_count": new_likes, "liked": liked}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/posts/bookmark")
def toggle_bookmark(action: BookmarkAction):
    try:
        existing = supabase.table("post_bookmarks").select("id").eq("post_id", action.post_id).eq("username", action.username).execute()
        if existing.data:
            supabase.table("post_bookmarks").delete().eq("id", existing.data["id"]).execute()
            return {"status": "success", "bookmarked": False}
        else:
            supabase.table("post_bookmarks").insert({"post_id": action.post_id, "username": action.username}).execute()
            return {"status": "success", "bookmarked": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/users/follow")
def toggle_follow(action: FollowAction):
    try:
        if action.follower == action.following:
            return {"status": "ignored"}
        existing = supabase.table("user_follows").select("id").eq("follower_username", action.follower).eq("following_username", action.following).execute()
        if existing.data:
            supabase.table("user_follows").delete().eq("id", existing.data["id"]).execute()
            return {"status": "success", "following": False}
        else:
            supabase.table("user_follows").insert({"follower_username": action.follower, "following_username": action.following}).execute()
            add_notification(action.following, action.follower, "follow", None, f"@{action.follower} подписался на вас 👤")
            return {"status": "success", "following": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/users/block")
def toggle_block(action: BlockAction):
    try:
        if action.blocker == action.blocked:
            return {"status": "ignored"}
        existing = supabase.table("user_blocks").select("id").eq("blocker_username", action.blocker).eq("blocked_username", action.blocked).execute()
        if existing.data:
            supabase.table("user_blocks").delete().eq("id", existing.data["id"]).execute()
            return {"status": "success", "blocked": False}
        else:
            supabase.table("user_blocks").insert({"blocker_username": action.blocker, "blocked_username": action.blocked}).execute()
            return {"status": "success", "blocked": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/users/blocked/{username}")
def get_blocked_list(username: str):
    try:
        res = supabase.table("user_blocks").select("blocked_username").eq("blocker_username", username).execute()
        return {"status": "success", "blocked": [x["blocked_username"] for x in (res.data or [])]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/reports/create")
def create_report(data: ReportCreate):
    try:
        now_str = datetime.now().strftime("%d.%m.%Y %H:%M")
        supabase.table("reports").insert({
            "reporter_username": data.reporter,
            "target_post_id": data.post_id,
            "target_username": data.target_username,
            "reason": data.reason,
            "status": "pending",
            "created_at": now_str
        }).execute()
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/reports/list")
def get_reports():
    try:
        res = supabase.table("reports").select("*").order("id", desc=True).execute()
        return {"status": "success", "reports": res.data or []}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/posts/comment")
def add_comment(data: CommentCreate):
    try:
        last_c = supabase.table("post_comments").select("created_ts").eq("username", data.username).order("id", desc=True).limit(1).execute()
        if last_c.data:
            last_time = datetime.fromisoformat(last_c.data["created_ts"].replace("Z", "+00:00"))
            diff = (datetime.now(timezone.utc) - last_time).total_seconds()
            if diff < 5:
                raise HTTPException(status_code=429, detail=f"Антиспам: подождите {int(5 - diff) + 1} сек.")
                
        now_str = datetime.now().strftime("%d.%m.%Y %H:%M")
        res = supabase.table("post_comments").insert({
            "post_id": data.post_id,
            "parent_id": data.parent_id,
            "username": data.username,
            "text": data.text,
            "created_at": now_str
        }).execute()
        
        post_res = supabase.table("posts").select("username").eq("id", data.post_id).execute()
        if post_res.data:
            author = post_res.data.get("username")
            add_notification(author, data.username, "comment", data.post_id, f"@{data.username} прокомментировал: {data.text[:30]}...")
        return {"status": "success"}
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/comments/edit/{comment_id}")
def edit_comment(comment_id: int, data: CommentEdit):
    try:
        c_res = supabase.table("post_comments").select("username").eq("id", comment_id).execute()
        if not c_res.data:
            raise HTTPException(status_code=404, detail="Комментарий не найден")
        if data.username != c_res.data["username"] and data.username != "admin1":
            raise HTTPException(status_code=403, detail="Нет прав")
        supabase.table("post_comments").update({"text": data.text}).eq("id", comment_id).execute()
        return {"status": "success"}
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/comments/delete/{comment_id}")
def delete_comment(comment_id: int, username: str = ""):
    try:
        c_res = supabase.table("post_comments").select("username").eq("id", comment_id).execute()
        if not c_res.data:
            raise HTTPException(status_code=404, detail="Комментарий не найден")
        if username != c_res.data[0].get("username") and username != "admin1":
            raise HTTPException(status_code=403, detail="Нельзя удалить чужой комментарий!")
        supabase.table("post_comments").delete().eq("id", comment_id).execute()
        return {"status": "success"}
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/notifications/{username}")
def get_notifications(username: str):
    try:
        res = supabase.table("notifications").select("*").eq("recipient_username", username).order("id", desc=True).limit(30).execute()
        return {"status": "success", "notifications": res.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/notifications/read_all/{username}")
def mark_notifications_read(username: str):
    try:
        supabase.table("notifications").update({"is_read": True}).eq("recipient_username", username).execute()
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

from datetime import timedelta

@app.post("/stories/create")
async def create_story(
    username: str = Form(...),
    caption: str = Form(""),
    file: UploadFile = File(...)
):
    try:
        ext = file.filename.split(".")[-1].lower() if "." in file.filename else "jpg"
        media_type = "video" if ext in ["mp4", "mov", "avi", "mkv"] else "image"
        file_name = f"story_{username}_{int(time.time())}.{ext}"
        file_bytes = await file.read()
        
        supabase.storage.from_("nabz-media").upload(
            path=file_name,
            file=file_bytes,
            file_options={"content-type": file.content_type}
        )
        public_url = supabase.storage.from_("nabz-media").get_public_url(file_name)
        
        now_str = datetime.now().strftime("%d.%m.%Y %H:%M")
        expires_iso = (datetime.now(timezone.utc) + timedelta(hours=24)).isoformat()
        
        supabase.table("stories").insert({
            "username": username,
            "media_url": public_url,
            "media_type": media_type,
            "caption": caption,
            "views_count": 0,
            "created_at": now_str,
            "expires_at": expires_iso
        }).execute()
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stories/active")
def get_active_stories():
    try:
        now_iso = datetime.now(timezone.utc).isoformat()
        res = supabase.table("stories").select("*").gt("expires_at", now_iso).order("id", desc=True).execute()
        return {"status": "success", "stories": res.data or []}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/stories/view/{story_id}")
def view_story(story_id: int):
    try:
        res = supabase.table("stories").select("views_count").eq("id", story_id).execute()
        if res.data:
            cnt = (res.data[0].get("views_count") or 0) + 1
            supabase.table("stories").update({"views_count": cnt}).eq("id", story_id).execute()
        return {"status": "success"}
    except:
        return {"status": "ignored"}

@app.delete("/stories/delete/{story_id}")
def delete_story(story_id: int, username: str = ""):
    try:
        res = supabase.table("stories").select("username, media_url").eq("id", story_id).execute()
        if not res.data:
            raise HTTPException(status_code=404, detail="История не найдена")
        if username != res.data[0].get("username") and username != "admin1":
            raise HTTPException(status_code=403, detail="Нельзя удалить чужую Story!")
        if res.data[0].get("media_url"):
            fname = res.data[0]["media_url"].split("/")[-1]
            try:
                supabase.storage.from_("nabz-media").remove([fname])
            except:
                pass
        supabase.table("stories").delete().eq("id", story_id).execute()
        return {"status": "success"}
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/posts/create_reel")
async def create_reel(
    text: str = Form(""),
    username: str = Form(...),
    is_reel: bool = Form(True),
    video_file: UploadFile = File(...),
    cover_file: Optional[UploadFile] = File(None)
):
    try:
        v_ext = video_file.filename.split(".")[-1].lower() if "." in video_file.filename else "mp4"
        v_name = f"reel_{username}_{int(time.time())}.{v_ext}"
        v_bytes = await video_file.read()
        supabase.storage.from_("nabz-media").upload(path=v_name, file=v_bytes, file_options={"content-type": video_file.content_type})
        video_url = supabase.storage.from_("nabz-media").get_public_url(v_name)
        
        cover_url = ""
        if cover_file and cover_file.filename:
            c_ext = cover_file.filename.split(".")[-1].lower() if "." in cover_file.filename else "jpg"
            c_name = f"cover_{username}_{int(time.time())}.{c_ext}"
            c_bytes = await cover_file.read()
            supabase.storage.from_("nabz-media").upload(path=c_name, file=c_bytes, file_options={"content-type": cover_file.content_type})
            cover_url = supabase.storage.from_("nabz-media").get_public_url(c_name)
            
        now_str = datetime.now().strftime("%d.%m.%Y %H:%M")
        supabase.table("posts").insert({
            "username": username,
            "text": text,
            "media_urls": video_url,
            "cover_url": cover_url,
            "is_reel": is_reel,
            "is_draft": False,
            "likes_count": 0,
            "views_count": 0,
            "created_at": now_str
        }).execute()
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class ChatRoomCreate(BaseModel):
    creator: str
    members: List[str]
    name: Optional[str] = ""
    is_group: bool = False

@app.post("/users/ping/{username}")
def ping_online(username: str):
    try:
        now_iso = datetime.now(timezone.utc).isoformat()
        supabase.table("profiles").update({"last_seen": now_iso}).eq("username", username).execute()
        return {"status": "success"}
    except:
        return {"status": "ignored"}

@app.post("/chats/create")
def create_chat_room(data: ChatRoomCreate):
    try:
        all_members = sorted(list(set([data.creator] + [m.strip().lstrip("@") for m in data.members if m.strip()])))
        if len(all_members) < 2:
            raise HTTPException(status_code=400, detail="Укажите хотя бы одного собеседника")
        members_str = ",".join(all_members)
        
        if not data.is_group and len(all_members) == 2:
            existing = supabase.table("chat_rooms").select("*").eq("is_group", False).eq("members", members_str).execute()
            if existing.data:
                return {"status": "success", "room": existing.data}
                
        now_str = datetime.now().strftime("%d.%m.%Y %H:%M")
        room_name = data.name.strip() if data.is_group and data.name else ""
        res = supabase.table("chat_rooms").insert({
            "name": room_name,
            "is_group": data.is_group,
            "members": members_str,
            "created_at": now_str
        }).execute()
        return {"status": "success", "room": res.data if res.data else {}}
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/chats/user/{username}")
def get_user_chats(username: str):
    try:
        res = supabase.table("chat_rooms").select("*").order("id", desc=True).execute()
        user_rooms = []
        for r in (res.data or []):
            m_list = r.get("members", "").split(",")
            if username in m_list:
                user_rooms.append(r)
        return {"status": "success", "rooms": user_rooms}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/chats/{room_id}/messages")
def get_chat_messages(room_id: int, viewer: str):
    try:
        supabase.table("chat_messages").update({"is_read": True}).eq("room_id", room_id).neq("sender_username", viewer).execute()
        res = supabase.table("chat_messages").select("*").eq("room_id", room_id).order("id", desc=False).execute()
        return {"status": "success", "messages": res.data or []}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chats/{room_id}/send")
async def send_chat_message(
    room_id: int,
    sender: str = Form(...),
    text: str = Form(""),
    file: Optional[UploadFile] = File(None)
):
    try:
        media_url = ""
        media_type = "text"
        if file and file.filename:
            ext = file.filename.split(".")[-1].lower() if "." in file.filename else "bin"
            if ext in ["jpg", "jpeg", "png", "gif"]:
                media_type = "image"
            elif ext in ["mp4", "mov", "avi", "mkv"]:
                media_type = "video"
            elif ext in ["mp3", "wav", "ogg", "m4a"]:
                media_type = "audio"
            else:
                media_type = "file"
                
            fname = f"chat_{room_id}_{int(time.time())}.{ext}"
            fbytes = await file.read()
            supabase.storage.from_("nabz-media").upload(path=fname, file=fbytes, file_options={"content-type": file.content_type})
            media_url = supabase.storage.from_("nabz-media").get_public_url(fname)
            
        now_str = datetime.now().strftime("%H:%M")
        supabase.table("chat_messages").insert({
            "room_id": room_id,
            "sender_username": sender,
            "text": text,
            "media_url": media_url,
            "media_type": media_type,
            "is_read": False,
            "created_at": now_str
        }).execute()
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/explore/data")
def get_explore_data(viewer: Optional[str] = None):
    try:
        p_res = supabase.table("posts").select("*").eq("is_draft", False).order("likes_count", desc=True).limit(15).execute()
        popular_posts = p_res.data or []
        
        tags_count = {}
        for p in popular_posts:
            for word in (p.get("text") or "").split():
                if word.startswith("#") and len(word) > 1:
                    clean_tag = word.strip(".,!?").lower()
                    tags_count[clean_tag] = tags_count.get(clean_tag, 0) + 1
        trending_tags = sorted(tags_count.items(), key=lambda x: x, reverse=True)[:10]
        
        u_res = supabase.table("profiles").select("username, first_name, last_name, avatar_url, bio, last_seen").limit(20).execute()
        users = []
        now_utc = datetime.now(timezone.utc)
        for u in (u_res.data or []):
            if u["username"] == viewer:
                continue
            is_online = False
            if u.get("last_seen"):
                try:
                    ls = datetime.fromisoformat(u["last_seen"].replace("Z", "+00:00"))
                    if (now_utc - ls).total_seconds() < 300:
                        is_online = True
                except:
                    pass
            u["is_online"] = is_online
            users.append(u)
            
        return {"status": "success", "popular_posts": popular_posts, "trending_tags": trending_tags, "recommended_users": users}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

from fastapi import Request
from fastapi.responses import JSONResponse

BANNED_KEYWORDS = [
    "политика", "митинг", "партия", "выборы", "госпереворот", "оппозиция", "революция", "экстремизм", "теракт",
    "сиёсат", "гирдиҳамоӣ", "инқилоб", "ҳизб", "ифротгароӣ", "террор",
    "politics", "protest", "coup", "election", "extremism", "terror",
    "порно", "секс", "эротика", "интим", "голая", "голый", "шлюха", "блядь", "хуй", "пизда", "ебать", "сука",
    "порнография", "фаҳш", "беҳаё", "фоҳиша", "ҷалаб", "кер", "кун",
    "porn", "xxx", "nsfw", "nude", "sex", "fuck", "bitch", "whore",
    "казино", "ставки", "1xbet", "букмекер", "наркотик", "героин", "мефедрон", "закладки", "қимор", "маводи мухаддир", "casino", "drugs"
]

def is_text_clean(text: str) -> bool:
    if not text:
        return True
    low = text.lower()
    for word in BANNED_KEYWORDS:
        if word in low:
            return False
    return True

@app.middleware("http")
async def nabz_content_shield(request: Request, call_next):
    if request.method in ["POST", "PUT"]:
        c_type = request.headers.get("content-type", "")
        if "application/json" in c_type:
            body_bytes = await request.body()
            body_str = body_bytes.decode("utf-8", errors="ignore")
            if not is_text_clean(body_str):
                return JSONResponse(
                    status_code=400,
                    content={"detail": "🛡️ Щит безопасности NABZ: запрещены политика, 18+, оскорбления, казино и спам!"}
                )
    return await call_next(request)

@app.post("/posts/update_meta/{post_id}")
def update_post_meta(post_id: int, category: str = Form("💬 Общение"), subtitles: str = Form("")):
    try:
        supabase.table("posts").update({"category": category, "subtitles": subtitles}).eq("id", post_id).execute()
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/users/search")
def search_users(q: str = ""):
    try:
        query = supabase.table("profiles").select("username, first_name, last_name, avatar_url, cover_url, bio, is_private, is_banned, last_seen")
        if q.strip():
            clean_q = q.strip().lstrip("@")
            query = query.or_(f"username.ilike.%{clean_q}%,first_name.ilike.%{clean_q}%,last_name.ilike.%{clean_q}%")
        res = query.limit(20).execute()
        return {"status": "success", "users": res.data or []}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/posts/share_to_chat")
def share_post_to_chat(post_id: int = Form(...), sender: str = Form(...), recipient: str = Form(...)):
    try:
        rec = recipient.strip().lstrip("@")
        p_res = supabase.table("posts").select("username, text, media_urls").eq("id", post_id).execute()
        if not p_res.data:
            raise HTTPException(status_code=404, detail="Пост не найден")
        post = p_res.data[0]
        
        members_str = ",".join(sorted([sender, rec]))
        existing = supabase.table("chat_rooms").select("id").eq("is_group", False).eq("members", members_str).execute()
        now_date = datetime.now().strftime("%d.%m.%Y %H:%M")
        if existing.data:
            room_id = existing.data[0]["id"]
        else:
            r_ins = supabase.table("chat_rooms").insert({"name": "", "is_group": False, "members": members_str, "created_at": now_date}).execute()
            room_id = r_ins.data[0]["id"]
            
        share_text = f"📩 Пересланная запись от @{post['username']}:\n{post.get('text', '')}"
        first_media = post.get("media_urls", "").split(",")[0] if post.get("media_urls") else ""
        m_type = "video" if first_media.lower().endswith((".mp4", ".mov", ".avi", ".mkv")) else ("image" if first_media else "text")
        
        now_time = datetime.now().strftime("%H:%M")
        supabase.table("chat_messages").insert({
            "room_id": room_id,
            "sender_username": sender,
            "text": share_text,
            "media_url": first_media,
            "media_type": m_type,
            "is_read": False,
            "created_at": now_time
        }).execute()
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/posts/for_you/{username}")
def get_personalized_feed(username: str):
    try:
        likes_res = supabase.table("post_likes").select("post_id").eq("username", username).limit(30).execute()
        liked_ids = [x["post_id"] for x in (likes_res.data or [])]
        fav_categories = set()
        if liked_ids:
            lp_res = supabase.table("posts").select("category").in_("id", liked_ids).execute()
            for item in (lp_res.data or []):
                if item.get("category"):
                    fav_categories.add(item["category"])
                    
        all_res = supabase.table("posts").select("*").eq("is_draft", False).order("id", desc=True).limit(30).execute()
        all_posts = all_res.data or []
        
        if fav_categories:
            matched = [p for p in all_posts if p.get("category") in fav_categories]
            others = [p for p in all_posts if p.get("category") not in fav_categories]
            return {"status": "success", "posts": matched + others, "interests": list(fav_categories)}
        return {"status": "success", "posts": all_posts, "interests": []}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/admin/dashboard")
def admin_dashboard():
    try:
        u_cnt = len(supabase.table("profiles").select("id").execute().data or [])
        p_cnt = len(supabase.table("posts").select("id").execute().data or [])
        s_cnt = len(supabase.table("stories").select("id").execute().data or [])
        r_res = supabase.table("reports").select("*").order("id", desc=True).execute()
        u_res = supabase.table("profiles").select("username, first_name, last_name, is_banned").order("username").execute()
        return {
            "status": "success",
            "stats": {"users": u_cnt, "posts": p_cnt, "stories": s_cnt},
            "reports": r_res.data or [],
            "users": u_res.data or []
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/admin/ban_toggle/{target_username}")
def admin_ban_toggle(target_username: str):
    try:
        if target_username == "admin1":
            raise HTTPException(status_code=400, detail="Нельзя заблокировать главного администратора")
        res = supabase.table("profiles").select("is_banned").eq("username", target_username).execute()
        if not res.data:
            raise HTTPException(status_code=404, detail="Пользователь не найден")
        new_state = not bool(res.data[0].get("is_banned"))
        supabase.table("profiles").update({"is_banned": new_state}).eq("username", target_username).execute()
        return {"status": "success", "is_banned": new_state}
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

from fastapi.responses import FileResponse, HTMLResponse

@app.get("/Nabz.apk")
def direct_apk_file():
    if os.path.exists("Nabz.apk"):
        return FileResponse(
            path="Nabz.apk",
            filename="Nabz.apk",
            media_type="application/vnd.android.package-archive"
        )
    raise HTTPException(status_code=404, detail="Файл Nabz.apk не найден на сервере")

@app.get("/download", response_class=HTMLResponse)
def universal_download_page():
    return """
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Скачать NABZ — Социальная сеть</title>
        <link rel="manifest" href="data:application/manifest+json,{&quot;name&quot;:&quot;NABZ&quot;,&quot;short_name&quot;:&quot;NABZ&quot;,&quot;start_url&quot;:&quot;https://streamlit.app&quot;,&quot;display&quot;:&quot;standalone&quot;,&quot;background_color&quot;:&quot;%230E0E14&quot;,&quot;theme_color&quot;:&quot;%2300F2FE&quot;}">
        <style>
            body {
                margin: 0; padding: 20px; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background: linear-gradient(135deg, #0E0E14 0%, #1d1536 100%);
                color: #ffffff; display: flex; justify-content: center; align-items: center; min-height: 100vh;
            }
            .card {
                background: rgba(255, 255, 255, 0.06); border: 1px solid rgba(255, 255, 255, 0.15);
                border-radius: 24px; padding: 32px 24px; max-width: 420px; width: 100%; text-align: center;
                box-shadow: 0 20px 50px rgba(0, 0, 0, 0.5); backdrop-filter: blur(12px);
            }
            .logo {
                width: 84px; height: 84px; border-radius: 22px; margin: 0 auto 16px;
                background: linear-gradient(135deg, #9b51e0, #00f2fe);
                display: flex; align-items: center; justify-content: center;
                font-size: 36px; font-weight: 900; color: #fff; box-shadow: 0 8px 25px rgba(155, 81, 224, 0.5);
            }
            h1 { margin: 0 0 8px; font-size: 28px; letter-spacing: 1px; }
            p { color: #b8b8d0; font-size: 15px; margin: 0 0 24px; line-height: 1.5; }
            .btn {
                display: block; width: 100%; box-sizing: border-box; padding: 15px 20px; margin-bottom: 12px;
                border-radius: 14px; font-size: 16px; font-weight: 700; text-decoration: none;
                transition: transform 0.15s ease; cursor: pointer; border: none;
            }
            .btn:active { transform: scale(0.98); }
            .btn-android { background: linear-gradient(90deg, #00f2fe, #4facfe); color: #0E0E14; }
            .btn-web { background: rgba(255, 255, 255, 0.12); color: #ffffff; border: 1px solid rgba(255, 255, 255, 0.2); }
            .ios-box {
                display: none; background: rgba(155, 81, 224, 0.18); border: 1px solid #9b51e0;
                border-radius: 14px; padding: 14px; margin-bottom: 14px; font-size: 14px; text-align: left; line-height: 1.5;
            }
            .platforms { font-size: 12px; color: #8888a8; margin-top: 16px; }
        </style>
    </head>
    <body>
        <div class="card">
            <div class="logo">N</div>
            <h1>NABZ</h1>
            <p>Международная социальная сеть нового поколения. Установите приложение на любое устройство в один клик.</p>

            <a id="androidBtn" href="/Nabz.apk" download="Nabz.apk" class="btn btn-android">
                📲 Скачать для Android (APK)
            </a>

            <div id="iosBox" class="ios-box">
                <b>🍏 Установка на iPhone / iPad:</b><br>
                1. Нажмите кнопку <b>«Открыть NABZ»</b> ниже.<br>
                2. Внизу экрана нажмите значок <b>«Поделиться»</b> (квадрат со стрелкой вверх).<br>
                3. Выберите <b>«На экран „Домой“»</b> — иконка NABZ появится на рабочем столе.
            </div>

            <a href="https://streamlit.app" class="btn btn-web">
                🌐 Открыть / Установить на ПК и iPhone
            </a>

            <div class="platforms">
                Поддерживается: Android • iOS (iPhone) • Windows • macOS • Linux
            </div>
        </div>

        <script>
            const ua = navigator.userAgent || "";
            if (/iPhone|iPad|iPod/i.test(ua)) {
                document.getElementById("iosBox").style.display = "block";
                document.getElementById("androidBtn").style.display = "none";
            }
        </script>
    </body>
    </html>
    """