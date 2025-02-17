from pikepdf import Pdf
import os, ctypes
import pymupdf

def getBasicPaths(filepath):
    
    tmp_dir = os.path.dirname(filepath)
    tmp_name = os.path.basename(filepath).split('.pdf')[0]
    
    return {
        "directory": tmp_dir,
        "filename": tmp_name
    }

def extChecker(filename: str):
    
    ALLOWED_EXTENSIONS = {'pdf'}
    
    if '.' in filename:
        return filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
    else:
        return False        
    
def convertBytes(size: float):
        
    for x in ['bytes', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024.0:
            return "%3.1f %s" % (size, x)
        size /= 1024.0   
        
def flattenPDFs(file: str,config: dict):
    
    tmp_dir = os.path.dirname(file)
    tmp_name = os.path.basename(file).split('.pdf')[0]
    
    with Pdf.open(file, allow_overwriting_input=True) as pdf:
    
        pdf.flatten_annotations('screen')
        
        #reformat content stream
        pdf.save(f'{tmp_dir}\\{tmp_name}--{config.get("combo_val")}.pdf')
        
    print("Annotations flattening done!")  
      
    return True

#TODO - do poprawy
def TrimPDF(file: str,astr: set):
    tmp_dir = os.path.dirname(file)
    tmp_name = os.path.basename(file).split('.pdf')[0]
    
    dst = Pdf.new()
    
    with Pdf.open(file, allow_overwriting_input=True) as pdf:
        
        print(astr)
        
        for page_selected in astr:
            
            try:
                page = pdf.pages.p(page_selected)
                dst.pages.append(page)
                
            except Exception as e:
                
                ctypes.windll.user32.MessageBoxW(0, "Brak takiego zakresu stron", "Błąd", 0)
                print("Brak takiego zakresu stron")
                return False
            
        dst.save(f'{tmp_dir}\\{tmp_name}--OUT.pdf')
        
    print("Wniosek's processing complete!")
    dst = None    
        
    return True

def parse_range(astr):
    result = set()
    for part in astr.split(','):
        x = part.split('-')
        
        # zwraca str jezeli nie występuje "-"
        # x[-1] zwraca ostatni element z tablicy
        result.update(range(int(x[0]),int(x[-1])+1))
    return sorted(result)

def has_numbers(inptStr):
    return any(char.isdigit() for char in inptStr)

def flattenArr(xss):
    
    flat_list = []
    
    for xs in xss:
        for x in xs:
            flat_list.append(x)
            
    return flat_list

def deleteSHX(file: str):
    
    pathObj = getBasicPaths(file)
    
    doc = pymupdf.open(file)
    
    for page in doc:
        
        doc.xref_set_key(page.xref, "Annots", "null")
        print("SHX usunięte")
    
    doc.save(f"{pathObj.get('directory')}\\{pathObj.get('filename')}--SHX-OUT.pdf",garbage=3,deflate=True)
    doc.close()
    
    return True
    
def simplifyRasterize(file: str,config: dict):
    
    pathObj = getBasicPaths(file)
    
    img_dpi= config.get('dpi_value')
    img_format = "jpg"

    src = pymupdf.open(file)
    target = pymupdf.open()

    for page in src:
        
        pix = page.get_pixmap(dpi=img_dpi,annots=True,colorspace=pymupdf.csRGB)
        img_bytes = pix.tobytes(img_format,jpg_quality=95)
        outpage = target.new_page(width = page.rect.width, height = page.rect.height)
        outpage.insert_image(outpage.rect, stream=img_bytes)

        try:
            target.ez_save(f"{pathObj.get('directory')}\\{pathObj.get('filename')}{config.get('combo_val')}")
        except pymupdf.mupdf.FzErrorSystem: 
            ctypes.windll.user32.MessageBoxW(0, "Narzędzie nie moze nadpisać do aktywnego pliku o tej samej nazwie", "Błąd", 0)   

    print("raster gotowy")
    src.close()
    target.close()   
            
    return True

def isVectorOrScan(file: str):
    
    doc = pymupdf.open(file)
    
    page = doc[0]
        
    #całkowita liczba pikseli wzgledem strony
    page_area = abs(page.rect)
    txt_area = 0.0
        
    img_area = 0.0
    img_perc = 0.0
    text_perc = 0.0
        
    for block in page.get_text("dict")["blocks"]:
            
         #dict zwroci key:value zoacz get_text(;blocks) co zwraca
        if block["type"] == 1: # Type=1 are images
            bbox=block["bbox"]
            img_area += (bbox[2]-bbox[0])*(bbox[3]-bbox[1]) # width*height
            img_perc = img_area / page_area
        
        #zawiera tekst i metainfo o img
    for block_txt in page.get_text("blocks"):
            
            #block_txt - zawiera bbox kordy, potem tekst, potem sekwencer bloka a potem jezeli 0 to text, a 1 to blok pod img
            # tutaj zwracamy listę bbox kazdego tekstu
            #pprint.pprint(block[:4])
            
            #obiekt Rect
            r = pymupdf.Rect(block_txt[:4])
                
            #wid*hei dając procent zajetosci
            txt_area = txt_area + abs(r)
            text_perc = txt_area / page_area
            
        
    if text_perc < 0.01: #No text = Scanned
                page_type = "Skan"
    elif img_perc > .8:  #Has text but very large images = Searchable
                page_type = "tekst wszukiwany" 
    else:
                page_type = "Cyfrowo utworzony"


    result = 'Wynik: %s z wartościami text_perc=%.2f i img_perc= %.2f' % (page_type, text_perc, img_perc) 
    
    return result