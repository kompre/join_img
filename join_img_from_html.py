#%% [markdown]
"""
# Unione di immagini

Il presente script unisce le immagini presenti nella cartella in un'unica immagine per essere importata facilemnte in un file .odt 

Requisiti:

    - è necessario esportare nella cartella la relazione come html:
        - è presente un file html del tipo "Relazione <nome>.html"
        - serie di immagini "image_<id>.<ext>"

funzioni:

    - Lettura del file html, da cui:
        - si estraggono i nomi delle immagini presenti
        - si estrae la didasclia corrispondente alle immagini
    - Unione delle immagini:
        - le immagini con lo stesso indice sono uniti in un unico png
    - Salvataggio immagini:
        - le immagini sono salvate in directory di livello superiore
        - si crea nuova cartella basata sul <nome> del file html
        - si salvano le immagini con la didascalia come nome
"""
#%%
import sys
from PIL import Image
import os, inspect
import re
import html
from ordered_set import OrderedSet

# %% lettura immagini
# si determina la directory dalla quale si avvia lo script
cd = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

# lista delle estensioni comuni per file di immagini
extensions = list(Image.registered_extensions().keys())
save_ext = 'png'

fl = os.listdir(cd)

# ci sarà sempre un solo file html nella cartella alla volta perché altrimenti i file delle immagini sono riscritti
try:
    file_html = [os.path.join(cd, f) for f in fl if '.html' in f][0]
except IndexError:
    print('Nessun file html nella cartella')
    sys.exit()

new_dir = re.search(r"(?<=Relazione )(.+?)(?=_|\.)", os.path.basename(file_html)).group(0)

# lista di file utilizzati
file_list = [file_html]
#%%
out_path = os.path.abspath(os.path.join(cd, r"..\\"))

save_path = os.path.join(out_path, new_dir)
if not os.path.exists(save_path):
    os.makedirs(save_path)

delete_files = True
#%% [markdown]
"""
Esportando direttamente in HTML dal SismiCAD, si creano delle coppie di immagini con lo schema seguente:

    - "image_{}.gif": Scala dei valori
    - "image_{}.jpg": Vista

Si manipola la lista in modo tale che la *vista* preceda la *scala dei valori*
"""

#%%

with open(file_html) as f:
    body = f.read()

lista_img = list(re.finditer(r'(?<=img src=")(\S+)(?=")', body))

gruppi_img = OrderedSet([os.path.splitext(img.group(0))[0] for img in lista_img])

gruppi_img
#%%

bn = os.path.splitext


for gi in gruppi_img:
    # filtra immagini del gruppo
    subg = list(filter(lambda x: gi == bn(x.group(0))[0], lista_img))
    
    # estrazione didascalia
    """
    si cerca il primo match della stringa "ff13" dall'ultima posizione del gruppo corrente
    """
    index = subg[-1].end()
    try:
        didascalia = html.unescape(re.search('(?<="ff13">)(.+)(?=<)', body[index:]).group(0))
    except AttributeError:
        didascalia = gi

    # Pulizia dei caratteri illegali per salvataggio file
    didascalia = re.sub(r'[\\/*?<>:"|]', "§",  didascalia)
    # Rimozione punto alla fine della stringa (evita che il nome file abbia ..ext)
    didascalia = re.sub(r"\.$", "", didascalia)

    # apertura delle immagini del gruppo
    images = []
    for sg in subg:
        img_path = os.path.join(cd, sg.group(0))
        images.append(Image.open(img_path))
        file_list.append(img_path)
    
    # dimensioni immagini
    widths, heights = zip(*(i.size for i in images))
    total_width = sum(widths)
    max_height = max(heights)    

    # creazione nuova immagine
    new_im = Image.new('RGBA', (total_width, max_height))

    x_offset = 0
    for im in images:
        new_im.paste(im, (x_offset,0)) 
        x_offset += im.size[0]

    # salvataggio dell'immagine
    new_path = os.path.join(save_path, f'{didascalia}.{save_ext}')
    new_im.save(new_path)
    print(f"nuovo file aggiunto in :\n\t{new_path}")

if delete_files:
    for f in file_list:
        os.remove(f)

#%%