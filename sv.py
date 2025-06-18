#!/usr/bin/env python3
import os

# Klasör ve dosya yolu
devc = ".devcontainer"
os.makedirs(devc, exist_ok=True)

# Dockerfile içeriği
docker = f"""\
FROM mcr.microsoft.com/devcontainers/base:ubuntu

RUN apt-get update \\
 && apt-get install -y openjdk-21-jre-headless python3 python3-pip curl gpg \\
 && pip3 install requests

RUN curl -SsL https://playit-cloud.github.io/ppa/key.gpg \\
  | gpg --dearmor \\
  | tee /etc/apt/trusted.gpg.d/playit.gpg >/dev/null \\
 && echo "deb [signed-by=/etc/apt/trusted.gpg.d/playit.gpg] https://playit-cloud.github.io/ppa/data ./" \\
  | tee /etc/apt/sources.list.d/playit-cloud.list \\
 && apt-get update \\
 && apt-get install -y playit

WORKDIR /workspace
COPY download_and_run.py .
ENTRYPOINT ["bash","-lc","./download_and_run.py"]
"""
open(os.path.join(devc, "Dockerfile"), "w").write(docker)

# devcontainer.json içeriği
devjson = """\
{
  "name": "MC Paper + Playit",
  "build": { "dockerfile": "Dockerfile" },
  "forwardPorts": [25565],
  "postCreateCommand": "chmod +x download_and_run.py",
  "customizations": {
    "vscode": { "extensions": ["ms-python.python"] }
  }
}
"""
open(os.path.join(devc, "devcontainer.json"), "w").write(devjson)

# download_and_run.py içeriği
script = """#!/usr/bin/env python3
import requests, subprocess, os

# Kullanıcıdan sürüm girişi
vers = input("Paper sürümü (örnek 1.21.4): ")
URL = f"https://qing762.is-a.dev/api/papermc/projects/paper/versions/{vers}"
data = requests.get(URL).json()
jar_url = data["url"]

dst = os.path.join(os.getcwd(), "minecraft")
os.makedirs(dst, exist_ok=True)
jar_path = os.path.join(dst, "paper.jar")
print("İndiriliyor:", jar_url)
r = requests.get(jar_url, stream=True)
with open(jar_path, "wb") as f:
    for c in r.iter_content(8192): f.write(c)

eula = os.path.join(dst, "eula.txt")
if not os.path.exists(eula):
    open(eula, "w").write("eula=true\\n")
    print("EULA oluşturuldu.")

print("\\n## playit.gg kurulumu ##")
subprocess.run(["sudo","systemctl","start","playit"], check=True)
subprocess.run(["sudo","systemctl","enable","playit"], check=True)
subprocess.run(["playit","setup"], check=True)
print("playit.gg tünelin hazır!")

os.chdir(dst)
print("\\nMinecraft sunucusu başlatılıyor…")
subprocess.run(["java","-Xms1G","-Xmx2G","-jar","paper.jar","nogui"])
"""
open("download_and_run.py","w").write(script)
os.chmod("download_and_run.py", 0o755)

print("🎉 Tüm dosyalar oluşturuldu!")
print("Sonraki adımlar:")
print("1. VS Code’u aç ve 'Reopen in Container' tuşuna bas veya 'Codespaces'da aç.")
print("2. Codespace ortamı kurulur kurulmaz, konsolda script çalışacak, sürüm sorulacak, indirilecek, playit çalışacak ve sunucu başlayacak.")
