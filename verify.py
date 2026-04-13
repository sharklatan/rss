from bs4 import BeautifulSoup

with open('rss/9to5mac.xml', 'r', encoding='utf-8') as f:
    xml = f.read()

soup = BeautifulSoup(xml, 'html.parser')
items = soup.find_all('item')

print(f'Total items: {len(items)}')
print()

for idx, item in enumerate(items[:2], 1):
    title = item.find('title').get_text()
    desc = item.find('description').get_text()
    
    print(f'Artículo {idx}:')
    print(f'  Título: {title[:70]}...')
    print(f'  Descripción (primeros 100 chars): {desc[:100]}...')
    print(f'  Tamaño descripción: {len(desc)} chars')
    has_html = '<' in desc or '>' in desc
    print(f'  ¿Tiene HTML tags?: {has_html}')
    print()
