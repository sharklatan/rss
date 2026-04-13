from bs4 import BeautifulSoup

with open('rss/9to5mac.xml', 'r', encoding='utf-8') as f:
    xml = f.read()

soup = BeautifulSoup(xml, 'html.parser')
items = soup.find_all('item')
desc = items[2].find('description').get_text()
desc_formatted = desc.replace('&#10;', '\n')

# Buscar dónde está "Haz más"
idx = desc_formatted.lower().find('haz más')
if idx > 0:
    print("Contexto alrededor de 'Haz más':")
    print(repr(desc_formatted[max(0, idx-50):idx+150]))
