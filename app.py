from flask import Flask, request, render_template_string
import requests
import json
from datetime import datetime

app = Flask(__name__)

UA = (
    "Mozilla/5.0 (Linux; Android 14; Mobile) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/136.0.0.0 Mobile Safari/537.36"
)

HTML = r"""
<!DOCTYPE html>
<html lang="tr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">

<title>TikTok Public Checker</title>

<style>
*{box-sizing:border-box}

body{
    margin:0;
    min-height:100vh;
    background:#08080a;
    color:#fff;
    font-family:Arial,sans-serif;
}

.container{
    width:min(680px,94%);
    margin:40px auto;
}

h1{
    text-align:center;
    margin-bottom:8px;
}

.sub{
    text-align:center;
    color:#999;
    margin-bottom:28px;
}

.search{
    display:flex;
    gap:10px;
}

input{
    flex:1;
    padding:16px;
    border-radius:12px;
    border:1px solid #333;
    background:#151519;
    color:white;
    font-size:16px;
    outline:none;
}

button{
    padding:0 22px;
    border:0;
    border-radius:12px;
    background:#fff;
    color:#000;
    font-weight:bold;
    cursor:pointer;
}

.card{
    margin-top:18px;
    padding:22px;
    border-radius:18px;
    background:#151519;
    border:1px solid #29292e;
}

.title{
    font-size:20px;
    font-weight:bold;
    margin-bottom:18px;
}

.row{
    display:flex;
    justify-content:space-between;
    gap:20px;
    padding:12px 0;
    border-bottom:1px solid #29292e;
}

.row:last-child{
    border-bottom:0;
}

.label{
    color:#999;
}

.value{
    text-align:right;
    word-break:break-word;
}

.bio{
    background:#0b0b0e;
    padding:15px;
    border-radius:12px;
    line-height:1.5;
}

.error{
    margin-top:18px;
    padding:15px;
    border-radius:12px;
    background:#321414;
    color:#ffb0b0;
}

.video{
    display:block;
    margin-top:10px;
    padding:14px;
    border-radius:12px;
    background:#0b0b0e;
    color:white;
    text-decoration:none;
    word-break:break-all;
}

.small{
    color:#888;
    font-size:13px;
}
</style>
</head>

<body>

<div class="container">

<h1>🎵 TikTok Public Checker</h1>
<div class="sub">Sadece public profil bilgileri</div>

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
<div class="error">❌ {{ error }}</div>
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

{% if create %}
<div class="row">
<span class="label">Hesap tarihi</span>
<span class="value">{{ create }}</span>
</div>
{% endif %}

{% if nick_edit %}
<div class="row">
<span class="label">Nick değişimi</span>
<span class="value">{{ nick_edit }}</span>
</div>
{% endif %}

{% if language %}
<div class="row">
<span class="label">Dil</span>
<span class="value">{{ language }}</span>
</div>
{% endif %}

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
<span class="value">{{ stats.followerCount }}</span>
</div>

<div class="row">
<span class="label">➡️ Takip edilen</span>
<span class="value">{{ stats.followingCount }}</span>
</div>

<div class="row">
<span class="label">❤️ Beğeni</span>
<span class="value">{{ stats.heartCount }}</span>
</div>

<div class="row">
<span class="label">🎬 Video</span>
<span class="value">{{ stats.videoCount }}</span>
</div>

<div class="row">
<span class="label">🤝 Arkadaş</span>
<span class="value">{{ stats.friendCount }}</span>
</div>

</div>


<div class="card">

<div class="title">🆔 TikTok ID</div>

<div class="bio">{{ user.id }}</div>

</div>


<div class="card">

<div class="title">🔐 TikTok SecUID</div>

<div class="bio">{{ user.secUid }}</div>

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
<span class="small">{{ video }}</span>
</a>

{% endfor %}

</div>

{% endif %}

{% endif %}

</div>

</body>
</html>
"""


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
    except:
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
        return json.loads(
            html[start + 1:end].strip()
        )
    except:
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

    except:
        return {}, {}, []


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

                elif response.status_code != 200:

                    error = (
                        "TikTok isteği başarısız. "
                        f"HTTP {response.status_code}"
                    )

                else:

                    data = get_data(response.text)

                    if not data:

                        error = (
                            "TikTok public verisi "
                            "bulunamadı."
                        )

                    else:

                        user, stats, items = \
                            get_profile(data)

                        if not user:

                            error = (
                                "Profil bilgileri "
                                "bulunamadı."
                            )

                        else:

                            create = tarih(
                                user.get("createTime")
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

                                video_id = item.get("id")

                                if video_id:

                                    videos.append(
                                        f"https://www.tiktok.com/"
                                        f"@{username}/video/"
                                        f"{video_id}"
                                    )

            except requests.RequestException:

                error = (
                    "TikTok'a bağlanırken "
                    "bağlantı hatası oluştu."
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

    print("=" * 55)
    print("       TIKTOK PUBLIC CHECKER")
    print("=" * 55)
    print()
    print("Tarayıcıdan aç:")
    print("http://127.0.0.1:5000")
    print()

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False
    )
