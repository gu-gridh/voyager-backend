from typing import Optional, List
from enum import Enum
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import voyager
import utils
import datetime
import pandas as pd

CONFIG_PATH         = './configs/config.yml'
VESSEL_CONFIG_PATH  = './configs/vessels.yml'

# Load the vessel configuration
vessel_cfg = utils.load_yaml(VESSEL_CONFIG_PATH)

# Set the available modes in the configuration
Mode = Enum('Mode', {k: k for k in vessel_cfg.keys()})


######### CONFIGURE APPLICATION ###############
app = FastAPI()
origins = [
    "http://localhost",
    "http://localhost:8080",
    "http://192.168.68.106:8080/",
]

app.add_middleware(
    CORSMiddleware,
    # allow_origins=origins
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/vessels/")
async def vessel(mode: Mode, id: Optional[int] = None):
    """Returns the vessel configurations, the craft type and their features.

    Args:
        mode (Mode): Mode of propulsion, e.g. 'drifting'
        id (Optional[int], optional): ID integer for type of craft. Defaults to None.

    Raises:
        HTTPException: If the vessel ID is not found

    Returns:
        List: A list of vessel configurations, or a list of vessel features.
    """

    # Load the vessel configuration
    vessel_cfg = utils.load_yaml(VESSEL_CONFIG_PATH)

    # Two different modes:
    # One lists all vessel ids based on the mode of propulsion
    # The second lists a specific vessel given id and mode of propulsion
    if not id:
        vessel = vessel_cfg.get(mode.value, {})
        vessel = [{'id': k, ** v} for k, v in vessel.items()]
    else:

        vessel = vessel_cfg.get(mode.value, {})

        try:
            vessel = vessel.get(id, {})
        except:
            raise HTTPException(status_code=404, detail="Vessel ID not found.")

    return vessel


@app.get("/api/trajectory/")
def trajectory(
    mode: Mode,
    craft: int,
    start_date: datetime.date,
    duration: float,
    timestep: float,
    destination_lat: float,
    destination_lon: float,
    departure_lat: float,
    departure_lon: float,
    lat_min: float,
    lat_max: float,
    lon_min: float,
    lon_max: float,
    speed: Optional[float] = None):
    """Generates a trajectory using the Voyager tool. Returns a GeoJSON feature
    collection with PolyLine coordinates in latitude/longitude.

    Args:
        mode (Mode): Mode of propulsion, e.g. 'drifting'
        craft (int): ID integer for type of craft
        start_date (datetime.date): Start date of the vessel departure
        duration (float): Maximal duration of the trajectory from the departure date
        timestep (float): Simulation timestep resolution in seconds (s)
        destination_lat (float): Latitude of the destination coordinate
        destination_lon (float): Longitude of the destination coordinate
        departure_lat (float): Latitude of the destination coordinate
        departure_lon (float): Longitude of the destination coordinate
        lat_min (float): Minimum latitude of the simulation bounding box
        lat_max (float): Maximum latitude of the simulation bounding box
        lon_min (float): Minimum longitude of the simulation bounding box
        lon_max (float): Maximum longitude of the simulation bounding box
        speed (Optional[float], optional): Paddling speed (m/s). Defaults to None.

    Returns:
        dict: GeoJSON feature collection
    """

    # Load the general backend configuration
    cfg         = utils.load_yaml(CONFIG_PATH)
    vessel_cfg  = utils.load_yaml(VESSEL_CONFIG_PATH)

    # Create the bounding box, observe the order (lonlat)
    bbox = [lon_min, lat_min, lon_max, lat_max]

    # Convert time from datetime to timestamp
    start_date = pd.Timestamp(start_date)

    # Create the chart
    # Should possibly be pre-computed if computation is too slow
    chart = voyager.Chart(bbox, 
                          start_date, 
                          start_date+pd.Timedelta(duration, unit='days')).load(cfg['data']['path'], **cfg['chart'])
    
    # Create the model that steps throught time
    model = voyager.Model(duration, timestep, **cfg['model'])

    # Calculate the trajectories
    try: 
        results = voyager.Traverser.trajectory(
                    mode = mode.value,
                    craft = craft, 
                    duration = duration,
                    timestep = timestep, 
                    destination = [destination_lon, destination_lat], 
                    speed = speed, 
                    bbox = bbox, 
                    departure_point = [departure_lon, departure_lat], 
                    vessel_params=vessel_cfg,
                    chart = chart, 
                    model = model
                )

    except RuntimeError as re:
        raise HTTPException(status_code=418, detail=str(re))

    return results