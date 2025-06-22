import discord
import yt_dlp
import os
import tempfile
import asyncio

TOKEN = os.getenv("TOKEN")
COOKIES_PATH = "/etc/secrets/cookies.txt"  

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'🤖 Bot logado como {client.user}!')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('!baixar'):
        partes = message.content.split()
        if len(partes) < 2:
            await message.channel.send("Uso: `!baixar <link> [mp3|mp4]`")
            return

        url = partes[1]
        formato = partes[2] if len(partes) > 2 else 'mp3'

        await message.channel.send(f'🎧 Baixando `{formato}` de:\n{url}')

        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                outtmpl = os.path.join(tmpdir, '%(title)s.%(ext)s')

                # Copiar cookies para um arquivo temporário
                cookie_tmp_path = os.path.join(tmpdir, "cookies.txt")
                with open(COOKIES_PATH, "r") as f_in, open(cookie_tmp_path, "w") as f_out:
                    f_out.write(f_in.read())

                ydl_opts = {
                    'noplaylist': True,
                    'format': 'bestaudio/best' if formato == 'mp3' else 'bestvideo+bestaudio/best',
                    'outtmpl': outtmpl,
                    'cookiefile': cookie_tmp_path,
                    'quiet': True,
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': formato,
                        'preferredquality': '192',
                    }] if formato == 'mp3' else []
                }

                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    loop = asyncio.get_event_loop()
                    info = await loop.run_in_executor(None, lambda: ydl.extract_info(url, download=True))
                    filename = ydl.prepare_filename(info)
                    if formato == 'mp3':
                        filename = filename.rsplit('.', 1)[0] + f".{formato}"

                if os.path.getsize(filename) > 8 * 1024 * 1024:
                    await message.channel.send("⚠️ O arquivo é muito grande pro Discord (8MB).")
                else:
                    await message.channel.send(file=discord.File(filename))

        except Exception as e:
            await message.channel.send(f'❌ Erro: `{str(e)}`')

client.run(TOKEN)
