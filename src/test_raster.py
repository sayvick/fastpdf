import sys, os, shutil, logging, json
import pymupdf  

test = sys.argv[1]
dir_test = str(os.path.dirname(test))
filename = str(os.path.basename(test))
imgfolder = ''
tmp_dir = '_tmp_'
log_dir = '_log_'

DPI = 96
FORMAT = "jpg"

#subfolder path
img_folder = os.path.join(dir_test,tmp_dir)
log_folder = os.path.join(dir_test,log_dir)

if not os.path.exists(img_folder):
    os.makedirs(img_folder)
else:
    shutil.rmtree(img_folder)
    os.makedirs(img_folder)

#format to wypuszczenie danych o loggerze
def setup_logging():
    
    if not os.path.exists(log_folder):
        os.makedirs(log_folder)
    else:
        shutil.rmtree(log_folder)
        os.makedirs(log_folder)
    
    logging.basicConfig(filename=f'{log_folder}\\image_info.txt', level=logging.DEBUG,
                        format='%(asctime)s - %(levelname)s - %(message)s')

def log_pretty(data):
    pretty_data = json.dumps(data, indent=4)
    logging.debug(f'\n{pretty_data}')

doc = pymupdf.open(test)
doc2 = pymupdf.open()

setup_logging()
log_pretty(doc.metadata)

for page in doc:
    
    #w głównej mierze mamy doczynienia z wektorami
    
    #anoots=True - adnotacje tez do rastera
    pix = page.get_pixmap(dpi=DPI,annots=True,colorspace=pymupdf.csRGB)
    print(pix.size)
    pix.save(f'{img_folder}\\page-%i--dpi-{DPI}.{FORMAT}' % (page.number+1))
    
    
doc.close()
subfolder_list = os.listdir(img_folder)

for i,f in enumerate(subfolder_list):

    img = pymupdf.open(os.path.join(img_folder, f))
    
    #page
    rect = img[0].rect
    
    #ref for pdf in memory
    pdfbytes = img.convert_to_pdf() 
    img.close()
    
    #open PDF stream
    imgPDF = pymupdf.open("pdf", pdfbytes) 
    page = doc2.new_page(width = rect.width, height = rect.height)  
    page.show_pdf_page(rect, imgPDF, 0)
    imgPDF.close()
    
doc2.save(f'{dir_test}\\TEST--RASTER-OUT.pdf',garbage=4,deflate=True)
print("zapisano")
doc2.close()

new_rects = []  # resulting rectangles

for p in page.get_drawings():
    w = p["width"]
    r = p["rect"] + (-w, -w, w, w)  # enlarge each rectangle by width value
    for i in range(len(new_rects)):
        if r.intersects(new_rects[i]):  # touching one of the new rects?
            new_rects[i] |= r  # enlarge it
    # now look if contained in a new rect
    remainder = [s for s in new_rects if r in s]
    if remainder == []:  # no ==> add it
        new_rects.append(r)

new_rects = list(set(new_rects))  # remove any duplicates
new_rects.sort(key=lambda r: (r.tl.y, r.tl.x))  # sort by appearance sequence
mat = fitz.Matrix(3, 3)  # high resolution matrix
for i, r in enumerate(new_rects):
    pix = page.get_pixmap(matrix=mat, clip=r)
    pix.save("drawing-%i.png" % i)