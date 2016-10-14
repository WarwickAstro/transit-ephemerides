
# 
#                        Ephemeris2.py 
# 
#       An updated version of Neale Gibson's Ephemeris script
# 
#						 James McCormac
#
# All of the basic functionality regarding predicting when transits 
# occur etc was written by Neale. Over time I spotted some ways to make
# this script more efficient when scheduling follow-up observations.
# This is my attempt do that. I wanted to automatically set the 
# evening and morning twilights, calculate the moon distance and its
# percentage illuminated. This eliminates the need to check each target's
# visibilty/twilight/moon limitations on a transit-by-transit basis. 
# Much quicker :)
#
# Usage (same as before):
#     python Ephemeris2.py Planets Observatories start end [--calendar]
#	
# where Planets and Observatories are files containing planet ephemrides		
# and observatory specific information. Start and end can be either in 
# Gregorian format, e.g. 2014-12-12 or julian date, e.g. 2456780
#
# Requirements:
#    PyEphem must be installed. For iCal events icalendar must also be
#    installed. Both are easily obtained using pip.
#
# To do:
#    Add options on how to filter transits sent to iCal
# 	 Add ability to create events for other observatories
#
# Version History:
# 20141214:	v1.0    Code adapted from NG's Ephemeris.py, added moon calcs,
#                   argparse, twilight calcs, and changed layout of 
#                   observatories file. 
#                   Fixed bug in eph_functions --> Deg()
#	                The code is still run in the same way as before
#                   for simplicity. - JMCC
# 20141215: v1.1    Added iCal event creator. Only flags full transits
#                   that are >= 30 deg from moon for La Palma. - JMCC
#

# import functions needed
import sys,os,time
import eph_functions as JD
import argparse as ap
from datetime import datetime, timedelta

# look for pyephem, warn and die happily if not installed
try:
	import ephem
except ImportError:
	print "You need to install PyEphem. It is easy if you have pip:"
	print "\n\tsudo pip install ephem\n"
	print "If you don't have pip, get pip :)\n"
	print "\thttps://pip.pypa.io/en/latest/installing.html\n" 
	sys.exit()

# start counting
start = time.time()

# function to parse the command line
def ArgParse():

	parser=ap.ArgumentParser()
	parser.add_argument("objects", help="objects filename (e.g. Planets1.txt)")
	parser.add_argument("observatories", help="observatories filename (e.g. Observatories1.txt)")
	parser.add_argument("start", help="date range lower limit (e.g. 2014-12-12 or 2456708)")
	parser.add_argument("end", help="date range upper limit (e.g. 2014-12-30 or 2456724)")
	parser.add_argument("--calendar", help="iCal filename")
	args=parser.parse_args()

	return args

# function to get the sunset, sunrise and twilight times
# assumed astronomical for obvious reasons
def GetSunTimes(date,lat,lon,elev):

	obs=ephem.Observer()
	obs.lon=str(lon)
	obs.lat=str(lat)
	obs.elev=elev
	obs.pressure=750
	obs.horizon = '-0:34'
	
	obs.date=date
	sunset  =obs.next_setting(ephem.Sun()) 
	sunrise =obs.next_rising(ephem.Sun())  
	
	#-6=civil twilight, -12=nautical, -18=astronomical
	obs.horizon = '-18' 
	end_evening_twi=obs.next_setting(ephem.Sun(), use_center=True) 
	start_morning_twi=obs.next_rising(ephem.Sun(), use_center=True) 
	
	return obs,sunset,end_evening_twi,start_morning_twi,sunrise

# parse command line
args=ArgParse()

# check for output directory
suffix = ".eph2"
dir = 'planet_eph2'
if os.path.exists(dir) == False:
	os.mkdir(dir)

# checks on command line inputs
if os.path.exists(args.objects) == True:
	objects = open(args.objects)
else:
	print "No objects file %s, exiting..." % (args.objects)
	sys.exit()

if os.path.exists(args.observatories) == True:
	observatories = open(args.observatories)
else:
	print "No observatories file %s, exiting..." % (args.observatories)
	sys.exit()


# check for type of start and end dates
try:
	startJD=int(args.start)
	endJD=int(args.end)
except ValueError:
	print "Dates in Gregorian format, converting..."
	startJD=int(ephem.julian_date(args.start))+1
	endJD=int(ephem.julian_date(args.end))+1
	print "%s-->%d" % (args.start,startJD)
	print "%s-->%d" % (args.end,endJD)

if endJD < startJD:
	print "Date range [%d-->%d] invalid" % (startJD,endJD) 
	print "Range ends before it starts, exiting..." 
	sys.exit()

if len(str(endJD)) != 7 or len(str(startJD)) != 7:
	print "Invalid JD, check number of digits, exiting..."
	sys.exit()


# get date and time tuples
sdate,stime = JD.Jul_date(startJD)
edate,etime = JD.Jul_date(endJD)

# create range string
obsrange = "%.2i/%.2i/%.4i - %.2i/%.2i/%.4i " % (sdate[0],sdate[1],sdate[2],edate[0],edate[1],edate[2])

# define following useful lists
lat = [0.,0.,0.]
lon = [0.,0.,0.]
RA = [0.,0.,0.]
Dec = [0.,0.,0.]

# set up dictionaries for noontimes in UTC
# and observatory elevations
noontime={}
obselev={}

# loop over all obsevatories in list
for line in observatories:
	# read in observatory info
	if line[0] == '#':
		continue
	elif line[0] != '\n' and line[0] != ' ':
		# for each observatory get its information
		# if looks wrong, warn about the new format of observatory file
		try:
			observatory,lat[0],lat[1],lat[2],lon[0],lon[1],lon[2],lowlim,obsndate,obsntime,elev = line.split()
		except ValueError:
			print "Problem splitting observatory file %s..." % (args.observatories)
			print "Ensure the file has the following format with 1 line per observatory:\n"
			print "\tname latitude longitude alt_limit noondate noontime(UTC) elevation"
			print "e.g."
			print "\tLaPalma 28 40 00 -17 52 00 30. 2014-12-12 12:00:00 2326.\n"
			print "noondate can be any date in the above format, noontime must be"
			print "the approximate UTC of noon at the observatory. This is best approximated"
			print "by 12:00:00 minus the time zone difference"
			print "Exiting..."
			sys.exit()
		
		# set up some numbers for the calcs to follow	
		noontime[observatory] = "%s %s" % (obsndate, obsntime)
		obselev[observatory] = float(elev)
		latitude = JD.Deg(lat)
		longitude = JD.Deg(lon)
		lowlim=float(lowlim)
		
		# set up an "Observer" location for moon distance calcs	
		telescope=ephem.Observer()
		telescope.lon=str(longitude)
		telescope.lat=str(latitude)
		telescope.elev=obselev[observatory]
		print "%s [%.6fN:%.6fE]" % (observatory,latitude,longitude)
		
		# where all the transity stuff will go
		Transits={}

		# open a per observatory file and create a header
		obs_output = open(observatory + suffix, "w") 
		print >> obs_output, "# Visible transits from " + observatory
		print >> obs_output, "#   Objects :    RA         Dec"
		objects.seek(0)
		for line in objects:
			if line[0] == '#':
				continue
			elif line[0] != '\n' and line[0] != ' ':
				print >> obs_output, "# %10s [%s] [%s]" % (line.split()[0],' '.join(line.split()[4:7]),' '.join(line.split()[7:10]))
		print >> obs_output, "# Date range : " + obsrange
		print >> obs_output, "#\n#    HJD          Object      Date     Time/UT      Window",
		print >> obs_output, "        HA limits             Alt            Transit type?        MoonAng      % Illuminated\n#"
		
		# start looping over objects
		objects.seek(0)
		for line in objects:
			if line[0] == '#':
				continue
			elif line[0] != '\n' and line[0] != ' ':
				# for each object do
				object,HJD,period,duration,RA[0],RA[1],RA[2],Dec[0],Dec[1],Dec[2] = line.split()[:10]
				HJD,period,duration = float(HJD),float(period),float(duration)
				ra = JD.Deg(RA)
				delta = JD.Deg(Dec)		
		
				# open a per object file and create a header
				obj_output = open(dir + "/" + object + "_" + observatory + suffix, "w")
				print >> obj_output, "# Object : " + object
				print >> obj_output, "# Observatory : " + observatory
				print >> obj_output, "# Date range : " + obsrange
				print >> obj_output, "# Coords : RA " + ' '.join(RA) + ' dec ' + ' '.join(Dec)
				print >> obj_output, "# Epoch(0) : HJD " + str(HJD)
				print >> obj_output, "# Period : " + str(period) + " days"
				print >> obj_output, "# Duration : " + str(duration) + " hrs"
				print >> obj_output, "#\n#    HJD          Date     Time/UT      Window",
				print >> obj_output, "       HA limits             Alt            Transit type?        MoonAng      % Illuminated\n#"
				
				# make an ephem object per target for moon calcs
				star=ephem.FixedBody()
				rin="%s:%s:%s" % (RA[0],RA[1],RA[2])
				din="%s:%s:%s" % (Dec[0],Dec[1],Dec[2])
				star._ra=ephem.hours(rin)
				star._dec=ephem.degrees(din)
				
				# now loop over transits
				while HJD < endJD:
					HJD += period
					# calculate times, alts etc
					date,UT = JD.Jul_date(HJD)
					
					# moon separation calcs
					tnow="%04d/%02d/%02d %02d:%02d:%.2f" % (date[2],date[1],date[0],UT[0],UT[1],UT[2])
					m=ephem.Moon(tnow)
					telescope.date = tnow
					star.compute(telescope)
					moon_sep=ephem.separation(m,star)
					sep_calc=str(moon_sep).split(":")
					moon_sep_deg=JD.Deg(tuple((sep_calc[0],sep_calc[1],sep_calc[2])))
					
					hrs = float(UT[0]) + float(UT[1])/60. + float(UT[2])/60./60.
					LST = JD.Sid_time(HJD, longitude)
					HA = JD.HA(LST,ra)
					alt, alt_s, alt_e = JD.Altitude(latitude, delta, HA),JD.Altitude(latitude, delta, HA-duration/2.),JD.Altitude(latitude, delta, HA+duration/2.)

					# send noon of this day to get the sun times
					twidate="%04d/%02d/%02d %s" % (date[2],date[1],date[0],noontime[observatory].split()[1])
					noontime[observatory]=twidate
					obs,t1,t2,t3,t4=GetSunTimes(noontime[observatory],latitude,longitude,obselev[observatory])
					twi1=JD.Time_to_decimal(tuple(str(t2).split()[1].split(':')))
					twi2=JD.Time_to_decimal(tuple(str(t3).split()[1].split(':')))

					# only save and print under observable conditions
					# need to calculate things differently for (twi2<twi1) and vice verca
					if (twi2 < twi1): # eg La Palma
						if (HJD > startJD) and (alt>lowlim or alt_s > lowlim or alt_e > lowlim) and (hrs > twi1 or hrs < twi2):
							# add output string to dicionary
							window = JD.window(UT, duration)
							Date = "%.2i/%.2i/%.4i " % (date[0],date[1],date[2]) 
							HA_alt = JD.HA_alt(HA,duration,alt_s,alt,alt_e) # just returns a string
							Transits[HJD] = "%10s  %10s %24s %s" % (object,Date,window,HA_alt)
						
							# determine what type of transit it is ie Full/partial
							if (alt_s > lowlim and alt > lowlim and alt_e > lowlim and ((hrs-duration/2.) > twi1 or (hrs-duration/2.) < twi2) and ((hrs+duration/2.) < twi2 or (hrs+duration/2.) > twi1) ):
								Transits[HJD] += "  Full Transit > %i   " % lowlim
							elif (alt_s > lowlim) and ((hrs-duration/2.) > twi1 or (hrs-duration/2.) < twi2):
								if (hrs > twi1 or hrs < twi2) and alt > lowlim:
									Transits[HJD] += "  Ingress + mid > %i  " % lowlim
								else:
									Transits[HJD] += "  Ingress only > %i   " % lowlim
							elif (alt_e > lowlim) and ((hrs+duration/2.) > twi1 or (hrs+duration/2.) < twi2):
								if (hrs > twi1 or hrs < twi2) and alt > lowlim:
									Transits[HJD] += "  Egress + mid > %i   " % lowlim
								else:
									Transits[HJD] += "  Egress only > %i    " % lowlim
							else:
								Transits[HJD] += "  Mid only? > %i      " % lowlim
								
							# add moon
							Transits[HJD] += "   %03d   " % (int(moon_sep_deg))	
							Transits[HJD] += "       %03d   " % (int(m.phase))
								
 							# now output to file
 							print >> obj_output, "%.5f  %s" % (HJD, Transits[HJD][12:])
 					
 					# need to calculate things differently for (twi2<twi1) and vice verca
					if (twi2 > twi1): # eg Hawaii
						if (HJD > startJD) and (alt>lowlim or alt_s > lowlim or alt_e > lowlim) and (hrs > twi1 and hrs < twi2):
							# add output string to dicionary
							window = JD.window(UT, duration)
							Date = "%.2i/%.2i/%.4i " % (date[0],date[1],date[2])
							HA_alt = JD.HA_alt(HA,duration,alt_s,alt,alt_e)
							Transits[HJD] = "%10s  %10s %24s %s" % (object,Date,window,HA_alt)
						
							# determine what type of transit it is ie Full/partial
							if (alt_s > lowlim and alt > lowlim and alt_e > lowlim and ((hrs-duration/2.) > twi1 and (hrs-duration/2.) < twi2) and ((hrs+duration/2.) < twi2 and (hrs+duration/2.) > twi1) ):
								Transits[HJD] += "  Full Transit > %i   " % lowlim
							elif (alt_s > lowlim) and ((hrs-duration/2.) > twi1 and (hrs-duration/2.) < twi2):
								if (hrs > twi1 or hrs < twi2) and alt > lowlim:
									Transits[HJD] += "  Ingress + mid > %i  " % lowlim
								else:
									Transits[HJD] += "  Ingress only > %i   " % lowlim
							elif (alt_e > lowlim) and ((hrs+duration/2.) > twi1 and (hrs+duration/2.) < twi2):
								if (hrs > twi1 or hrs < twi2) and alt > lowlim:
									Transits[HJD] += "  Egress + mid > %i   " % lowlim
								else:
									Transits[HJD] += "  Egress only > %i    " % lowlim
							else:
								Transits[HJD] += "  Mid only? > %i      " % lowlim
 							
 							# add moon
							Transits[HJD] += "   %03d   " % (int(moon_sep_deg))
							Transits[HJD] += "       %03d   " % (int(m.phase))
 							
 							# now output to file
 							print >> obj_output, "%.5f  %s" % (HJD, Transits[HJD][12:])
				obj_output.close()

		# calendar outputs 
		if args.calendar:
			
			if observatory != "LaPalma":
				print "WARNING CALENDAR IS ONLY WORKING FOR LA PALMA OBSERVATIONS SO FAR, BREAKING..."
				break
						
			try:
				from icalendar import Calendar, Event
			except ImportError:
				print "No iCal module, disabling calendar functionality"
				print "You can install iCal for python using pip\n"
				print "\tsudo pip install icalendar\n"
				print "Exiting..."
				sys.exit()	
			
			cal = Calendar()
			cal.add('version', '2.0')
			cal.add('prodid', 'meadeCalendar')
			cal.add('X-WR-CALNAME','NITES Transit Calendar')

				
		# output sorted observatory list
		key = sorted(Transits.keys())
		for HJD in key:
			print >> obs_output, "%.5f  %s" % (HJD, Transits[HJD])
		
			if args.calendar:
				uid=0
				for HJD in key:
					if "Full Transit" in Transits[HJD]:
						md,mi=Transits[HJD].split()[-2:]
						
						# only objects further than 30 deg from the moon!
						if md >= 30:
							tar,dmid,tmid,trange,harange,el1,el2,el3,ft1,ft2,ft3,ft4,md,mi=Transits[HJD].split()
							
							# correct the night starting date
							d=datetime(int(dmid.split('/')[2]),int(dmid.split('/')[1]),int(dmid.split('/')[0]),int(tmid.split(':')[0]),int(tmid.split(':')[1]),int(tmid.split(':')[2]))
							if d.hour <= 12:
								d=d-timedelta(days=1)	
							
							summary="%s\n%s %s %s %s %s %s %s %s %s %s %s %s" % (tar,d,trange,harange,el1,el2,el3,ft1,ft2,ft3,ft4,md,mi)
								
							event = Event()
							event.add('summary', summary)
							event.add('dtstart', d)
							event.add('dtend', d+timedelta(hours=1))
							event.add('dtstamp', datetime.now())
							event['uid'] = uid 
							event.add('priority', 5)
							cal.add_component(event)
							uid += 1
		
		# write out the iCal file
		if args.calendar:					
			calname='%s.ics' % (args.calendar)
			calfile=open(calname,'w')
			calfile.write(cal.to_ical())
			calfile.close()				
			print "Import %s into iCal to see the transits" % (calname)
		
		obs_output.close()

# close the open files
observatories.close()
objects.close()

# show time elapsed
end = time.time()
print "t = %im %.1fs" % (int((end - start)/60),(end - start)%60)

