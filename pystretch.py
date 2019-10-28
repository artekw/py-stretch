import sys
import os
import hashlib
import random
import img2pdf
import glob
from PyPDF2 import PdfFileWriter, PdfFileReader
from PIL import Image

# Image.MAX_IMAGE_PIXELS = 1000000000
Image.MAX_IMAGE_PIXELS = None

# rozmiar formatów
# szer x wys w pikselach 300dpi
A4 = (2480, 3508)
A3 = (3508, 4961)
A2 = (4961, 7016)
A1 = (7016, 9933)
A0 = (9933, 14043)


def resize_image(filename, resize_to, center=False, output='resized_image.jpg', fill_color=(255, 255, 255, 255)):
    img = Image.open(filename)
    if img.size[0] > img.size[1]:
        resize_to = (resize_to[1], resize_to[0])

    ratio_w = resize_to[0]/img.width
    ratio_h = resize_to[1]/img.height

    if ratio_w < ratio_h:
        resize_width = resize_to[0]
        resize_height = round(ratio_w * img.height)
    else:
        resize_width = round(ratio_h * img.width)
        resize_height = resize_to[1]

    image_resize = img.resize((resize_width, resize_height), Image.ANTIALIAS)
    new_img = Image.new('RGB', resize_to, fill_color)

    if center:
        offset = (round((resize_to[0] - resize_width) / 2),
                round((resize_to[1] - resize_height) / 2))
        new_img.paste(image_resize, offset)
    else:
        new_img.paste(image_resize)
    new_img.save(output)


def cut_image(filename, width=None, height=None):
    k = 0
    img = Image.open(filename)
    imgwidth, imgheight = img.size
    if width == None or height == None:
        print('UWAGA: Podaj rozmiar kawałka!')
        sys.exit(1)

    if img.size[0] > img.size[1]:
        # print("Obracam")
        width, height = height, width


    for i in range(imgwidth//width):
        for j in range(imgheight//height):
            box = (i*width, j*height, (i+1)*width, (j+1)*height)

            # clue pieces
            out = img.crop(box)
            outfile, outfile_ext = os.path.splitext(filename)
            img_filename = '{0}_{1}{2}'.format(outfile, k, outfile_ext)
            out.save(img_filename)

            # conver to pdf file
            pdf_filename = '{0}_{1}{2}'.format(outfile, k, '.pdf')
            pdf_bytes = img2pdf.convert(img_filename)
            file = open(pdf_filename, "wb")
            file.write(pdf_bytes)
            file.close()
            k = k + 1

            # clean up images
            os.remove(img_filename)
    os.remove(filename)


def merge_pdf(filename, paths):
    pdf_writer = PdfFileWriter()

    for p in paths:
        pdf_reader = PdfFileReader(p)
        for page in range(pdf_reader.getNumPages()):
            pdf_writer.addPage(pdf_reader.getPage(page))

    with open(filename + '.pdf', 'wb') as fh:
            pdf_writer.write(fh)


def hashtag():
    return hashlib.sha256(str(random.getrandbits(256)).encode('utf-8')).hexdigest()


# if __name__ == "__main__":
#     base = os.getcwd()
#     temp_dir = base + '/tmp'

#     if not os.path.isdir(temp_dir):
#         os.mkdir(temp_dir)

#     for f in os.listdir('.'):
#         filename, filename_ext = os.path.splitext(f)
#         if filename_ext == '.jpg':
#             if not 'resized' in filename: 
#                 sesion_hastag = hashtag()
#                 sesion_folder = '{0}/{1}'.format(temp_dir, sesion_hastag)
#                 os.mkdir(sesion_folder)
#                 print(f)
#                 resize_image(
#                     f, A3, '{0}/{1}_resized{2}'.format(sesion_folder, filename, filename_ext))
#                 cut_image(
#                     '{0}/{1}_resized{2}'.format(sesion_folder, filename, filename_ext), 2408, 3505)

#                 # merge pdf's in one document
#                 paths = [sesion_folder + '/' + pdf for pdf in os.listdir(sesion_folder)]
#                 merge_pdf(base + '/' + filename, paths)
#                 print('Gotowe!')

