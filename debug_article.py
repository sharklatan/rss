from bs4 import BeautifulSoup
import urllib.request

url = "https://9to5mac.com/2026/04/13/apple-releases-ios-26-5-beta-2-for-iphone/"
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
req = urllib.request.Request(url, headers=headers)
html = urllib.request.urlopen(req).read().decode('utf8', errors='ignore')
soup = BeautifulSoup(html, 'html.parser')

content = soup.select_one('div.post-content')
if content:
    # Buscar qué párrafo tiene "Haz más" o "Make more"
    for p in content.find_all('p'):
        text = p.get_text()
        if 'haz más' in text.lower() or 'make more' in text.lower():
            print("ENCONTRADO:")
            print(text)
            print("\n---\n")
            break
    
    # Ver los últimos párrafos del artículo
    print("\nÚltimos 5 párrafos del artículo:")
    all_p = content.find_all('p')
    for p in all_p[-5:]:
        text = p.get_text(strip=True)
        if text:
            print(f"- {text[:100]}...")
