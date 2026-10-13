# Hackpad 16 — OpenSCAD enclosure

Editable, parametric OpenSCAD design for the Hackpad 16 enclosure. Open `hackpad16_case.scad` in [OpenSCAD](https://openscad.org/), choose a part from the `part` selector, press **F6** to render, then use **File → Export → Export as STL**.

## Parts

- `lower_tray` — lower case, PCB pocket, standoffs, USB-C opening, and service access opening
- `switch_plate` — 4×4 switch plate, encoder opening, screw holes/counterbores, USB notch, badge recess
- `service_hatch` — removable underside cover
- `encoder_bezel` — optional accent ring
- `hackpad16_badge` — separate raised-text badge

The source uses millimeters. To export using the OpenSCAD command line, run from this directory:

```sh
openscad -o lower_tray.stl -D 'part="lower_tray"' hackpad16_case.scad
openscad -o switch_plate.stl -D 'part="switch_plate"' hackpad16_case.scad
openscad -o service_hatch.stl -D 'part="service_hatch"' hackpad16_case.scad
openscad -o encoder_bezel.stl -D 'part="encoder_bezel"' hackpad16_case.scad
openscad -o hackpad16_badge.stl -D 'part="hackpad16_badge"' hackpad16_case.scad
```

## Starting dimensions

- PCB cavity: 100.4 × 100.4 mm
- Outer case: 120 × 120 mm
- Tray floor: 3 mm; tray height: 13 mm
- Top plate: 3 mm thick
- Switch layout: 4 × 4 at 19.05 mm pitch; 14.4 mm openings
- PCB mounting holes follow the asymmetric positions encoded in the source
