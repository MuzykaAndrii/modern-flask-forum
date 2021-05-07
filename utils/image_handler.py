import os
import secrets
from PIL import Image

def save_picture(form_picture, path):
    #generate random name for pic
    random_hex = secrets.token_hex(8)

    #divide filename to name and extentions
    f_name, f_ext, = os.path.splitext(form_picture.filename)

    #connect new pic name to her extention
    picture_fn = random_hex + f_ext

    #generate new pic path according to new name and os folders position
    picture_path = os.path.join(path, picture_fn)
    
    #define default pic size
    output_size = (200, 200)

    #open, crop and save pic
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn