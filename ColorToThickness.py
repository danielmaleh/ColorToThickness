import threading
import pandas as pd
import cv2
import numpy as np
import os
from tkinter import Tk, Button, Label, filedialog, messagebox, StringVar, Radiobutton, Entry

# Function to convert RGB to LAB color space
def rgb_to_lab(rgb):
    try:
        lab = cv2.cvtColor(np.uint8([[rgb]]), cv2.COLOR_RGB2LAB)
        return lab[0][0]
    except Exception as e:
        messagebox.showerror("Conversion Error", f"Failed to convert RGB to LAB: {e}")
        return None

# Function to normalize colors
def normalize_colors(average_rgb, average_lab, background_rgb, background_lab):
    try:
        normalized_rgb = tuple(np.round(np.clip(np.array(average_rgb) / np.array(background_rgb), 0, 255), 5))
        normalized_lab = tuple(np.round(np.clip(np.array(average_lab) / np.array(background_lab), 0, 255), 5))
        return normalized_rgb, normalized_lab
    except Exception as e:
        messagebox.showerror("Normalization Error", f"Failed to normalize colors: {e}")
        return None, None

# Class to create the GUI application
class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Lookup Table creation / Color to thickness mapping")
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.function_choice = self.create_radiobutton_group("Functionality:", ["Lookup Table Entry", "Map Image to Lookup Table"], 0)
        self.entry_choice = self.create_radiobutton_group("Entry Method:", ["Manual Entry", "Image-Based Entry"], 1)
        self.substrate_choice = self.create_radiobutton_group("Substrate Type:", ['Float', 'Borofloat', 'Si', 'D263'], 2, default='Float')

        self.background_image_loaded = False
        self.goldflake_image_loaded = False

        self.manual_entries = []
        self.background_rgb_entries = self.create_rgb_entries("Background RGB:", 4)
        self.goldflake_rgb_entries = self.create_rgb_entries("Gold Flake RGB:", 8)

        self.background_rgb_label = self.create_rgb_label("Background RGB:", 4)
        self.goldflake_rgb_label = self.create_rgb_label("Gold Flake RGB:", 8)

        self.background_image_button = self.create_button("Select Background Image", self.select_background_image, 3, 0)
        self.goldflake_image_button = self.create_button("Select Gold Flake Image", self.select_gold_flake_image, 3, 1)

        self.thickness_label = Label(root, text="Enter Thickness [nm]:")
        self.thickness_entry = Entry(root)

        self.create_button("Process", self.process_in_thread, 13, 0, colspan=3)
        self.create_button("Reset", self.reset_application, 14, 0, colspan=3)
        self.create_button("Remap Results", self.remap_results, 15, 0, colspan=3)

        self.update_entry_options()

    # Function to create radio button group
    def create_radiobutton_group(self, label_text, options, row, default=None):
        Label(self.root, text=label_text).grid(row=row, column=0, padx=10, pady=10)
        var = StringVar(self.root)
        var.set(default if default else options[0])
        for i, option in enumerate(options):
            Radiobutton(self.root, text=option, variable=var, value=option).grid(row=row, column=i + 1, padx=10, pady=10)
        var.trace_add('write', self.reset_on_mode_switch)
        return var
    
    # Function to create RGB entries
    def create_rgb_entries(self, label_text, row_start):
        Label(self.root, text=label_text).grid(row=row_start, column=0, padx=10, pady=5, sticky="W")
        entries = {color: Entry(self.root) for color in ["R", "G", "B"]}
        for i, (color, entry) in enumerate(entries.items()):
            entry.grid(row=row_start + 1, column=i + 1, padx=5, pady=5)
            self.manual_entries.append(entry)
        return entries
    
    # Function to create RGB label
    def create_rgb_label(self, label_text, row_start):
        Label(self.root, text=label_text).grid(row=row_start, column=0, padx=10, pady=5, sticky="W")
        label = Label(self.root, text="R: , G: , B: ", anchor="w")
        label.grid(row=row_start + 1, column=0, padx=5, pady=5, sticky="W", columnspan=3)
        return label
    
    # Function to create button
    def create_button(self, text, command, row, col, colspan=1):
        button = Button(self.root, text=text, command=command)
        button.grid(row=row, column=col, padx=10, pady=10, columnspan=colspan)
        return button

    # Function to reset on mode switch
    def reset_on_mode_switch(self, *args):
        self.reset_application(message="The application has been reset due to mode/substrate change.")

    # Function to reset the application
    def reset_application(self, message="The application has been reset."):
        self.background_image_loaded = False
        self.goldflake_image_loaded = False
        self.background_rgb_label.config(text="R: , G: , B: ")
        self.goldflake_rgb_label.config(text="R: , G: , B: ")
        for entry in self.manual_entries:
            entry.delete(0, "end")
        self.update_entry_options()
        self.root.title("Lookup Table creation / Color to thickness mapping")
        messagebox.showinfo("Reset", message)

    # Function to update entry options
    def update_entry_options(self, *args):
        entry_type = self.entry_choice.get()
        function_type = self.function_choice.get()

        if entry_type == "Manual Entry":
            self.background_image_button.grid_remove()
            self.goldflake_image_button.grid_remove()
            self.toggle_manual_entry_fields(True)
            if function_type == "Lookup Table Entry":
                self.thickness_label.grid(row=12, column=0, padx=10, pady=10)
                self.thickness_entry.grid(row=12, column=1, padx=10, pady=10)
            else:
                self.toggle_thickness_entry(False)
        else:
            self.toggle_manual_entry_fields(False)
            self.background_rgb_label.grid()
            self.goldflake_rgb_label.grid()
            self.background_image_button.grid(row=3, column=0, padx=10, pady=10)
            self.goldflake_image_button.grid(row=3, column=1, padx=10, pady=10)
            if function_type == "Lookup Table Entry":
                self.thickness_label.grid(row=12, column=0, padx=10, pady=10)
                self.thickness_entry.grid(row=12, column=1, padx=10, pady=10)
            else:
                self.toggle_thickness_entry(False)

    # Function to toggle manual entry fields
    def toggle_manual_entry_fields(self, show):
        for entry in self.manual_entries:
            if show:
                entry.grid()
            else:
                entry.grid_remove()
        if not show:
            self.background_rgb_label.grid_remove()
            self.goldflake_rgb_label.grid_remove()

    # Function to toggle thickness entry
    def toggle_thickness_entry(self, show):
        if show:
            self.thickness_label.grid()
            self.thickness_entry.grid()
        else:
            self.thickness_label.grid_remove()
            self.thickness_entry.grid_remove()

    # Function to select background image
    def select_background_image(self):
        threading.Thread(target=self._select_background_image).start()

    # Function to select gold flake image
    def _select_background_image(self):
        self.background_rgb, self.background_lab = self.get_color_values(downscale=True)
        if self.background_rgb is not None:
            self.background_image_loaded = True
            self.update_rgb_label(self.background_rgb_label, self.background_rgb)

    # Function to select gold flake image
    def select_gold_flake_image(self):
        threading.Thread(target=self._select_gold_flake_image).start()

    # Function to select gold flake image
    def _select_gold_flake_image(self):
        self.gold_flake_rgb, self.gold_flake_lab = self.get_color_values(downscale=True)
        if self.gold_flake_rgb is not None:
            self.goldflake_image_loaded = True
            self.update_rgb_label(self.goldflake_rgb_label, self.gold_flake_rgb)

    # Function to update RGB label
    def update_rgb_label(self, label, rgb_values):
        label.config(text=f"R: {rgb_values[0]}, G: {rgb_values[1]}, B: {rgb_values[2]}")

    # Function to process in thread
    def process_in_thread(self):
        threading.Thread(target=self.process).start()

    # Function to process
    def process(self):
        try:
            if self.function_choice.get() == "Lookup Table Entry":
                self.create_lookup_table_entry()
            else:
                if self.entry_choice.get() == "Image-Based Entry":
                    if not self.background_image_loaded or not self.goldflake_image_loaded:
                        messagebox.showerror("Error", "Please select both background and gold flake images.")
                        return
                self.map_image_to_lookup_table()
        except Exception as e:
            messagebox.showerror("Processing Error", f"An error occurred during processing: {e}")

    # Function to get color values
    def get_color_values(self, downscale=False):
        image_path = filedialog.askopenfilename(title="Select an image", filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp")])
        if not image_path:
            messagebox.showerror("Error", "No image selected.")
            return None, None

        image = cv2.imread(image_path)

        if downscale:
            image = self.resize_image(image, max_size=400)  # Downscale to speed up operations

        roi = select_roi_adjustable(image)
        if roi is None:
            messagebox.showerror("Error", "No ROI selected.")
            return None, None

        selected_area_rgb = image[roi[1]:roi[1] + roi[3], roi[0]:roi[0] + roi[2]]
        selected_area_lab = cv2.cvtColor(selected_area_rgb, cv2.COLOR_BGR2LAB)

        rgb = tuple(map(int, np.mean(selected_area_rgb, axis=(0, 1))))
        lab = tuple(map(int, np.mean(selected_area_lab, axis=(0, 1))))

        self.selected_image_name = os.path.splitext(os.path.basename(image_path))[0]

        return rgb, lab

    # Function to resize image
    def resize_image(self, image, max_size=800):
        height, width = image.shape[:2]
        if max(width, height) > max_size:
            scale = max_size / max(width, height)
            image = cv2.resize(image, (int(width * scale), int(height * scale)))
        return image

    # Function to create lookup table entry
    def create_lookup_table_entry(self):
        substrate = self.substrate_choice.get()
        file_name = f'lookup_table_{substrate}.csv'

        lookup_table = pd.read_csv(file_name) if os.path.exists(file_name) else pd.DataFrame(columns=['R', 'G', 'B', 'L', 'a', 'b', 'Thickness [nm]'])

        if self.entry_choice.get() == "Manual Entry":
            background_rgb = self.get_rgb_from_entries(self.background_rgb_entries)
            gold_flake_rgb = self.get_rgb_from_entries(self.goldflake_rgb_entries)
            background_lab = rgb_to_lab(background_rgb)
            gold_flake_lab = rgb_to_lab(gold_flake_rgb)
            normalized_rgb, normalized_lab = normalize_colors(gold_flake_rgb, gold_flake_lab, background_rgb, background_lab)
        else:
            normalized_rgb, normalized_lab = normalize_colors(self.gold_flake_rgb, self.gold_flake_lab, self.background_rgb, self.background_lab)
        
        try:
            thickness = float(self.thickness_entry.get())
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid thickness value.")
            return
        
        new_entry = pd.DataFrame({
            'R': [normalized_rgb[0]], 'G': [normalized_rgb[1]], 'B': [normalized_rgb[2]],
            'L': [normalized_lab[0]], 'a': [normalized_lab[1]], 'b': [normalized_lab[2]],
            'Thickness [nm]': [thickness]
        })

        if all(column in lookup_table.columns for column in new_entry.columns):
            lookup_table = pd.concat([lookup_table, new_entry], ignore_index=True)
        else:
            messagebox.showerror("Error", "Mismatch in DataFrame columns.")
            return

        lookup_table.to_csv(file_name, index=False)
        messagebox.showinfo("Saved", f"Lookup table saved to '{file_name}'.")

    # Function to get RGB from entries
    def get_rgb_from_entries(self, entries):
        try:
            r = int(entries["R"].get())
            g = int(entries["G"].get())
            b = int(entries["B"].get())
            
            if not all(0 <= value <= 255 for value in [r, g, b]):
                raise ValueError("RGB values must be between 0 and 255.")

            return r, g, b
        except ValueError as e:
            messagebox.showerror("Error", f"Please enter valid RGB values (0-255): {e}")
            return None

    # Function to close the application
    def on_closing(self):
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.root.destroy()

    # Function to map image to lookup table
    def map_image_to_lookup_table(self):
        if self.entry_choice.get() == "Manual Entry":
            background_rgb = self.get_rgb_from_entries(self.background_rgb_entries)
            gold_flake_rgb = self.get_rgb_from_entries(self.goldflake_rgb_entries)
            background_lab = rgb_to_lab(background_rgb)
            gold_flake_lab = rgb_to_lab(gold_flake_rgb)
        else:
            background_rgb, background_lab = self.background_rgb, self.background_lab
            gold_flake_rgb, gold_flake_lab = self.gold_flake_rgb, self.gold_flake_lab

        substrate = self.substrate_choice.get()
        file_name = f'lookup_table_{substrate}.csv'
        
        if not os.path.exists(file_name):
            messagebox.showerror("Error", f"Lookup table for substrate '{substrate}' not found.")
            return
        
        lookup_table = pd.read_csv(file_name)

        normalized_rgb, normalized_lab = normalize_colors(gold_flake_rgb, gold_flake_lab, background_rgb, background_lab)

        thickness_rgb, match_type_rgb = self.find_closest_color(normalized_rgb, lookup_table, 'RGB')
        thickness_lab, match_type_lab = self.find_closest_color(normalized_lab, lookup_table, 'LAB')

        image_name = self.selected_image_name if self.entry_choice.get() == "Image-Based Entry" else "Manual Entry"

        # Prepare notes for the results
        note_rgb = match_type_rgb
        note_lab = match_type_lab

        results = pd.DataFrame({
            'Image': [image_name],
            'Substrate': [substrate],
            'Average_RGB': [normalized_rgb],
            'Average_LAB': [normalized_lab],
            'Thickness_RGB [nm]': [thickness_rgb],
            'Thickness_LAB [nm]': [thickness_lab],
            'Note_RGB': [note_rgb],
            'Note_LAB': [note_lab]
        })

        results_file = 'results.csv'
        results.to_csv(results_file, mode='a' if os.path.exists(results_file) else 'w', header=not os.path.exists(results_file), index=False)
        messagebox.showinfo("Results", f"Results saved to '{results_file}'.")

        results_text = f"Normalized RGB values: {normalized_rgb}\nNormalized LAB values: {normalized_lab}\n"
        results_text += f"Mapped thickness for RGB: {thickness_rgb} nm ({note_rgb})\n"
        results_text += f"Mapped thickness for LAB: {thickness_lab} nm ({note_lab})"
        messagebox.showinfo("Results", results_text)

    # Function to remap results
    def remap_results(self):
        try:
            results_file = 'results.csv'
            if not os.path.exists(results_file):
                messagebox.showerror("Error", f"No results file found. Please generate results first.")
                return
            
            # Load the existing results
            results = pd.read_csv(results_file)
            
            # Iterate over each row in the results to remap the thicknesses
            updated_results = []
            for index, row in results.iterrows():
                normalized_rgb = tuple(map(float, row['Average_RGB'].strip('()').split(',')))
                normalized_lab = tuple(map(float, row['Average_LAB'].strip('()').split(',')))

                # Determine the substrate from the row, not from the current GUI selection
                substrate = row['Substrate']
                lookup_table_file = f'lookup_table_{substrate}.csv'
                
                if not os.path.exists(lookup_table_file):
                    messagebox.showerror("Error", f"Lookup table for substrate '{substrate}' not found.")
                    return
                
                lookup_table = pd.read_csv(lookup_table_file)

                # Remap using the correct lookup table based on the stored substrate
                thickness_rgb, match_type_rgb = self.find_closest_color(normalized_rgb, lookup_table, 'RGB')
                thickness_lab, match_type_lab = self.find_closest_color(normalized_lab, lookup_table, 'LAB')

                # Update only the thickness and notes in the results
                updated_row = row.copy()
                updated_row['Thickness_RGB [nm]'] = thickness_rgb
                updated_row['Thickness_LAB [nm]'] = thickness_lab
                updated_row['Note_RGB'] = match_type_rgb
                updated_row['Note_LAB'] = match_type_lab

                updated_results.append(updated_row)

            # Consolidate results to remove any duplicates or near-identical entries
            final_results = pd.DataFrame(updated_results).drop_duplicates()

            # Save the updated and consolidated results back to the file
            final_results.to_csv(results_file, index=False)
            messagebox.showinfo("Success", "Results have been remapped and consolidated.")
        
        except Exception as e:
            messagebox.showerror("Error", f"Failed to remap results: {e}")

    # Function to find closest color
    def find_closest_color(self, color_value, lookup_table, color_space='RGB', threshold=5):
        try:
            if color_space == 'RGB':
                diff = lookup_table[['R', 'G', 'B']] - color_value
            else:
                diff = lookup_table[['L', 'a', 'b']] - color_value
            
            distance = np.sqrt((diff**2).sum(axis=1))
            min_distance = distance.min()
            
            # Find all closest matches
            closest_indices = distance[distance == min_distance].index
            thicknesses = lookup_table.loc[closest_indices, 'Thickness [nm]'].astype(str).tolist()
            
            # Determine match type
            exact_match = False
            if len(closest_indices) == 1:
                closest_diff = diff.loc[closest_indices].iloc[0]
                exact_match = (closest_diff == 0).all()
            
            # Multiple matches if more than one thickness is found
            if len(thicknesses) > 1:
                match_type = "Multiple matches"
            elif exact_match:
                match_type = "Exact match"
            elif min_distance <= threshold:
                match_type = "Approximate match"
            else:
                match_type = "No match"
            
            # Join thicknesses
            thickness_str = "/".join(thicknesses)
            
            return thickness_str, match_type
        except Exception as e:
            messagebox.showerror("Error", f"Failed to find closest color: {e}")
            return None, "Error"

# Function to select ROI adjustable
def select_roi_adjustable(image):
    max_size = 800
    height, width = image.shape[:2]
    if max(width, height) > max_size:
        scale = max_size / max(width, height)
        image = cv2.resize(image, (int(width * scale), int(height * scale)))

    cv2.namedWindow('Select ROI', cv2.WINDOW_NORMAL)
    cv2.resizeWindow('Select ROI', 800, 600)
    roi = cv2.selectROI('Select ROI', image, fromCenter=False, showCrosshair=True)
    cv2.destroyAllWindows()

    return roi if roi != (0, 0, 0, 0) else None

if __name__ == "__main__":
    root = Tk()
    app = App(root)
    root.mainloop()