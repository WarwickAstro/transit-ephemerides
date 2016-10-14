import numpy

"""
Module to calculate UT/date and Sidereal Time from Julian Date
"""

def Jul_date(JD):
	jd_temp = JD
	
	while jd_temp > 100000:
		jd_temp -= 10000
	while jd_temp > 10000:
		jd_temp -= 10000
	while jd_temp > 1000:
		jd_temp -= 1000
	while jd_temp > 100:
		jd_temp -= 100
	while jd_temp > 10:
		jd_temp -= 10
	while jd_temp > 1:
		jd_temp -= 1
		
	if jd_temp >= 0.5:
		JD += 1
		jd_temp -= 0.5
		hours = 0
	else:
		hours = 12

	L= int(JD+68569)
	N= int(4*L/146097)
	L= int(L-(146097*N+3)/4)
	I= int(4000*(L+1)/1461001)
	L= int(L-1461*I/4+31)
	J= int(80*L/2447)
	K= int(L-2447*J/80)
	L= int(J/11)
	J= int(J+2-12*L)
	I= int(100*(N-49)+I+L)
	
	year = I
	month = J
	day = K
	
	mins = 0
	secs = 0
	
	jd_temp *= 24.
	while jd_temp >= 10:
		jd_temp -= 10
		hours += 10
	while jd_temp >= 1:
		jd_temp -= 1
		hours += 1
	jd_temp *= 60.
	while jd_temp >= 10:
		jd_temp -= 10
		mins += 10
	while jd_temp >= 1:
		jd_temp -= 1
		mins += 1
	jd_temp *= 60.
	while jd_temp >= 10:
		jd_temp -= 10
		secs += 10
	while jd_temp >= 1:
		jd_temp -= 1
		secs += 1
	secs += jd_temp
		
	return (day, month, year), (hours, mins, secs)

##################################

def Sid_time(JD, long):
	D = JD - 2451545.0
	#calculate GMST (Grenwich mean sidereal time)
	GMST = 18.697374558 + 24.06570982441908 * D
	
	#calculate apparent sidereal time
	Epsilon = (23.4393 - 0.0000004 * D) * numpy.pi / 180.
	L = (280.47 + 0.98565 * D) * numpy.pi / 180.
	Omega = (125.04 - 0.052954 * D) * numpy.pi / 180.
	del_phi = -0.000319*numpy.sin(Omega) - 0.00024*numpy.sin(2*L)
	eqeq = del_phi * numpy.cos(Epsilon)
	GAST = GMST + eqeq
	
	#now calculate local sidereal time by correcting for longitude
	LST = GAST + long/15.

	#reduce to < 24
	while LST > 24.:
		LST -= 24.
	
	return LST

##################################

def RA_to_decimal(RA):
	l = len(RA.split())
	
	if l == 3:
		h,m,s = RA.split()
		RA = float(h) + float(m)/60. + float(s)/60./60.
		return RA
	
	if l == 2:
		h,m = RA.split()
		RA = float(h) + float(m)/60.
		return RA

##################################

def Time_to_decimal(t):
	
	if len(t) == 3:
		h,m,s = t[0],t[1],t[2]
		RA = float(h) + float(m)/60. + float(s)/60./60.
		return RA
	
	if len(t) == 2:
		h,m = t[0],t[1]
		RA = float(h) + float(m)/60.
		return RA

##################################

def HA(LST, RA):
	#h,m,s = RA.split()
	HA = LST - RA
	while HA > 12:
		HA -= 24.
	while HA < -12:
		HA += 24.
	
	return HA

#################################

def window(time, duration):
	time_str = "%.2i:%.2i:%.2i" % (time[0], time[1], time[2])
	time = float(time[0]) + float(time[1])/60. + float(time[2])/60./60.
	start = time - duration/2.
	end = time + duration/2.
	
	if start >= 24.:
		start -= 24.
	if start < 0.:
		start += 24.
	if end >= 24.:
		end -= 24.
	if end < 0.:
		end += 24.
	
	start = "%.2i:%.2i" % (int(start),int(float(start%1)*60.))
	end = "%.2i:%.2i" % (int(end),int(float(end%1)*60.))
	
	return "%s  [%s-%s] " % (time_str,start,end)
	
#################################	
	
def Altitude(latitude, delta, HA):
	return (180./numpy.pi*numpy.arcsin(numpy.sin(latitude*numpy.pi/180.)*numpy.sin(delta*numpy.pi/180.)+numpy.cos(latitude*numpy.pi/180.)*numpy.cos(delta*numpy.pi/180.)*numpy.cos(HA/24.*2*numpy.pi)))
	
#################################

def HA_alt(HA,dur,alts,alt,alte):
	HAs = HA - dur/2.
	HAe = HA + dur/2.
	
	if HAs < 0.:
		HAs = "%.2i:%.2iE" % (int(-HAs),int(float((-HAs)%1)*60.))
	else:
		HAs = "%.2i:%.2iW" % (int(HAs),int(float((HAs)%1)*60.))
	if HAe < 0.:
		HAe = "%.2i:%.2iE" % (int(-HAe),int(float((-HAe)%1)*60.))
	else:
		HAe = "%.2i:%.2iW" % (int(HAe),int(float((HAe)%1)*60.))

	return "[%s-%s]  [%+5.1f %+5.1f %+5.1f]" % (HAs,HAe,alts,alt,alte)

#################################

def Deg(l):
	#
	#probable bug for anything that is -0 20 34 deg etc!!!!!
	#
	if float(l[0]) >= 0:
		return (float(l[0]) + float(l[1])/60. + float(l[2])/60./60.)
	else:
		return (float(l[0]) - (float(l[1])/60.) - (float(l[2])/3600.))
