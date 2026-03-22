# SSDV_Check - GUI for plotting the coverage of upcoming SilverSat SSDV passes

This project is a Python application that visualizes the ground track of satellite object 66909 on an equirectangular map of Earth. It reads location data from a CSV file and satellite position data from TLE (Two-Line Element) information, allowing users to see the satellite's path over specified time intervals.

## Project Structure

```
satellite-ground-track-gui
├── src
│   ├── main.py          # Entry point of the application
│   ├── gui.py           # Contains the EarthMapGUI class for the graphical interface
│   ├── satellite.py      # Defines the Satellite class for position calculations
│   ├── projection.py      # Functions for converting coordinates and plotting arcs
│   └── utils.py         # Utility functions for data processing
├── data
│   ├── earth_equirectangular.jpg  # Equirectangular map image
│   ├── tle_66909.txt              # TLE data for satellite object 66909
│   ├── locations.csv               # CSV file with location data (name, latitude, longitude)
│   └── SSDVContacts.csv            # CSV file with dates and times for satellite position calculations
├── requirements.txt                # Project dependencies
└── README.md                       # Project documentation
```

## Requirements

Install dependencies from `requirements.txt`:

```bash
pip install -r requirements.txt
```

If you need to install manually:

```bash
pip install numpy matplotlib cartopy skyfield mplcursors screeninfo pillow requests python-dateutil pytz
```

`cartopy` may require system packages on macOS:
- `brew install geos proj gdal`
- then `pip install cartopy`

4. The GUI will display the equirectangular map with plotted locations and satellite ground tracks based on the provided TLE data and SSDV contact times.

## License

This project is open-source and available under the MIT License.