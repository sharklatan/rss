# coding:utf-8 
import configparser
from pygtrans import Translate
from bs4 import BeautifulSoup
import sys
import os
from urllib import request
import urllib
import time
from urllib.parse import urljoin
import re
import hashlib

def get_md5_value(src):
    _m = hashlib.md5()
    _m.update(src.encode('utf-8'))
    return _m.hexdigest()
    
config = configparser.ConfigParser()
config.read('test.ini',encoding='utf-8')
secs=config.sections()

def get_cfg(sec,name):
    return config.get(sec,name).strip('"')

def set_cfg(sec,name,value):
    config[sec][name]='"%s"'%value

def get_cfg_tra(sec):
    cc=config.get(sec,"action").strip('"')
    target=""
    source=""
    if cc == "auto":
        source  = 'auto'
        target  = 'zh-CN'
    else:
        source  = cc.split('->')[0]
        target  = cc.split('->')[1]
    return source,target

def extract_full_article(article_url):
    """Descarga el artículo completo preservando párrafos y estructura"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        req = urllib.request.Request(article_url, headers=headers)
        html_doc = request.urlopen(req, timeout=10).read().decode('utf8', errors='ignore')
        soup_article = BeautifulSoup(html_doc, 'html.parser')
        
        # Buscar contenido - probamos varios selectores comunes
        content = None
        for selector in ['div.post-content', 'article', 'div.entry-content', 'main', 'div.content']:
            content = soup_article.select_one(selector)
            if content:
                break
        
        if not content:
            return None
        
        # Remover scripts y estilos
        for script in content(['script', 'style', 'nav', 'footer']):
            script.decompose()
        
        # Procesar párrafos, listas y encabezados preservando estructura
        text_parts = []
        
        for element in content.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li', 'blockquote', 'pre']):
            # Obtener texto del elemento
            elem_text = element.get_text(strip=True)
            
            if elem_text:
                # Agregar encabezados con énfasis visual
                if element.name.startswith('h'):
                    text_parts.append(f"\n[{element.name.upper()}] {elem_text}\n")
                # Agregar items de lista con viñeta
                elif element.name == 'li':
                    text_parts.append(f"• {elem_text}\n")
                # Párrafos normales
                else:
                    text_parts.append(f"{elem_text}\n")
        
        if not text_parts:
            # Fallback a texto completo si no hay párrafos detectados
            clean_text = content.get_text(separator='\n', strip=True)
        else:
            clean_text = '\n'.join(text_parts)
        
        # Limpiar múltiples saltos de línea
        while '\n\n\n' in clean_text:
            clean_text = clean_text.replace('\n\n\n', '\n\n')
        
        clean_text = clean_text.strip()
        
        # Validar que sea contenido significativo
        if len(clean_text) > 300:
            return clean_text
        
        return None
    except Exception as e:
        print(f"    ! Error descargando {article_url}: {type(e).__name__}")
        return None

BASE=get_cfg("cfg",'base')
try:
    os.makedirs(BASE)
except:
    pass

links=[]

def tran(sec):
    out_dir= BASE + get_cfg(sec,'name')
    url=get_cfg(sec,'url')
    max_item=int(get_cfg(sec,'max'))
    old_md5=get_cfg(sec,'md5')
    source,target=get_cfg_tra(sec)
    global links

    print(f"\n============================================================")
    print(f"Procesando: {sec}")
    print(f"  URL: {url}")
    print(f"  Idioma: {source} → {target}")
    
    links+=[" - %s [%s](%s) -> [%s](%s)\n"%(sec,url,url,get_cfg(sec,'name'),out_dir)]

    GT = Translate()
    headers={
        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    req = urllib.request.Request(url, headers=headers)
    html_doc=request.urlopen(req).read().decode('utf8')
    new_md5= get_md5_value(html_doc)

    if old_md5 == new_md5:
        print(f"  ℹ Sin cambios (MD5 idéntico)")
        return
    else:
        set_cfg(sec,'md5',new_md5)
    
    # move style
    html_doc=html_doc.replace('<?', '</s')
    html_doc=html_doc.replace('?>', '/>')
    
    soup = BeautifulSoup(html_doc, 'html.parser')
    items=soup.find_all('item')
    
    # Eliminar tags de creadores (dc:creator)
    for creator in soup.find_all('dc:creator'):
        creator.decompose()
    
    # Procesar items: extraer artículos completos
    print(f"  Procesando {min(max_item, len(items))} artículos...")
    for idx, item in enumerate(items):
        if idx >= max_item:
            break
        
        # Obtener URL del artículo - el link puede estar vacío pero el texto después
        article_url = None
        link_tag = item.find('link')
        
        if link_tag:
            # Intenta obtener de .string
            if link_tag.string:
                article_url = link_tag.string
            else:
                # Busca el siguiente nodo de texto que sea una URL
                next_node = link_tag.next_sibling
                if next_node and hasattr(next_node, 'strip'):
                    text = next_node.strip()
                    if text.startswith('http'):
                        article_url = text
        
        if not article_url:
            print(f"    ! [{idx+1}] No se encontró URL")
            continue
        
        # Descargar y extraer artículo completo
        full_text = extract_full_article(article_url)
        if full_text:
            print(f"    ✓ [{idx+1}] Artículo completo ({len(full_text)} chars)")
            # Reemplazar descripción con texto completo
            desc = item.find('description')
            if desc:
                desc.string = full_text
        else:
            print(f"    ~ [{idx+1}] No se extrajo (fragmento original)")
        
        time.sleep(0.3)  # No sobrecargar servidor
    
    # Eliminar items por encima del máximo
    for idx, e in enumerate(items):
        if idx >= max_item:
            e.decompose()
    
    # AHORA: Traducir SOLO los textos, no todo el XML
    items = soup.find_all('item')
    texts_to_translate = []
    
    for idx, item in enumerate(items):
        if idx >= max_item:
            break
        
        title = item.find('title')
        desc = item.find('description')
        
        if title and title.string:
            texts_to_translate.append(('title', idx, str(title.string)))
        if desc and desc.string:
            texts_to_translate.append(('desc', idx, str(desc.string)))
    
    print(f"  Traduciendo {len(texts_to_translate)} textos de {source} a {target}...")
    
    # Traducir cada texto por separado
    for text_type, item_idx, text_content in texts_to_translate:
        try:
            # Usar marcador de salto de línea para preservar durante traducción
            text_with_marker = text_content.replace('\n', '###NEWLINE###')
            
            translated = GT.translate(text_with_marker, target=target, source=source)
            translated_text = translated.translatedText
            
            # Restaurar saltos de línea después de traducción
            translated_text = translated_text.replace('###NEWLINE###', '\n')
            
            # AHORA: Aplicar cutoff de patrones EN EL TEXTO TRADUCIDO
            # Esto asegura que cortamos DESPUÉS de que los patrones han sido traducidos
            if text_type == 'desc':
                # Patrones en el idioma destino (español, etc.)
                cutoff_patterns = [
                    'haz más con',
                    'ftc:',
                    'háganos saber en los comentarios',
                    'consulta el resumen',
                    'sigue leyendo'
                ]
                
                for pattern in cutoff_patterns:
                    if pattern in translated_text.lower():
                        idx = translated_text.lower().find(pattern)
                        translated_text = translated_text[:idx].strip()
                        break
            
            item = items[item_idx]
            if text_type == 'title':
                title_tag = item.find('title')
                if title_tag:
                    title_tag.string = translated_text
            else:  # desc
                desc_tag = item.find('description')
                if desc_tag:
                    # Escapar saltos de línea para preservarlos en XML
                    desc_tag.string = translated_text.replace('\n', '&#10;')
            
            time.sleep(0.5)  # Delay entre traducciones
        except Exception as e:
            print(f"    ✗ Error traduciendo: {type(e).__name__}")
    
    content = str(soup)
    
    with open(out_dir,'w',encoding='utf-8') as f:
        f.write(content)
    
    print(f"  ✓ Completado: {url} → {out_dir}")

for x in secs[1:]:
    tran(x)
    print(config.items(x))

with open('test.ini','w') as configfile:
    config.write(configfile)



YML="README.md"

f = open(YML, "r+", encoding="UTF-8")
list1 = f.readlines()           
list1= list1[:13] + links

f = open(YML, "w+", encoding="UTF-8")
f.writelines(list1)
f.close()