import numpy
from PIL import Image, ImageDraw


#code from jialongw - download_image() method modified
# imports
import requests # to get image from the web
import shutil # to save it locally
import os
import csv
import cv2
from ast import literal_eval

# global variables
project_name = ""
paths = []
object_labels = []

def set_paths():
    global paths
    for object_label in object_labels:
        for item in ['Images', 'Labels', 'Masks']:
            paths.append(os.path.join(project_name, object_label, item))

def make_directories():
    for path in paths:
        try:
            os.makedirs(path) # make directories
        except OSError as e:
            print ("Creation of the directory %s failed: %s" % (path, format(e)))
        else:
            print ("Successfully created the directory %s " % path)

def download_images(csv_file):
    try:
        # read data
        with open(csv_file, 'rt') as file:
            data = csv.reader(file)
            # Sniffer class to deduce the format of a CSV file and detect whether a header row is present
            # along with the built-in next() function to skip over the first row only when necessary
            has_header = csv.Sniffer().has_header(file.read(1024))
            file.seek(0)  # rewind
            if has_header:
                next(data)  # skip header row

            for row_idx, row in enumerate(data):
                row_index = str(row_idx+1)
                # load data
                labeled_data_url = row[2] # load original image url
                labels = literal_eval(row[3]) # label entry converted to dictionary
                if len(labels) == 0:
                    continue # if no labels created, skip the current entry
                else:
                    objects = labels['objects'] # load label instances

                for i in range(len(object_labels)):
                    image_downloaded = False
                    masks = []
                    mask_index = 0
                    result = 0
                    file_name = ""
                    for object in objects:
                        if object['title'] == object_labels[i]:
                            if image_downloaded:
                                #crop image section 

                                param = object['polygon'] #takes in crop coord as dict
                                crop_param = []
                                for xy in param: #iterates over values and adds to crop_param
                                    crop_param.append((xy["x"],xy["y"]))
                                polygon_crop(file_name, crop_param)
                            else:
                                # download original image
                                dir_name = paths[3*i]
                                file_name = "{}{}{}.png".format(project_name, "0"*(5-len(row_index)), row_index)
                                save_image(labeled_data_url, dir_name, file_name)
                                image_downloaded = True
except IOError:
        logging.exception('')
    if not data:
        raise ValueError('No data available')

def save_image(image_url, dir_name, file_name):
    # Open the url image, set stream to True, this will return the stream content.
    # stream = True to guarantee no interruptions
    r = requests.get(image_url, stream = True)
    # Check if the image was retrieved successfully
    if r.status_code == 200:
        # Set decode_content value to True, otherwise the downloaded image file's size will be zero.
        r.raw.decode_content = True
        # Open a local file with wb ( write binary ) permission.
        with open(os.path.join(dir_name, file_name), 'wb') as f:
            shutil.copyfileobj(r.raw, f)
        print("Image sucessfully Downloaded: ", os.path.join(dir_name, file_name))
    else:
        print("Image Couldn\'t be retreived")
#end

def polygon_crop(im_file, crop_param):
    #code to poly crop

    # read image as RGB and add alpha (transparency)
    im = Image.open(im_file).convert("RGBA")

    # convert to numpy (for convenience)
    imArray = numpy.asarray(im)

    # create mask
    polygon = [crop_param]
    maskIm = Image.new('L', (imArray.shape[1], imArray.shape[0]), 0)
    ImageDraw.Draw(maskIm).polygon(polygon, outline=1, fill=1)
    mask = numpy.array(maskIm)

    # assemble new image (uint8: 0-255)
    newImArray = numpy.empty(imArray.shape,dtype='uint8')

    # colors (three first columns, RGB)
    newImArray[:,:,:3] = imArray[:,:,:3]

    # transparency (4th column)
    newImArray[:,:,3] = mask*255

    # back to Image from numpy
    newIm = Image.fromarray(newImArray, "RGBA")
    newIm.save("{}{}{}.png".format(project_name, "0"*(5-len(row_index)), row_index))


def get_avg_dim():
    #get height/width tuple
    #add to sum and increment counter
    #at end return avg = sum/count
    
    pass

def box_crop():
    pass


if __name__=='__main__':
    # define the name of the directory to be created
    input_string = input('What is your project\'s name?\n').split()
    for word in input_string:
        project_name = project_name + word.capitalize()
    input_string = input('What are the object labels in your project? (separate by comma)\n').split(',')
    for word in input_string:
        object_labels.append(word)
    set_paths()
    make_directories()
    csv_file = input('Enter the csv file name: ')
    download_images(csv_file)