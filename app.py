from flask import Flask, request, render_template_string
import requests
import json
import os
from datetime import datetime

app = Flask(__name__)

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

UA = (
    "Mozilla/5.0 (Linux; Android 14; Mobile) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/136.0.0.0 Mobile Safari/537.36"
)


def telegram_gonder(mesaj):
    if not BOT_TOKEN or not CHAT_ID:
        return

    try:
        requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            data={
                "chat_id": CHAT_ID,
                "text": mesaj
            },
            timeout=10
        )
    except Exception:
        pass


def tarih(timestamp):
    if not timestamp:
        return None

    try:
        timestamp = int(timestamp)

        if timestamp > 100000000000:
            timestamp //= 1000

        return datetime.fromtimestamp(timestamp).strftime(
            "%d.%m.%Y %H:%M:%S"
        )
    except Exception:
        return None


def get_data(html):
    marker = "__UNIVERSAL_DATA_FOR_REHYDRATION__"
    pos = html.find(marker)

    if pos == -1:
        return None

    start = html.find(">", pos)

    if start == -1:
        return None

    end = html.find("</script>", start)

    if end == -1:
        return None

    try:
        return json.loads(html[start + 1:end].strip())
    except Exception:
        return None


def get_profile(data):
    try:
        detail = data[
            "__DEFAULT_SCOPE__"
        ]["webapp.user-detail"]

        info = detail["userInfo"]

        user = info.get("user", {})
        stats = info.get("stats", {})
        items = detail.get("itemList", [])

        return user, stats, items

    except Exception:
        return {}, {}, []


HTML = """
<!DOCTYPE html>
<html lang="tr">

<head>

<meta charset="UTF-8">

<meta name="viewport"
content="width=device-width,initial-scale=1">

<title>TikTok Public Checker</title>

<style>

* {
    box-sizing: border-box;
}

body {
    margin: 0;
    min-height: 100vh;
    background: #08080a;
    color: white;
    font-family: Arial, sans-serif;
}

.container {
    width: min(680px, 94%);
    margin: 40px auto;
}

h1 {
    text-align: center;
}

.subtitle {
    text-align: center;
    color: #999;
    margin-bottom: 25px;
}

.search {
    display: flex;
    gap: 10px;
}

input {
    flex: 1;
    padding: 15px;
    border-radius: 12px;
    border: 1px solid #333;
    background: #151519;
    color: white;
    font-size: 16px;
}

button {
    border: 0;
    border-radius: 12px;
    padding: 0 22px;
    font-weight: bold;
    cursor: pointer;
}

.card {
    margin-top: 18px;
    padding: 20px;
    background: #151519;
    border: 1px solid #29292e;
    border-radius: 18px;
}

.title {
    font-size: 20px;
    font-weight: bold;
    margin-bottom: 15px;
}

.row {
    display: flex;
    justify-content: space-between;
    gap: 15px;
    padding: 12px 0;
    border-bottom: 1px solid #29292e;
}

.label {
    color: #999;
}

.value {
    text-align: right;
    word-break: break-word;
}

.bio {
    background: #0b0b0e;
    padding: 15px;
    border-radius: 12px;
    margin-top: 12px;
}

.error {
    margin-top: 18px;
    padding: 15px;
    border-radius: 12px;
    background: #321414;
}

.video {
    display: block;
    color: white;
    text-decoration: none;
    background: #0b0b0e;
    padding: 14px;
    border-radius: 12px;
    margin-top: 10px;
    word-break: break-all;
}

</style>

</head>

<body>

<div class="container">

<h1>🎵 TikTok Public Checker</h1>

<div class="subtitle">
Sadece public TikTok verileri
</div>

<form class="search" method="POST">

<input
name="username"
placeholder="@kullanıcı adı"
value="{{ username }}"
autocomplete="off"
>

<button type="submit">ARA</button>

</form>


{% if error %}

<div class="error">
❌ {{ error }}
</div>

{% endif %}


{% if user %}

<div class="card">

<div class="title">👤 Profil</div>

<div class="row">
<span class="label">Kullanıcı adı</span>
<span class="value">@{{ user.uniqueId }}</span>
</div>

<div class="row">
<span class="label">Görünen ad</span>
<span class="value">{{ user.nickname }}</span>
</div>

{% if user.signature %}

<div class="bio">
📝 {{ user.signature }}
</div>

{% endif %}

</div>


<div class="card">

<div class="title">📅 Hesap</div>

<div class="row">
<span class="label">Hesap tarihi</span>
<span class="value">{{ create or "Bulunamadı" }}</span>
</div>

<div class="row">
<span class="label">Nick değişimi</span>
<span class="value">{{ nick_edit or "Bulunamadı" }}</span>
</div>

<div class="row">
<span class="label">Dil</span>
<span class="value">{{ language or "Bulunamadı" }}</span>
</div>

<div class="row">
<span class="label">Doğrulanmış</span>
<span class="value">
{{ "Evet" if user.verified else "Hayır" }}
</span>
</div>

<div class="row">
<span class="label">Gizli hesap</span>
<span class="value">
{{ "Evet" if user.privateAccount else "Hayır" }}
</span>
</div>

</div>


<div class="card">

<div class="title">📊 İstatistikler</div>

<div class="row">
<span class="label">👥 Takipçi</span>
<span class="value">{{ stats.get("followerCount", 0) }}</span>
</div>

<div class="row">
<span class="label">➡️ Takip edilen</span>
<span class="value">{{ stats.get("followingCount", 0) }}</span>
</div>

<div class="row">
<span class="label">❤️ Beğeni</span>
<span class="value">{{ stats.get("heartCount", 0) }}</span>
</div>

<div class="row">
<span class="label">🎬 Video</span>
<span class="value">{{ stats.get("videoCount", 0) }}</span>
</div>

<div class="row">
<span class="label">🤝 Arkadaş</span>
<span class="value">{{ stats.get("friendCount", 0) }}</span>
</div>

</div>


<div class="card">

<div class="title">🆔 TikTok ID</div>

<div class="bio">
{{ user.id }}
</div>

</div>


<div class="card">

<div class="title">🔐 TikTok SecUID</div>

<div class="bio">
{{ user.secUid }}
</div>

</div>


{% if videos %}

<div class="card">

<div class="title">🎬 Public Videolar</div>

{% for video in videos %}

<a
class="video"
href="{{ video }}"
target="_blank"
>
URL {{ loop.index }}<br>
{{ video }}
</a>

{% endfor %}

</div>

{% endif %}

{% endif %}

</div>

</body>
</html>
"""


@app.route("/", methods=["GET", "POST"])
def index():

    username = ""
    user = None
    stats = {}
    videos = []
    error = None
    create = None
    nick_edit = None
    language = None

    now = datetime.now().strftime(
        "%d.%m.%Y %H:%M:%S"
    )

    # Ziyaret bildirimi
    if request.method == "GET":

        telegram_gonder(
            "🔔 YENİ ZİYARET\n\n"
            f"🕐 Zaman: {now}\n"
            f"📡 İstek: GET\n"
            f"📄 Sayfa: {request.path}\n"
            "📊 HTTP: 200\n"
            f"📱 User-Agent: "
            f"{request.headers.get('User-Agent', '-')}\n"
            f"🌐 Dil: "
            f"{request.headers.get('Accept-Language', '-')}\n"
            f"🔗 Referrer: "
            f"{request.headers.get('Referer', '-')}"
        )

    if request.method == "POST":

        username = request.form.get(
            "username", ""
        ).strip().lstrip("@")

        if not username:

            error = "Kullanıcı adı gir."

        else:

            url = f"https://www.tiktok.com/@{username}"

            try:

                response = requests.get(
                    url,
                    headers={
                        "User-Agent": UA,
                        "Accept-Language":
                            "tr-TR,tr;q=0.9,en;q=0.8"
                    },
                    timeout=30
                )

                if response.status_code == 404:

                    error = "Kullanıcı bulunamadı."

                    telegram_gonder(
                        "🔎 TIKTOK ARAMASI\n\n"
                        f"👤 Kullanıcı: @{username}\n"
                        "❌ Sonuç: Bulunamadı"
                    )

                elif response.status_code != 200:

                    error = (
                        f"TikTok HTTP "
                        f"{response.status_code}"
                    )

                    telegram_gonder(
                        "🔎 TIKTOK ARAMASI\n\n"
                        f"👤 Kullanıcı: @{username}\n"
                        f"❌ HTTP: "
                        f"{response.status_code}"
                    )

                else:

                    data = get_data(
                        response.text
                    )

                    if not data:

                        error = (
                            "Public profil verisi "
                            "bulunamadı."
                        )

                    else:

                        user, stats, items = \
                            get_profile(data)

                        if not user:

                            error = (
                                "Profil bulunamadı."
                            )

                        else:

                            create = tarih(
                                user.get(
                                    "createTime"
                                )
                            )

                            nick_edit = tarih(
                                user.get(
                                    "nickNameModifyTime"
                                )
                            )

                            language = user.get(
                                "language"
                            )

                            for item in items:

                                video_id = item.get(
                                    "id"
                                )

                                if video_id:

                                    videos.append(
                                        "https://www.tiktok.com/"
                                        f"@{username}/video/"
                                        f"{video_id}"
                                    )

                            telegram_gonder(
                                "🔎 TIKTOK ARAMASI\n\n"
                                f"👤 Kullanıcı: "
                                f"@{username}\n"
                                "✅ Sonuç: Bulundu\n"
                                f"🎬 Video: "
                                f"{len(videos)}\n"
                                f"🕐 Zaman: {now}"
                            )

            except Exception as e:

                error = (
                    "Bağlantı sırasında hata "
                    "oluştu."
                )

                telegram_gonder(
                    "⚠️ TIKTOK ARAMA HATASI\n\n"
                    f"👤 Kullanıcı: @{username}\n"
                    f"❌ Hata: {str(e)[:200]}"
                )

    return render_template_string(
        HTML,
        username=username,
        user=user,
        stats=stats,
        videos=videos,
        error=error,
        create=create,
        nick_edit=nick_edit,
        language=language
    )


if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False
                            )
