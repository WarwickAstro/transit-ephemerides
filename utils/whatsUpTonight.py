import os
from astropy.time import Time

# pylint: disable = superfluous-parens

def getTonightsTransits():
    """
    Grab a list of tonight's transiting objects
    """
    script_dir = os.path.dirname(os.path.realpath(__file__))
    f = open('{}/../LaPalma.eph2'.format(script_dir)).readlines()
    jd_today = int(Time.now().jd)
    todays_lines = []
    coords = {}
    for i in range(0, len(f)):
        if f[i].startswith('#'):
            if "[" in f[i] and "]" in f[i]:
                t = f[i].split()
                name = t[1]
                ra = "{}:{}:{}".format(t[2][1:], t[3], t[4][:-1])
                dec = "{}:{}:{}".format(t[5][1:], t[6], t[7][:-1])
                coords[name] = "%s %s" % (ra, dec)
        if not f[i].startswith('#'):
            if int(float(f[i].split()[0])) == jd_today:
                todays_lines.append(f[i])
    return todays_lines, coords

def splitFullPartials(todays_lines, coords):
    """
    Split up tonights transiting objects into
    full and partial transits, print the results
    to the screen
    """
    partials, full_coords, partial_coords = [], [], []
    print("\nFull Transits (La Palma):")
    for i in range(0, len(todays_lines)):
        x = todays_lines[i].split()[9:]
        if "Full" in x and "Transit" in x:
            print(todays_lines[i].split('\n')[0])
            full_coords.append(todays_lines[i].split()[1])
        else:
            partials.append(todays_lines[i])
    print("\nPartials (La Palma):")
    if len(partials) > 0:
        for i in range(0, len(partials)):
            print(partials[i].split('\n')[0])
            partial_coords.append(partials[i].split()[1])

    print("\nTarget Coordinates for Object Visibility:")
    if len(full_coords) > 0:
        for i in range(0, len(full_coords)):
            print("{} {}".format(full_coords[i], coords[full_coords[i]]))
    if len(partial_coords) > 0:
        for i in range(0, len(partial_coords)):
            print("{} {}".format(partial_coords[i], coords[partial_coords[i]]))

if __name__ == '__main__':
    tonight, coords = getTonightsTransits()
    splitFullPartials(tonight, coords)
