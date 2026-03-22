# SSDV_Check.py - plots the ground tracks for SilverSat during SSDV passes.
# Last update: 3/15/2026 DJC
#
# Revision history: 3/1/2026 DJC - inception
#                   3/15/2026 DJC - added TLE validation and update, tooltips for tracks
#                   3/22/2026 DJC - changed SSDV_times format to match the three columns in Lord Of The Spreadsheets

#


import matplotlib.pyplot as plt  # package for plotting
import cartopy.feature as cfeature  # package for making maps
import cartopy.crs as ccrs  # cartopy projections
import urllib.request # used to fetch TLE data if file is missing or outdated
from datetime import datetime, timezone, timedelta
from datetime import datetime, timezone
import screeninfo # used to get screen size for dynamic figure sizing
from skyfield.api import load, EarthSatellite # Skyfield for satellite tracking
import mplcursors  # new import for tooltips

LOCATION_FILE = 'data/locations.csv'  # CSV file with location names and lat/lon (name,lat,lon)
SSDV_FILE = 'data/SSDV_times.txt' # text file with SSDV times (location, type, time) - type is currently ignored but can be used for future expansion
NORAD_NUM = 66909   # SilverSat NORAD number 
TLE_FILE = 'data/tle_66909.txt' # local file to store TLE data for SilverSat - will be updated if missing or outdated
PASS_LENGTH = 6 # SSDV pass length in minutes - used to determine how long to plot the ground track for each pass

def plot_map(projection=ccrs.PlateCarree(), gridlines=False):
    # creates the base map with the Earth image as a background. The projection can be 
    # changed by passing a different cartopy CRS object. Gridlines can be turned on by 
    # setting gridlines=True (does not currently work).
    screen = screeninfo.get_monitors()[0]
    width_inches = (screen.width * 0.75) / 100  # approximate inches at 100 DPI
    height_inches = (screen.height * 0.75) / 100
    fig = plt.figure(figsize=(width_inches, height_inches))
    
    img = plt.imread('data/earth_equirectangular.jpg')

    # Define the image (covers the entire Earth)
    img_extent = (-180, 180, -90, 90)
    
    ax = plt.axes(projection=projection)
    ax.set_global()
    ax.imshow(img, origin='upper', extent=img_extent, transform=ccrs.PlateCarree(), zorder=0)
    if gridlines:
        gl = ax.gridlines(color='white', linewidth=0.5, alpha=0.8)
        gl.zorder = 10
    # ax.add_feature(cfeature.BORDERS, linestyle=':')
    # ax.add_feature(cfeature.COASTLINE)
    plt.tight_layout()
    return ax

def plot_locations(ax):
    # reads the locations from the CSV file and plots them on the map. The CSV file should 
    # have three columns: name, latitude, longitude. Lines starting with # or empty lines 
    # are ignored.
    with open(LOCATION_FILE, 'r') as f:
        for line in f:
            if line.startswith('#') or not line.strip():
                continue
            parts = line.strip().split(',')
            if len(parts) < 3:
                continue
            name, lat, lon = parts[0], float(parts[1]), float(parts[2])
            ax.plot(lon, lat, marker='o', color='red', markersize=5, transform=ccrs.PlateCarree())
            ax.text(lon + 1, lat + 1, name, fontsize=9, color='red',transform=ccrs.PlateCarree())   

def read_ssdv_times():
    # reads the SSDV times from the text file. The file should have three columns: location, type, time. 
    # Lines that do not have exactly three columns or where the second column is not 'SSDV' are 
    # ignored. The time can be in either ISO format (YYYY-MM-DDThh:mm:ss) or in the 
    # SSDVTimes command format (SSDV yr mon day hr min sec). The function returns a list 
    # of tuples (location, datetime).
    ssdv_data = []
    with open(SSDV_FILE, 'r') as f:
        for line in f:
            parts = line.strip().split('\t')
            if len(parts) != 3 or parts[1] != 'SSDV':
                continue
            location = parts[0]
            time_str = parts[2]
            if '-' in time_str:
                # ISO format: YYYY-MM-DDThh:mm:ss
                dt = datetime.fromisoformat(time_str).replace(tzinfo=timezone.utc)
            else:
                # Old format: space-separated yr mon day hr min sec
                time_parts = time_str.split()
                if len(time_parts) == 6:
                    yr, mon, day, hr, min, sec = time_parts
                    dt = datetime(year=int(yr), month=int(mon), day=int(day), 
                                  hour=int(hr), minute=int(min), second=int(sec), tzinfo=timezone.utc)
                else:
                    continue
            ssdv_data.append((location, dt))
    return ssdv_data


def check_tle_file():
 # checks if the TLE file exists and is valid. If the file is missing, has an invalid 
 # format, has a NORAD number that does not match SilverSat, or is over 1 hour old, 
 # it fetches new TLE data from Celestrak and saves it to the file. 
 
    print("Checking TLE file...")
    try:
        with open(TLE_FILE, 'r') as f:
            lines = [line.strip() for line in f.readlines()]
        if len(lines) < 3 or not lines[1].startswith('1 ') or not lines[2].startswith('2 '):
            raise ValueError("Invalid TLE format")
        line1, line2 = lines[1], lines[2]
        # Check NORAD number
        norad_from_tle = int(line1[2:7])
        if norad_from_tle != NORAD_NUM:
            raise ValueError("NORAD number mismatch")
        # Parse epoch
        yy = int(line1[18:20])
        ddd = int(line1[20:23])
        frac = float(line1[23:32])
        year = 2000 + yy
        day_of_year = ddd + frac
        tle_date = datetime(year, 1, 1, tzinfo=timezone.utc) + timedelta(days=day_of_year - 1)
        now = datetime.now(timezone.utc)
        if now - tle_date > timedelta(hours=1):
            raise ValueError("TLE is over 1 hour old")
    except (FileNotFoundError, ValueError, IndexError):
        # Fetch new TLE
        print("TLE file is missing or invalid. Fetching new TLE data...")
        url = f'https://celestrak.org/NORAD/elements/gp.php?CATNR={NORAD_NUM}&FORMAT=TLE'
        with urllib.request.urlopen(url) as resp:
            data = resp.read().decode('utf-8').strip().splitlines()
        if len(data) < 3:
            raise ValueError("TLE response did not contain three lines")
        name = data[0].strip()
        line1 = data[1].strip()
        line2 = data[2].strip()
        with open(TLE_FILE, 'w') as f:
            f.write(name + '\n')
            f.write(line1 + '\n')
            f.write(line2 + '\n')

def create_satellite():
    # reads the TLE from the file and returns a Skyfield EarthSatellite object. 
 
    with open(TLE_FILE, 'r') as f:
        lines = f.readlines()
    name = lines[0].strip()
    line1 = lines[1].strip()
    line2 = lines[2].strip()
    satellite = EarthSatellite(line1, line2, name)
    return satellite

def plot_ground_track(ax, satellite, start_time, duration_seconds, color):
# plots the ground track of the satellite starting from the given time for the specified
#  duration. The track is plotted in the specified color. The function samples the 
# satellite position every 30 seconds and converts it to latitude and longitude for 
# plotting.
    ts = load.timescale()
    # Sample every 30 seconds
    num_points = duration_seconds // 30 + 1
    times = [start_time + timedelta(seconds=i * 30) for i in range(num_points)]
    lats, lons = [], []
    for t in times:
        subpoint = satellite.at(ts.utc(t)).subpoint()
        lats.append(subpoint.latitude.degrees)
        lons.append(subpoint.longitude.degrees)
    line, = ax.plot(lons, lats, color=color, transform=ccrs.PlateCarree(), linewidth=2)
    return line

if __name__ == "__main__":
    ax = plot_map(gridlines=False)
    plot_locations(ax)
    ssdv_data = read_ssdv_times()
    check_tle_file()
    satellite = create_satellite()

    print("SSDV Times:")
    for location, t in ssdv_data:
        print(f"{location}: {t.isoformat()}")

    colors = ['blue', 'green', 'orange', 'purple', 'brown']  # cycle colors
    lines = []
    line_to_data = {}
    for i, (location, start_time) in enumerate(ssdv_data):
        color = colors[i % len(colors)]
        line = plot_ground_track(ax, satellite, start_time, PASS_LENGTH * 60, color)
        lines.append(line)
        line_to_data[line] = (location, start_time)
    
    # Add tooltips for all tracks
    cursor = mplcursors.cursor(lines, hover=True)
    @cursor.connect("add")
    def on_add(sel):
        location, start_time = line_to_data[sel.artist]
        sel.annotation.set_text(f"{location}\n{start_time.isoformat()}")
    @cursor.connect("remove")
    def on_remove(sel):
        sel.annotation.set_visible(False)
        plt.gcf().canvas.draw_idle()
    
    plt.show()
