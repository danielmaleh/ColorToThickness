# Color to Thickness Mapping for Gold Flakes

This project provides a Python GUI application to create a lookup table that maps RGB and LAB color values of gold flakes observed under an optical microscope to their corresponding thicknesses. Additionally, the application allows mapping of the colors from an image to the corresponding thickness using the previously created lookup table.

## Table of Contents

- [Color to Thickness Mapping for Gold Flakes](#color-to-thickness-mapping-for-gold-flakes)
  - [Table of Contents](#table-of-contents)
  - [Introduction](#introduction)
  - [Prerequisites](#prerequisites)
  - [Overview](#overview)
  - [Usage](#usage)
    - [Creating the Lookup Table](#creating-the-lookup-table)
    - [Mapping Colors to Thickness](#mapping-colors-to-thickness)
  - [Output](#output)
  - [Creating an Executable](#creating-an-executable)
  - [Contributing](#contributing)
  - [License](#license)

## Introduction

The aim of this project is to assist in research involving the characterization of gold flakes by correlating their observed colors under a microscope to their thickness. The GUI application allows for easy creation of a lookup table and mapping colors from images to thickness using this table.

## Prerequisites

Ensure you have Python 3.x installed. You’ll also need to install the following Python packages:

```bash
pip install opencv-python-headless numpy pandas
```

## Overview

The application provides a graphical user interface (GUI) to perform the following tasks:

1. **Creating the Lookup Table**: 
   - Input RGB and LAB values, either manually or from images, along with the corresponding thickness values. 
   - The lookup table is saved in a CSV file based on the selected substrate.

2. **Mapping Color to Thickness**: 
   - Load an image of gold flakes, select a region of interest (ROI), and map the average RGB color of the selected area to the corresponding thickness using the lookup table. 
   - The results are stored in a CSV file.

## Usage

### Creating the Lookup Table

1. Run the application by executing the script:

   ```bash
   python color_to_thickness_mapping.py
   ```

2. In the GUI, select the substrate type from the options provided (e.g., Float, Borofloat, Si, D263).

3. Choose the entry method:
   - **Manual Entry**: Input RGB values (0-255) and corresponding thickness manually.
   - **Image-Based Entry**: Select an image and an ROI. The RGB and LAB values will be automatically extracted from the ROI, and then you input the measured thickness for that area.

4. Click "Process" to add the data to the lookup table. The table is saved as `lookup_table_SUBSTRATE.csv`, where `SUBSTRATE` is the selected substrate type.

### Mapping Colors to Thickness

1. Place the image file (e.g., `gold_flakes_image.jpg`) in the same directory as the script.

2. Run the application and select "Map Image to Lookup Table" in the GUI.

3. Load an image and select a region of interest (ROI) using your mouse.

4. The application will calculate the average RGB color of the selected area and map it to the corresponding thickness using the lookup table.

5. The results are saved in `results.csv`.

## Output

- **`lookup_table_SUBSTRATE.csv`**: Contains the lookup table mapping RGB and LAB values to thicknesses.
- **`results.csv`**: Contains the results of the color-to-thickness mapping for each image.

## Creating an Executable

To create a standalone executable for this application:

1. Install PyInstaller if you haven't already:

   ```bash
   pip install pyinstaller
   ```

2. Run PyInstaller with the following command:

   ```bash
   pyinstaller --onefile --noconsole color_to_thickness_mapping.py
   ```

3. The executable will be located in the `dist` folder. You can distribute this executable without needing Python installed on the target machine.

## Contributing

If you would like to contribute to this project, feel free to submit a pull request or open an issue to discuss any changes or improvements.

## License

Daniel Abraham Elmaleh - 2024 [EPFL](https://www.epfl.ch/en/)