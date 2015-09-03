"""
John Loeber | September 3, 2015 | Python 2.7.9 | Debian Linux

input: one command-line argument: the name of the file containing the data.
       also: Robinson_BW.png and Robinson_Color.png are required to be
       in the same directory.
output: two .png files, BW_<timestamp>.png and Color_<timestamp>.png.
timestamp is taken when the script finishes executing.
"""

from sys import argv,stderr
from geoip import geolite2
from PIL import Image, ImageDraw
from time import time
from math import log

import pyproj

def parse_input():
    """
    parses the content of the input file, returning a dictionary of 
    IPs : Frequency Counts
    """
    input_file = argv[1]
    with open(input_file,'r') as f:
        lines = map(lambda x: x.rstrip('\r\n'), f.readlines())
    split = map(lambda x: x.lstrip(' ').split(' '), lines)
    # now we have a list of lists containing counts and IPs.
    return_dict = {}
    for s in split:
        # sanity check / filter:
        if len(s)!=2:
            stderr.write("Double-check line: " + str(s)+"\n")
        else:
            count = int(s[0])
            ip = s[1]
            return_dict[ip]=count
    return return_dict

def convert_ip_to_coordinates(ips):
    """
    takes dictionary {ip:frequency count} as input, where
        ip is a string
        frequency count is an int
    and returns a dictionary {(lat,long) : frequency count}
        where lat, long are both floats.
    """

    return_dict = {}
    for ip in ips.keys():
        match = geolite2.lookup(ip)
        if match is None:
            stderr.write("No match found for IP: " + ip)
        elif match.location is None:
            stderr.write("Match found, but no location found for IP: " + ip)
        else:
            (lat,lon) = match.location
            # grab the frequency count
            return_dict[(lat,lon)] = ips[ip]
    return return_dict

def convert_geo_coord_to_pixel_coord(coordinate_counts):
    """
    takes dictionary {(lat,long) : frequency count} as input, where
        lat, long are floats
        frequency count is an int
    maps every geographical (lat,long) to a pixel (x,y) on the map.
    """

    # set the map projection from which we are converting to WGS84
    # I'm hoping that EPSG:4326 is actually the projection that the maxmind
    # database (which geolite queries) uses. This should be the case.
    mapfrom = pyproj.Proj(init='EPSG:4326')
    
    # set the map projection to which we are converting (Robinson)
    p = '+proj=robin +lon_0=0 +x_0=0 +y_0=0 +ellps=WGS84 +datum=WGS84 +units=m +no_defs'
    mapto = pyproj.Proj(p)
    
    # robinson projection offset from (0,0) at the center of the map
    # we need this since PIL puts (0,0) in the top-left.
    robw = 17005833.33052523
    robh = 8625154.471849944

    # following specs are set for the two maps included with this script.
    # image dimensions
    imgw = 2058
    imgh = 1050
    # space surrounding the map in the imagefile: width and height. (offsets)
    w = 8
    h = 7
    # scaling the coordinates according to the dimensions and offsets of the map.
    mapw = imgw - (2*w)
    maph = imgh - (2*h)
    scalew = (robw*2) / mapw
    scaleh = -(robh*2) / maph
    xc = lambda x: (x+robw)/scalew + w
    yc = lambda y: (y-robh)/scaleh + h
    
    return_dict = {}
    for (lat,lon) in coordinate_counts.keys():
        # transform lat, lon to Robinson coordinates
        new_lat, new_lon = pyproj.transform(mapfrom,mapto, lon, lat)

        # transform Robinson coords to pixel coords
        (x,y) = (xc(new_lat),yc(new_lon))
        # assign the frequency count
        return_dict[(x,y)] = coordinate_counts[(lat,lon)]
    return return_dict

def convert_frequencies_to_circle_radii(pixel_counts):
    """
    takes dictionary {(x,y) : frequency count} as input, where
        lat, long are floats
        frequency count is an int
    and converts the frequency count to a circle radius. returns dictionary
    {(x,y) : radius}, where radius is a float.
    """

    # create new dict to return. we could change the old one in place, but that 
    # makes it harder to debug.
    pixel_sizes = {}
 
    for key in pixel_counts.keys():
        value = pixel_counts[key]
        # set a large radius to make the circle visible
        radius = value + 2
        pixel_sizes[key] = radius
    return pixel_sizes

def draw(pixel_locs_with_sizes):
    """
    takes dictionary {(x,y) : radius} as input, where
        x, y, radius are floats
    and appropriately places circles on the Robinson maps, then timestamps
    and saves them.
    """
    Robinson_BW = Image.open('maps/Robinson_BW.png')
    Robinson_Color = Image.open('maps/Robinson_Color.png')
    draw_BW = ImageDraw.Draw(Robinson_BW,'RGBA')
    draw_Color = ImageDraw.Draw(Robinson_Color,'RGBA')
    
    # set graphical options. Different color options for the color map and
    # for the BW map, for better contrast. 4th value is alpha.
    stroke_color_Color = "black"
    stroke_color_BW = "orange"
    stroke_thickness = 2
    internal_color_Color = "white"
    internal_color_BW = "red"

    for (x,y),radius in pixel_locs_with_sizes.iteritems():
        # we draw two circles: an underlying, larger one to act as the stroke
        # then the interior circle over it.
        # constants to ints (float rounding can otherwise create messy display).
        distance = int(radius + stroke_thickness)
        x = int(x)
        y = int(y)
        stroke = (x - distance, y - distance, x + distance, y + distance)
        draw_BW.ellipse(stroke,fill=stroke_color_BW)
        draw_Color.ellipse(stroke,fill=stroke_color_Color)

        inside = (x - radius, y - radius, x + radius, y + radius)
        draw_BW.ellipse(inside, fill= internal_color_BW)
        draw_Color.ellipse(inside, fill= internal_color_Color)

    # assuming you won't call this more frequently than once per second...
    timestamp = str(int(time()))
    
    Robinson_BW.save("BW_" + timestamp + ".PNG", "PNG")
    Robinson_Color.save("Color_" + timestamp + ".PNG", "PNG")

def main():
    ip_counts = parse_input()
    coordinate_counts = convert_ip_to_coordinates(ip_counts)
    pixel_counts = convert_geo_coord_to_pixel_coord(coordinate_counts)
    pixel_locs_with_sizes = convert_frequencies_to_circle_radii(pixel_counts)
    draw(pixel_locs_with_sizes)

if __name__=='__main__':
    main()
