import sys, os, pprint
import pymupdf  


#Digitally Created PDF: The text is there (copyable) and it is guaranteed to be correct as it was created directly e.g. from Word
#Image-only PDF: A scanned document
#Searchable PDF: A scanned document, but an OCR engine was used. The OCR engine put text "below" the image so that you can search / copy the content. As OCR is pretty good, this is correct most of the time. But it is not guaranteed to be correct.


test = sys.argv[1]
dir_test = str(os.path.dirname(test))
filename = str(os.path.basename(test))
imgfolder = ''
log_dir = '_log_'

doc = pymupdf.open(test)

for page in doc:
    
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
            page_type = "Cyfrowo tworzony - wektor"


print('Wynik: %s z wartościami text_perc=%.2f i img_perc= %.2f' % (page_type, text_perc, img_perc))  

