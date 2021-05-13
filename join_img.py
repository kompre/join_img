#%% [markdown]
"""
# Unione di immagini

Il presente script unisce le immagini presenti nella cartella in un'unica immagine per essere importata facilmente in un file .odt 

funzioni:

- legge le immagini presente nella cartella
- unisce le immagini in senso orrizzontale, accostandole le une alle altre
"""
#%%
import sys
from PIL import Image
import os, inspect


# %% lettura immagini
cd = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

# lista delle estensioni comuni per file di immagini
# extensions = ['jpg', 'png', 'jpeg', 'svg']

extensions = list(Image.registered_extensions().keys())
ext = 'png'

fl = os.listdir(cd)
fl = [os.path.join(cd, f) for f in fl if any(ext in f for ext in extensions)]

out_path = os.path.abspath(os.path.join(cd, r"..\\"))
delete_files = False


#%%
images = [Image.open(f) for f in fl]
widths, heights = zip(*(i.size for i in images))

total_width = sum(widths)
max_height = max(heights)

new_im = Image.new('RGBA', (total_width, max_height))

x_offset = 0
for im in images:
  new_im.paste(im, (x_offset,0))
  x_offset += im.size[0]

new_path = os.path.join(out_path, f'test.{ext}')
new_im.save(new_path)
#%%