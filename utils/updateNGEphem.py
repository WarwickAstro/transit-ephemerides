

# ----------------------------------------------------------------------------------
#                               Description
# ----------------------------------------------------------------------------------
#
# UpdateNGEphem.py -    a python script to update the input file for NG's 
#                       Ephem program
#   
#

# ----------------------------------------------------------------------------------
#                               Update History
# ----------------------------------------------------------------------------------
# 16/08/12 -    code writen
# 16/08/12 -    code tested
#

# check for nltk
try:
    import nltk
except ImportError:
    print "No nltk module, exiting!"
    exit()
    
from urllib import urlopen
import re

url_home="http://var2.astro.cz/ETD/"
html_home=urlopen(url_home).read()
raw=nltk.clean_html(html_home).split('\n')

star_name,planet=[],[]

# find latest list of planets from ETD homepage
for i in range(0,len(raw)):
    if "Known transiters" in raw[i]:
        loc=i+1

for i in range(loc,len(raw)):
    if len(raw[i].split()) == 2:
        star_name.append(raw[i].split()[0])
        planet.append(raw[i].split()[1])
        
    if len(raw[i].split()) == 3:
        name=str(raw[i].split()[0])+"%20"+str(raw[i].split()[1])
        star_name.append(name)
        planet.append(raw[i].split()[2])
            
    if len(raw[i].split()) != 2 and len(raw[i].split()) != 3:
        break

# get the values for each planet from ETD's pages
epoch, period, depth, duration, ra, dec=[],[],[],[],[],[]

for j in range(0,len(star_name)):
    url_planet="http://var2.astro.cz/ETD/etd.php?STARNAME=%s&PLANET=%s" % (star_name[j],planet[j])
    html_planet=urlopen(url_planet).read()
    raw_planet=nltk.clean_html(html_planet)

    html_planet_split=html_planet.split('\n')
    for i in range(0,len(html_planet_split)):
        if "name=\'M\' size=\'12\' value=\'" and "name=\'PER\' size=\'7\' value=\'" in html_planet_split[i]:
            
            # epoch
            epoch.append(re.sub("[^0-9.]", "",html_planet_split[i].split("name=\'M\' size=\'12\' value=\'")[1][:12]))
            
            # period
            period.append(re.sub("[^0-9.]", "",html_planet_split[i].split("name=\'PER\' size=\'7\' value=\'")[1][:7]))
            
            # transit depth
            depth.append(re.sub("[^0-9.]", "",html_planet_split[i].split("</td><td><b>")[-1][:6]))
            
            # duration in minutes
            dur=re.sub("[^0-9.]", "",html_planet_split[i].split("</b></td><td>")[-1][:6])
            
            # convert duration to hours
            duration.append("%.2f" % (float(dur)/60.0))
            
            # fix error on ETD pages where extra &nbsp characters are present for WASP-17
            err=html_planet_split[i].split("&nbsp")
            while ";" in err:
                err.remove(";")
            
            # RA
            ra.append("%s %s %s" %(re.sub("[^0-9.]", "",err[1][-2:]), re.sub("[^0-9.]", "",err[2]), re.sub("[^0-9.]", "",err[3][:7])))
            
            # DEC
            dec.append("%s %s %s" % (re.sub("[^0-9+-]", "",err[3][-3:]), re.sub("[^0-9.]", "",err[4]), re.sub("[^0-9.]", "",err[5][:6])))
            
            # print - can comment this out later                        
            print "[%s %s] RA: %s DEC: %s Epoch: %s Period: %s Depth: %s Duration: %s" % (star_name[j], planet[j], ra[j], dec[j], epoch[j], period[j], depth[j], duration[j]) 
            

# remove the objects with two names second name the "/" confuses ng_ephemeris.py
for i in range(0,len(star_name)):
    if len(star_name[i].split("/")) > 1:
        star_name[i]=star_name[i].split("/")[0]

# write a file for ng_ephemeris.py
# example format:
# GJ-436    2454222.6157    2.643901    1.03  11 42 11  +26 42 37  #shallow - only ~0.6%
f=open("ETD","w")

for i in range(0,len(star_name)):
    line="%s%s  %s  %s  %s  %s  %s  #depth: %s\n" % (star_name[i],planet[i],epoch[i],period[i],duration[i],ra[i],dec[i],depth[i])
    f.write(line)
    
f.close()

