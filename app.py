import requests
from bs4 import BeautifulSoup
from collections import deque
import time
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Fungsi untuk mendapatkan semua link href dari halaman
def get_links(url, use_english):
    links = []
    try:
        if use_english:
            url = url.replace("https://www.ui.ac.id", "https://www.ui.ac.id/en")
        response = requests.get(url, timeout=10)
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
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            page_text = soup.get_text().lower()  # Mengambil teks dari halaman
            return keyword.lower() in page_text  # Memeriksa apakah kata kunci ada dalam teks
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
    return False

# Fungsi BFS untuk menemukan semua link dengan batas kedalaman
def bfs(start_url, max_depth, keyword="", use_english=False, progress_callback=None):
    visited = set()  # Set untuk menyimpan URL yang sudah dikunjungi
    queue = deque([(start_url, 0, [])])  # Antrian untuk BFS (URL, kedalaman, path yang dilalui)
    all_links = set()  # Set untuk menyimpan semua link yang ditemukan
    keyword_found_urls = set()  # Set untuk menyimpan URL yang mengandung kata kunci
    search_log = []  # Untuk menyimpan log pencarian

    visited_count = 0
    
    while queue:
        current_url, depth, path = queue.popleft()
        
        # Jika max_depth adalah -1, berarti kedalaman tidak terbatas
        if max_depth != -1 and depth > max_depth:
            continue
        
        if current_url not in visited:
            visited.add(current_url)
            visited_count += 1
            log_entry = f"Visiting (Depth {depth}): {current_url}"
            search_log.append(log_entry)
            print(log_entry)
            
            # Update progress jika callback diberikan
            if progress_callback:
                progress_callback({
                    'status': 'searching',
                    'url': current_url,
                    'depth': depth,
                    'visited_count': visited_count,
                    'log': log_entry
                })
            
            # Mencari kata kunci di halaman
            if keyword and search_keyword_in_page(current_url, keyword, use_english):
                log_entry = f"Keyword found at: {current_url}"
                search_log.append(log_entry)
                print(log_entry)
                keyword_found_urls.add(current_url)
                # Mencetak path menuju URL yang mengandung kata kunci
                path_log = f"Path to the keyword: {' -> '.join(path + [current_url])}"
                search_log.append(path_log)
                print(path_log)
                
                if progress_callback:
                    progress_callback({
                        'status': 'found',
                        'url': current_url,
                        'path': path + [current_url],
                        'log': log_entry
                    })
                
                if not keyword:  # Jika tidak mencari kata kunci, kita teruskan pencarian
                    continue

            links = get_links(current_url, use_english)  # Mendapatkan semua link dari halaman
            all_links.update(links)  # Menambahkan link baru ke set all_links
            
            # Tambahkan link yang belum dikunjungi ke dalam antrian
            for link in links:
                if link not in visited:
                    queue.append((link, depth + 1, path + [current_url]))

            # Agar tidak terlalu cepat mengirim permintaan
            time.sleep(0.5)  # Sleep untuk menghindari terlalu banyak permintaan ke server
    
    if progress_callback:
        progress_callback({
            'status': 'complete',
            'visited_count': visited_count,
            'all_links_count': len(all_links),
            'keyword_found_count': len(keyword_found_urls)
        })
        
    return all_links, keyword_found_urls, search_log

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    data = request.json
    start_url = data.get('start_url', 'https://www.ui.ac.id')
    max_depth = int(data.get('max_depth', -1))
    keyword = data.get('keyword', '')
    use_english = data.get('use_english', False)
    
    all_links, keyword_found_urls, search_log = bfs(
        start_url, 
        max_depth, 
        keyword, 
        use_english
    )
    
    return jsonify({
        'all_links': list(all_links),
        'keyword_found_urls': list(keyword_found_urls),
        'search_log': search_log
    })

if __name__ == '__main__':
    app.run(debug=True)
