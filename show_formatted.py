from bs4 import BeautifulSoup

with open('rss/9to5mac.xml', 'r', encoding='utf-8') as f:
    xml = f.read()

soup = BeautifulSoup(xml, 'html.parser')
items = soup.find_all('item')

print("=" * 80)
print(f"ARTÍCULO 3: {items[2].find('title').get_text()[:60]}...")
print("=" * 80)

desc = items[2].find('description').get_text()
# Convertir &#10; de vuelta a verdaderos saltos de línea para mostrar
desc_formatted = desc.replace('&#10;', '\n')
print(desc_formatted[:1500])
