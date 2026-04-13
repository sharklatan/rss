from bs4 import BeautifulSoup

with open('rss/9to5mac.xml', 'r', encoding='utf-8') as f:
    xml = f.read()

soup = BeautifulSoup(xml, 'html.parser')
item = soup.find('item')
desc = item.find('description').get_text()

print('Primeros 1000 caracteres de la descripción:')
print(desc[:1000])
print()
print('---')
print()
print('Verificando estructura:')
print(f'Cantidad de saltos de línea: {desc.count(chr(10))}')
print(f'Tiene párrafos dobles?: {chr(10)*2 in desc}')
print(f'Tiene viñetas?: {"•" in desc}')
print(f'Tiene encabezados?: {"[H" in desc}')
