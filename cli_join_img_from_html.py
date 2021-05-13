#%%
import sys
from PIL import Image
import os, inspect
import re
import html
from ordered_set import OrderedSet
import click

# %% lettura immagini
# si determina la directory dalla quale si avvia lo script
# cd = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

# lista delle estensioni comuni per file di immagini

extensions = list(Image.registered_extensions().keys())
save_ext = 'png'

@click.command()
@click.argument('source')
@click.option('--destination', '-d', default='.', help='percorso di salvataggio dei file uniti')
@click.option('--dir_name', '-n', default=None, help='sovrascrive il nome di default della cartella di salvataggio (nome del file html)')
@click.option('--keep_files', '-k', is_flag=True, default=False, help='cancella i file originali')
def join_img_html(source, destination, dir_name=None, keep_files=False):
    """
    # Unione di immagini

    Lo script unisce le immagini presenti nella cartella in un'unica immagine per essere importata facilemnte in un file .odt 
 
    ## Requisiti:
    
    È necessario esportare nella cartella la relazione come html:

        - è presente un file html del tipo "Relazione <nome>.html"

        - serie di immagini "image_<id>.<ext>"


    ## Funzioni:

    - Lettura del file html, da cui:

        - si estraggono i nomi delle immagini presenti

        - si estrae la didasclia corrispondente alle immagini

    - Unione delle immagini:

        - le immagini con lo stesso indice sono unite in un unico file tipo png

    - Salvataggio immagini:

        - le immagini sono salvate in directory di livello superiore

        - si crea nuova cartella basata sul <nome> del file html

        - si salvano le immagini con la didascalia come nome

    
    """

    
    
    # ritorna lista di di DirEntry (name, path, is_file, is_dir)
    fl = list(os.scandir(source))

    # ci sarà sempre un solo file html nella cartella alla volta perché altrimenti i file delle immagini sono riscritti
    try:
        file_html = list(filter(lambda f: re.search('html$', f.name), fl))[0]
    except IndexError:
        print('Nessun file html nella cartella')
        sys.exit()

    if dir_name:
        new_dir = dir_name
    else:
        new_dir, = os.path.splitext(file_html.name)
    
    save_path = os.path.join(destination, new_dir)

    if not os.path.exists(save_path):
        os.makedirs(save_path)
 
    # lista di file utilizzati
    file_list = [file_html.path]


    """
    Esportando direttamente in HTML dal SismiCAD, si creano delle coppie di immagini con lo schema seguente:

        - "image_{}.gif": Scala dei valori
        - "image_{}.jpg": Vista

    Si manipola la lista in modo tale che la *vista* preceda la *scala dei valori*
    """

    with open(file_html) as f:
        body = f.read()

    lista_img = list(re.finditer(r'(?<=img src=")(\S+)(?=")', body)) # lista di re.match object
    # il match object è del tipo "image_1.jpg": lo si spezza in nome+ext, si salva nome in nomi unici
    nomi_unici = OrderedSet( [os.path.splitext(img.group(0))[0] for img in lista_img] )

    print("nuovo file aggiunto in :")
    for nu in nomi_unici:
        # filtra immagini della lista in base al nome unico: se presenti jpg+gif crea la coppia di re.Match
        subg = list(filter(lambda x: nu == os.path.splitext(x.group(0))[0], lista_img))
        
        # estrazione didascalia
        """
        si cerca il primo match della stringa "ff13" dall'ultima posizione del gruppo corrente
        """
        index = subg[-1].end()
        try:
            didascalia = html.unescape(re.search('(?<="ff13">)(.+)(?=<)', body[index:]).group(0))
        except AttributeError:
            didascalia = nu

        # Pulizia dei caratteri illegali per salvataggio file
        didascalia = re.sub(r'[\\/*?<>:"|]', "§",  didascalia)
        # Rimozione punto alla fine della stringa (evita che il nome file abbia ..ext)
        didascalia = re.sub(r"\.$", "", didascalia)

        # apertura delle immagini del gruppo
        images = []
        for sg in subg:
            img_path = os.path.join(source, sg.group(0))
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
        print(new_path)

    if not keep_files:
        for f in file_list:
            os.remove(f)

#%% DEBUG
# join_img_html(source='./Spettri', destination='.', delete_files=False)