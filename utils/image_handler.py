import os
import secrets
from PIL import Image

def gen_filename(filename, number_of_characters):

    #generate random name for pic
    random_hex = secrets.token_hex(number_of_characters)

    #divide filename to name and extentions
    f_name, f_ext, = os.path.splitext(filename)

    #connect new pic name to her extention
    picture_fn = random_hex + f_ext

    return picture_fn



def save_picture(form_picture, filename, path, output_size):

    #generate new pic path according to new name and os folders position
    picture_path = os.path.join(path, filename)

    #open, crop and save pic
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return filename

def delete_file(path):
    if os.path.exists(path):
        os.remove(path)
        print("Successfully deleted!")
    else:
        print("The file does not exist")