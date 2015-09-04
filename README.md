# IP-Mapper

This is a tool for mapping frequency counts of IPs onto a world map,
displaying proportionally-sized circles to represent them. Builds open my
previous [Travelmap](https://github.com/Datamine/Travelmap) project.

### Usage:

`python ip-mapper.py <your-input-file-here>`

Input files should be formatted as a frequency count (integer) followed by a space, an IPv4 address, and a newline. An example is included: `example-input.txt`.
(The IPs listed therein have been [randomly generated](http://sqa.fyicenter.com/Online_Test_Tools/Test_IP_Address_Generator.php).)

There are two output maps:   

    1. A black-and-white one, which displays all datapoints in a high-contrast red, so they can be easily geographically identified.  
    2. A colored one, which displays transparent datapoints, so it is easier to gauge the geographical frequency of IPs over small areas.  

### Required Libraries:
* python-geoip (http://pythonhosted.org/python-geoip/)
* python-geoip-geolite2
* python-pyproj (https://pypi.python.org/pypi/pyproj?), Version 1.9.4
* Python Imaging Library (http://effbot.org/imagingbook/pil-index.htm), Version 1.1.7, Pillow Version 2.3.0

Beyond that, the script queries an online db to geolocate the IP, so an internet connection is required for it to run.
Note that the accuracy of that database is [apparently](https://www.maxmind.com/en/geoip2-city-database-accuracy?country=United+States&resolution=250) 72% within a distance of 250km for the US,
though it may vary significantly among other countries (example: for Germany, that accuracy drops to 44%, with 54% of queries going unresolved).

### Acknowledgements

This script comes with two Robinson projection maps based on open-source images:
* Robinson_BW.png: Courtesy of the [University of Alabama Cartographic Research Lab](http://alabamamaps.ua.edu/about.html)
* Robinson_Color.png: from [Wikipedia](http://upload.wikimedia.org/wikipedia/commons/9/96/Robinson_projection_SW.jpg) by [User:Strebe](http://commons.wikimedia.org/wiki/User:Strebe).
