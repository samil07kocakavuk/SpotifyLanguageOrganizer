from dotenv import load_dotenv
import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import requests
from bs4 import BeautifulSoup
from langdetect import detect
import time

# .env dosyasını yükle
load_dotenv()

# API bilgilerini .env'den oku
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI")
USERNAME = os.getenv("USERNAME")
GENIUS_API_TOKEN = os.getenv("GENIUS_API_TOKEN")
PLAYLIST_ID = os.getenv("PLAYLIST_ID")

scope = "playlist-modify-public playlist-modify-private playlist-read-private"

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    redirect_uri=REDIRECT_URI,
    scope=scope,
    username=USERNAME
))

def get_genius_lyrics(song_title, artist_name):
    base_url = "https://api.genius.com"
    headers = {'Authorization': 'Bearer ' + GENIUS_API_TOKEN}
    search_url = base_url + "/search"
    data = {'q': f"{song_title} {artist_name}"}

    response = requests.get(search_url, headers=headers, params=data)
    if response.status_code != 200:
        print(f"Genius API hata: {response.status_code} - {song_title} - {artist_name}")
        return None

    json_resp = response.json()
    hits = json_resp['response']['hits']
    if not hits:
        print(f"Şarkı bulunamadı Genius'ta: {song_title} - {artist_name}")
        return None

    song_path = hits[0]['result']['path']
    lyrics_url = "https://genius.com" + song_path

    page = requests.get(lyrics_url)
    if page.status_code != 200:
        print(f"Lyrics sayfası açılmadı: {lyrics_url}")
        return None

    html = BeautifulSoup(page.text, "html.parser")

    lyrics_div = html.find("div", class_="lyrics")
    if lyrics_div:
        return lyrics_div.get_text(strip=True)

    lyrics_div = html.find("div", class_="Lyrics__Root-sc-1ynbvzw-0")
    if lyrics_div:
        return lyrics_div.get_text(separator="\n", strip=True)

    print(f"Şarkı sözü bulunamadı sayfada: {song_title} - {artist_name}")
    return None

def delete_language_playlists():
    playlists = sp.current_user_playlists(limit=50)
    for pl in playlists['items']:
        if pl['name'].startswith("📚"):
            yanit = input(f"'{pl['name']}' adlı listeyi silmek istiyor musun? (y/n): ").lower()
            if yanit == 'y':
                print(f"Siliniyor: {pl['name']}")
                try:
                    sp.current_user_unfollow_playlist(pl['id'])
                except Exception as e:
                    print(f"Silme hatası: {e}")
            else:
                print(f"Atlandı: {pl['name']}")

def get_or_create_playlist(language_name):
    playlists = sp.current_user_playlists(limit=50)
    for pl in playlists['items']:
        if pl['name'] == f"📚 {language_name}":
            return pl['id']
    try:
        new_pl = sp.user_playlist_create(USERNAME, f"📚 {language_name}", public=False)
        print(f"Yeni liste oluşturuldu: 📚 {language_name}")
        return new_pl['id']
    except Exception as e:
        print(f"Playlist oluşturma hatası: {e}")
        return None

def get_all_playlist_tracks(sp, playlist_id):
    tracks = []
    limit = 100
    offset = 0

    while True:
        results = sp.playlist_items(playlist_id, limit=limit, offset=offset)
        items = results['items']
        if not items:
            break
        tracks.extend(items)
        offset += limit
        print(f"{offset} şarkı çekildi...")
    return tracks

def main():
    print("Önceki dil listeleri siliniyor...")
    delete_language_playlists()

    print("Playlist şarkıları çekiliyor...")
    tracks = get_all_playlist_tracks(sp, PLAYLIST_ID)

    print(f"Toplam şarkı sayısı: {len(tracks)}")

    language_buckets = {}

    for index, item in enumerate(tracks):
        try:
            track = item['track']
            title = track['name']
            artist = track['artists'][0]['name']

            print(f"{index+1}. İşleniyor: {title} - {artist}")

            lyrics = get_genius_lyrics(title, artist)
            if lyrics:
                try:
                    lang = detect(lyrics)
                    print(f"Bulunan dil: {lang}")
                except Exception as e:
                    lang = "unknown"
                    print(f"Dil tespiti yapılamadı: {e}")
            else:
                try:
                    lang = detect(title + " " + artist)
                    print(f"Şarkı sözü yok, isimden bulunan dil: {lang}")
                except Exception as e:
                    lang = "unknown"
                    print(f"İsimden dil tespiti yapılamadı: {e}")

            if lang not in language_buckets:
                language_buckets[lang] = []
            language_buckets[lang].append(track['uri'])

            print(f"'{title}' şarkısı '{lang}' listesine eklendi.")
            print(f"{index+1}. şarkı başarıyla işlendi.")

            time.sleep(1)

        except Exception as e:
            print(f"{index+1}. şarkıda hata: {e}")

    # Şarkıları dil listelerine ekle
    for lang, uris in language_buckets.items():
        pl_id = get_or_create_playlist(lang)
        if pl_id is None:
            print(f"{lang} listesi oluşturulamadı, şarkılar eklenemedi.")
            continue
        for i in range(0, len(uris), 100):
            try:
                sp.playlist_add_items(pl_id, uris[i:i+100])
                print(f"{lang} listesine {len(uris[i:i+100])} şarkı eklendi.")
            except Exception as e:
                print(f"Şarkı ekleme hatası: {e}")
            time.sleep(2)

if __name__ == "__main__":
    main()