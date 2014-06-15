#!/usr/bin/python

__author__ = "Arlo Carreon <http://arlocarreon.com>"


# Purpose: 
#  generate an "average" image from local directory


import sys
import os
import re
import math
from PIL import Image
from optparse import OptionParser

# Type of extensions you are willing to accept
ext = "JPG|jpeg|jpg|png"

# Function grabs all images in a folder
def get_photos_from_directory( path ):
	listing = os.listdir(path)
	images = []
	regex_str = '.*\.['+ext+']'
	print "Looking for matching files: "+regex_str
	for infile in listing:
		if re.match( regex_str, infile, re.I|re.X ):
			images.append(infile)
	return images

def resize(im, screen, standard_area):
    
    (screen_width, screen_height) = screen
    (width, height) = im.size
    
    # resize here to all occupy about the same area on screen.
    area = width * height
    factor = math.sqrt( standard_area * 1.0 / area )
    width *= factor
    height *= factor
        
    # but stay within the maximum screen.
    if width > screen_width or height > screen_height:
        # landscape
        if width > height:   
            width = screen_width
            height *= screen_width / width
        # portrait
        else:       
            width *= screen_height / height
            height = screen_height
    
    width = int(width)
    height = int(height)
    
    return im.resize((width,height), Image.BICUBIC)


def create_average(screen, photos, source_path):
    
    debug("starting")

    # some geometry
    (screen_width, screen_height) = screen
    center_x = screen_width / 2;
    center_y = screen_height / 2;

    # we will resize all photos to have an area around this.
    phi = 1
    standard_area = screen_width * (screen_width/phi)
    

    # prototype black screen all images get pasted onto. 
    black = Image.new("RGBA", screen)
    average = black.copy()

    
    for i in range(len(photos)):

        debug("processing >> %s" % photos[i])
        
        try:
            im = Image.open(source_path + photos[i]);
        except: 
            debug("Bad Image? Script no likie.")
            continue
        
        im = resize(im, screen, standard_area);
        
        # paste photo in the center of a black screen. 
        (im_width, im_height) = im.size
        offset_x = center_x - im_width / 2;
        offset_y = center_y - im_height / 2;
       
        im_frame = black.copy()
        im_frame.paste(im, (offset_x,offset_y))
        
        # and blend this with our average 
        alpha = 1.0/(i+1)  # <-- clever part. Get average in constant memory.
                           # perhaps too clever. 
                           # images where most of the detail is just squished into one or two
                           # bits of depth. This may account for the slow darkening (?)
                           # may be better to combine images in a tree
        average = Image.blend(average, im_frame, alpha);

        # is this necessary? jclark had it.
        del im

    return average

def debug(msg):
    sys.stderr.write(msg + "\n")

def main(*argv):

    parser = OptionParser("usage: %prog [options] source_dir dest_file")
    parser.add_option("-x", "--height", dest="height", default=500,
                      help="height of the output file")
    parser.add_option("-y", "--width", dest="width", default=500,
                      help="width of the output file")

    (options, args) = parser.parse_args()

    source_dir = './'
    file = './average.png'

    if (len(args) > 0):
        source_dir = args[0]

    if (len(args) > 1):
        file = args[1]

    # Set the screen
    screen = (options.width, options.height)

    photos = get_photos_from_directory(source_dir)
    average = create_average(screen, photos, source_dir)
    average.save(file, 'PNG')

if __name__ == '__main__':
    sys.exit(main(*sys.argv))
