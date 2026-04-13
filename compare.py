from bs4 import BeautifulSoup

with open('rss/9to5mac_BASELINE.xml', 'r', encoding='utf-8') as f:
    baseline = f.read()
with open('rss/9to5mac.xml', 'r', encoding='utf-8') as f:
    nuevo = f.read()

print('BASELINE:')
soup_b = BeautifulSoup(baseline, 'html.parser')
items_b = soup_b.find_all('item')
print(f'  Items: {len(items_b)}')
if items_b:
    print(f'  Primer item title: {items_b[0].find("title").get_text()[:60]}')
    desc_b = items_b[0].find('description').get_text()[:150]
    print(f'  Primer item desc: {desc_b}')

print()
print('NUEVO:')
soup_n = BeautifulSoup(nuevo, 'html.parser')
items_n = soup_n.find_all('item')
print(f'  Items: {len(items_n)}')
if items_n:
    print(f'  Primer item title: {items_n[0].find("title").get_text()[:60]}')
    desc_n = items_n[0].find('description').get_text()[:150]
    print(f'  Primer item desc: {desc_n}')
