import os
from tkinter import messagebox
import folium
import webview

class MapRenderer:
    """ Renders a route map using Folium and displays it in a webview"""
    def __init__(self):
        self.html_path = "route_map.html"

    def show_route_map(self, route_coords, start_name, end_name):
        """ Creates a Folium map with start and end markers and the route polyline.
            Returns folium.map: A map object for rendering or None on failure"""
        if not route_coords:
            messagebox.showerror("Map Error", "No route coordinates to display.")
            return

        latlon_coords = [[lat, lon] for lon, lat in route_coords]
        start_latlon = latlon_coords[0]

        m = folium.Map(location=start_latlon, zoom_start=12)
        folium.Marker(latlon_coords[0], tooltip=f"Start: {start_name}", icon=folium.Icon(color='green')).add_to(m)
        folium.Marker(latlon_coords[-1], tooltip=f"End: {end_name}", icon=folium.Icon(color='red')).add_to(m)
        folium.PolyLine(latlon_coords, color="blue", weight=5).add_to(m)
        return m

    def save_html(self, map_obj):
        """ Saves the generated map as an HTML file.
            Parameters: map_obj (folium.Map): Map object to save
            Returns str: Full file path to the saved HTML"""
        map_obj.save(self.html_path)
        return os.path.abspath(self.html_path)

    def launch_map_view(self):
        """ Opens the saved HTML file in a separate webview window.
            Raises: FileNotFoundError: If HTML map file is missing."""
        if not os.path.exists(self.html_path):
            raise FileNotFoundError("Map HTML file not found. Did you call save_html()?")
        webview.create_window("Route Map", f"file://{os.path.abspath(self.html_path)}")
        webview.start()
