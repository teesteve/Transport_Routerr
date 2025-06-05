import tkinter as tk
from tkinter import ttk, messagebox
import random  # For simulating traffic conditions
from route_logic_backup import RouteGenerator  # The class file
from map_renderer import MapRenderer
from multiprocessing import Process
import os
import subprocess

class TransportRouteApp:

    """ GUI application for finding and displaying transport routes.
        Integrates geocoding, route generation, map rendering and user reviews."""

    def __init__(self, root):
        self.root = root
        self.root.title("Transport Route Finder")
        self.root.geometry("500x700")

        self.api_key = 'api_key'
        self.route_generator = RouteGenerator(self.api_key)
        self.map_renderer = MapRenderer()

        self.output_text = tk.StringVar()
        self.directions_text = tk.StringVar()
        self.create_widgets()

    def create_widgets(self):

        """ Creates and packs all Tkinter widgets into the root window"""

        tk.Label(self.root, text="Start Location (e.g., Unilag):").pack(pady=5)
        self.start_entry = tk.Entry(self.root, width=40)
        self.start_entry.pack()

        tk.Label(self.root, text="Destination (e.g., Ikoyi):").pack(pady=5)
        self.end_entry = tk.Entry(self.root, width=40)
        self.end_entry.pack()

        tk.Label(self.root, text="Transport Mode:").pack(pady=5)
        self.transport_mode = ttk.Combobox(self.root, values=["Car", "Walk", "Bike", "Train"])
        self.transport_mode.set("Car")
        self.transport_mode.pack()

        tk.Button(self.root, text="Generate Route", command=self.generate_route).pack(pady=10)

        tk.Label(self.root, textvariable=self.output_text, wraplength=400, justify="left").pack(pady=10)

        tk.Label(self.root, text="Turn-by-Turn Instruction").pack(pady=5)

        text_frame = tk.Frame(self.root)
        text_frame.pack(pady=5, fill="both", expand=True)

        self.directions_text_widget = tk.Text(text_frame, wrap="word", height=10, width=55)
        self.directions_text_widget.pack(side="left", fill="both", expand=True)

        scrollbar = tk.Scrollbar(text_frame, command=self.directions_text_widget.yview)
        scrollbar.pack(side="right", fill="y")
        self.directions_text_widget.config(yscrollcommand=scrollbar.set, state="disabled")

        # Reviews Section
        tk.Label(self.root, text="Reviews:").pack(pady=5)
        self.review_entry = tk.Text(self.root, height=5, width=40)
        self.review_entry.pack()

        tk.Button(self.root, text="Submit Review", command=self.submit_review).pack(pady=5)
        tk.Button(self.root, text="View All Reviews", command=self.view_reviews).pack(pady=5)

    def generate_route(self):
        """ Handles geocoding, route calculation, traffic simulation, direction parsing
            and map rendering"""
        start_place = self.start_entry.get()
        end_place = self.end_entry.get()
        mode = self.transport_mode.get().lower()

        if not start_place or not end_place:
            messagebox.showwarning("Input Error", "Please enter both start and destination.")
            return

        start_coords = self.route_generator.geocode(start_place)
        end_coords = self.route_generator.geocode(end_place)

        print("Start coords:", start_coords)
        print("End coords:", end_coords)

        if not start_coords or not end_coords:
            self.output_text.set("Could not find one or both locations.")
            return

        mode_profile = {
            'car': 'driving-car',
            'walk': 'foot-walking',
            'bike': 'cycling-regular'
        }.get(mode, 'driving-car')

        distance, duration, route_coords, steps = self.route_generator.get_route_info(start_coords, end_coords, mode_profile)

        if distance is None or duration is None:
            self.output_text.set("❌ Could not retrieve route. One or both points may be too far from a road.\nTry a more popular or central location.")
            return

        # Simulated traffic condition
        traffic_condition = {
            "Free Flow": 0.9,
            "Moderate": 1.2,
            "Heavy": 1.5,
        }
        traffic_status = random.choice(list(traffic_condition.keys()))
        traffic_multiplier = traffic_condition[traffic_status]
        durations = round(duration * traffic_multiplier, 2)

        # Display route info
        self.output_text.set(
            f"Route from {start_place} to {end_place}:\n\n"
            f"Distance: {distance} km\nEstimated Time: {duration} minutes\n"
            f"Traffic: {traffic_status} (Adjusted Time: {durations} minutes)"
        )
        directions_output = ""
        for i, step in enumerate(steps, 1):
            directions_output += f"{i}. {step['instruction']} ({round(step['distance'], 1)} meters)\n"

        self.directions_text_widget.config(state="normal")
        self.directions_text_widget.delete("1.0", tk.END)
        self.directions_text_widget.insert(tk.END, directions_output)
        self.directions_text_widget.config(state="disabled")

        # Render and display map
        map_obj = self.map_renderer.show_route_map(route_coords, start_place, end_place)
        if map_obj:
            self.map_renderer.save_html(map_obj)
            # Launch in separate process to avoid freezing GUI
            Process(target=self.map_renderer.launch_map_view).start()

    def submit_review(self):
        """ Saves user review to a local text file"""
        review_text = self.review_entry.get("1.0", tk.END).strip()
        if review_text:
            try:
                with open("reviews.txt", "a", encoding="utf-8") as file:
                    file.write(f"{review_text}\n\n")
                self.review_entry.delete("1.0", tk.END)
                messagebox.showinfo("Thank you!", "Review submitted and saved to file.")
            except Exception as e:
                messagebox.showerror("Error", f"Could not save review:\n{e}")
        else:
            messagebox.showwarning("Empty Review", "Please write something before submitting.")

    def view_reviews(self):
        """ Opens the reviews file with the default OS file viewer"""
        filepath = "reviews.txt"
        if os.path.exists(filepath):
            try:
                os.startfile(filepath)  # Windows
            except AttributeError:
                try:
                    subprocess.call(["open", filepath])  # macOS
                except:
                    subprocess.call(["xdg-open", filepath])  # Linux
        else:
            messagebox.showinfo("No Reviews", "No reviews have been submitted yet.")



if __name__ == "__main__":
    root = tk.Tk()
    app = TransportRouteApp(root)
    root.mainloop()
