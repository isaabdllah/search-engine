# ie algo awal hungkul teu dipake


import requests
from bs4 import BeautifulSoup
from collections import deque
import time

# Fungsi untuk mendapatkan semua link href dari halaman
def get_links(url, use_english):
    links = []
    try:
        if use_english:
            url = url.replace("https://www.ui.ac.id", "https://www.ui.ac.id/en")
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            links = [a['href'] for a in soup.find_all('a', href=True) if 'ui.ac.id' in a['href']]
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
    return links

# Fungsi untuk mencari kata kunci di halaman
def search_keyword_in_page(url, keyword, use_english):
    try:
        if use_english:
            url = url.replace("https://www.ui.ac.id", "https://www.ui.ac.id/en")
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            page_text = soup.get_text().lower()  # Mengambil teks dari halaman
            return keyword.lower() in page_text  # Memeriksa apakah kata kunci ada dalam teks
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
    return False

# Fungsi BFS untuk menemukan semua link dengan batas kedalaman
def bfs(start_url, max_depth, keyword="", use_english=False):
    visited = set()  # Set untuk menyimpan URL yang sudah dikunjungi
    queue = deque([(start_url, 0, [])])  # Antrian untuk BFS (URL, kedalaman, path yang dilalui)
    all_links = set()  # Set untuk menyimpan semua link yang ditemukan
    keyword_found_urls = set()  # Set untuk menyimpan URL yang mengandung kata kunci

    while queue:
        current_url, depth, path = queue.popleft()
        
        # Jika max_depth adalah -1, berarti kedalaman tidak terbatas
        if max_depth != -1 and depth > max_depth:
            continue
        
        if current_url not in visited:
            visited.add(current_url)
            print(f"Visiting (Depth {depth}): {current_url}")
            
            # Mencari kata kunci di halaman
            if search_keyword_in_page(current_url, keyword, use_english):
                print(f"Keyword found at: {current_url}")
                keyword_found_urls.add(current_url)
                # Mencetak path menuju URL yang mengandung kata kunci
                print(f"Path to the keyword: {' -> '.join(path + [current_url])}")
                return all_links, keyword_found_urls

            links = get_links(current_url, use_english)  # Mendapatkan semua link dari halaman
            all_links.update(links)  # Menambahkan link baru ke set all_links
            
            # Tambahkan link yang belum dikunjungi ke dalam antrian
            for link in links:
                if link not in visited:
                    queue.append((link, depth + 1, path + [current_url]))

            # Agar tidak terlalu cepat mengirim permintaan
            time.sleep(1)  # Sleep 1 detik untuk menghindari terlalu banyak permintaan ke server
    
    return all_links, keyword_found_urls

# URL awal untuk BFS
start_url = 'https://www.ui.ac.id'

# Kata kunci yang ingin dicari
keyword = input("Enter the keyword to search for: ")

# Input untuk kedalaman
max_depth_input = input("Enter max depth (enter -1 for unlimited depth): ")
max_depth = int(max_depth_input) if max_depth_input.isdigit() or max_depth_input == '-1' else -1

# Input untuk memilih bahasa
use_english_input = input("Do you want to use the English version of the site? (True/False): ")
use_english = use_english_input.lower() == 'true'

# Mulai pencarian BFS dengan batas kedalaman yang ditentukan
found_links, keyword_found_urls = bfs(start_url, max_depth=max_depth, keyword=keyword, use_english=use_english)

# Menampilkan semua link yang ditemukan
print("\nAll found links:")
for link in found_links:
    print(link)

# Menampilkan URL yang mengandung kata kunci
print("\nURLs that contain the keyword:")
for url in keyword_found_urls:
    print(url)
