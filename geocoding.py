import time
import numpy as np
from folium.plugins.marker_cluster import MarkerCluster
import pandas as pd
import fontawesome as fa
import folium
import folium.plugins as plugins
from geopy import Nominatim
from geopy.extra.rate_limiter import RateLimiter

# Measuer Run Time
start_time = time.time()

# ====================================== Control panel ============================================
Number_of_Addresses = "Many"                                    # It's either 'One' or 'Many'.
starting_location = [46.20218520609474, 16.599402507819985]     # Takes form of [Latitude, Longitude]
starting_location_zoom = 4                                      # Takes values from 1 to 18
manual_address = "Papaflessa 65 Galatsi, Athens, Greece"        # Set Manually an address while Number_of_Addresses is set to 'One'.
delay_time_in_seconds = 0.5                                     # Set the delay of requests from geopy server (less than 0.5 pointless)
toggle_minimap_display = True                                   # It's either 'True or 'False'.
toggle_draw_toolkit = True                                      # Draw Toolkit
# =================================================================================================

# Form and Name of the Geocoder
locator = Nominatim(user_agent="Geocoder")

# Define Folium's map settings
folium_map = folium.Map(location=starting_location,
                        zoom_start=starting_location_zoom,
                        max_bounds=True)

# Create Themes with LayerControl for Folium Map
folium.TileLayer('openstreetmap').add_to(folium_map)
folium.TileLayer('Stamen Terrain').add_to(folium_map)
folium.TileLayer('Cartodbpositron').add_to(folium_map)
folium.TileLayer('CartoDB dark_matter').add_to(folium_map)
folium.TileLayer('stamenwatercolor').add_to(folium_map)
folium.TileLayer('stamentoner').add_to(folium_map)

if (Number_of_Addresses == "One"):   
    location = locator.geocode(manual_address)
    print("Latitude = {}, Longitude = {}".format(location.latitude, location.longitude))

    latitude = location.latitude
    longitude = location.longitude

    folium.Marker(location=[latitude, longitude]).add_to(folium_map)
    folium.LayerControl().add_to(folium_map)
    folium_map.save("map.html")
    

elif (Number_of_Addresses == "Many"):
    df = pd.read_csv("/home/varoth/Desktop/Work/Geoploting/Geocoding/addresses.csv")

    # Focusing data needed for geocoding into one column
    df["full_address"] = df.Address + "," + df.City + "," + df.Country

    locator = Nominatim(user_agent="Geocoder")
    geocode = RateLimiter(locator.geocode, min_delay_seconds=delay_time_in_seconds)
    df["Location"] = df["full_address"].apply(geocode)
    df["Point"] = df["Location"].apply(lambda loc: tuple(loc.point) if loc else None)
    df[["Latitude", "Longitude", "Altitude"]] = pd.DataFrame(df["Point"].tolist(), index=df.index)

    # Shape the data
    rows, cols = df.shape

    # Filter for Broken Addresses
    nan_value = float("NaN")
    df.replace("", nan_value, inplace=True)

    coordinates = df[["full_address", "Latitude", "Longitude"]]

    na_free = coordinates.dropna()
    broken_addresses = df[~coordinates.index.isin(na_free.index)]

    df.dropna(subset = ["Latitude"], inplace=True)
    df.dropna(subset = ["Longitude"], inplace=True)
    df.dropna(subset = ["full_address"], inplace=True)

    # Data from Somewhere
    varka_data = {"Latitude": [12.05],
                  "Longitude": [-23.58]}
    boat_data = pd.DataFrame(varka_data, columns = ["Latitude", "Longitude"])

    building_data = {"Latitude": [32.05],
                  "Longitude": [8.58]}
    corp_data = pd.DataFrame(building_data, columns = ["Latitude", "Longitude"])

    # Create Output csv files
    df.to_csv("coordinates.csv")
    broken_addresses.to_csv("broken_coordinates.csv")

    # Folium Groups
    customers = folium.FeatureGroup(name="Customers")
    ships = folium.FeatureGroup(name="Ships")
    headquarters = folium.FeatureGroup(name="Corporate Headquarters")
    heatmap = folium.FeatureGroup(name='Corona Virus Spread')

    # Icons of Every Group
    customers_icon = plugins.BeautifyIcon(icon='plane', border_color='#b3334f', text_color='#b3334f')

    # for row in df.full_address():
    labeled_popups = df["Address"].astype(str)

    # Create all Group's Icons from "https://fontawesome.com/v4.7.0/icons/"
    customers_icons = [folium.Icon(icon="user", prefix="fa", color='green') for _ in range(rows)]
    ships_icons = [folium.Icon(icon="ship", prefix="fa", color='blue') for _ in range(1)]
    headquarters_icons = [folium.Icon(icon="coffee", prefix="fa", color='orange') for _ in range(1)]

    # Create all Group's Labels
    customers_labels = df["Address"].astype(str)

    # Shape df
    new_rows, new_cols = df.shape

    # Data of Folium Map
    customers_data = list(zip(df['Latitude'].values, df['Longitude'].values))
    ship_data = list(zip(boat_data['Latitude'].values, boat_data['Longitude'].values))
    headquarters_data = list(zip(corp_data['Latitude'].values, corp_data['Longitude'].values))
    heatmap_data = (np.random.normal(size=(100, 3)) * np.array([[1, 1, 1]]) + np.array([[48, 5, 1]]) ).tolist()

    customers.add_child(MarkerCluster(locations=customers_data, icons=customers_icons)).add_to(folium_map)
    
    # Add Data to Folium Map
    # customers.add_child(MarkerCluster(location=customers_data, icons=customers_icons)).add_to(folium_map)
    # for i in range(0,len(customers_labels)):
    #      folium.Marker(location=customers_data[i], popup=customers_labels.iloc[i]).add_to(customers)
    ships.add_child(MarkerCluster(locations=ship_data, icons=ships_icons)).add_to(folium_map)
    headquarters.add_child(MarkerCluster(locations=headquarters_data, icons=headquarters_icons)).add_to(folium_map)

    # HeatMap   --> yes this is mostly for fun!
    # heatmap.add_child(plugins.HeatMap(heatmap_data)).add_to(folium_map)
    # plugins.HeatMap(heatmap_data).add_to(folium_map) 

    # =============================== Create Folium's Map attributes ==============================
    # Add Terminator to Folium Map if necessary
    # plugins.Terminator().add_to(folium_map)

    # Create Fullscreen Button
    plugins.Fullscreen(
    position="topright",
    title="Expand me",
    title_cancel="Exit me",
    force_separate_button=True
    ).add_to(folium_map)

    # Create Minimap
    minimap = plugins.MiniMap(toggle_display=toggle_minimap_display)
    folium_map.add_child(minimap)

    # Locate Control
    plugins.LocateControl(auto_start=False).add_to(folium_map)

    # Create Draw Toolkit
    draw = plugins.Draw(export=toggle_draw_toolkit)
    draw.add_to(folium_map)
    # =============================================================================================

    # Save Folium Map
    folium.LayerControl().add_to(folium_map)
    folium_map.save("map.html")

else:
    print("Please insert a valid 'Number_of_Addresses' input, either 'One' or 'Many'.")

print("Process finished --- %s seconds ---" % (time.time() - start_time))
