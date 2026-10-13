// Hackpad 16 enclosure — editable OpenSCAD source
// Units: mm. Select one part in the Customizer (or via -D part="...")
// and render (F6) before exporting an STL.

part = "lower_tray"; // [lower_tray, switch_plate, service_hatch, encoder_bezel, hackpad16_badge]
$fn = 72;

board = 100;
clearance = 0.2;
margin = 10;
outer = board + 2*margin;
floor_t = 3;
wall_h = 10;
base_h = floor_t + wall_h;
plate_t = 3;
holes = [[15,15],[105,35],[18,94],[105,105]];
keys = [for (r=[0:3], c=[0:3]) [30+19.05*c,41+19.05*r]];
encoder = [87,18];
usb_x = 35;

module rbox(size, radius=2) {
    // Centered rounded rectangular prism with exact outside dimensions.
    minkowski() {
        cube([size[0]-2*radius, size[1]-2*radius, max(0.01,size[2]-2*radius)], center=true);
        sphere(r=radius, $fn=16);
    }
}

module lower_tray() {
    difference() {
        // Hollow tray with a 3 mm bottom and 10 mm rim.
        translate([60,60,base_h/2]) rbox([outer,outer,base_h],7);
        translate([60,60,floor_t+(wall_h+1)/2]) rbox([board+2*clearance,board+2*clearance,wall_h+1],3.5);
        // USB-C opening at the front edge.
        translate([usb_x,4.5,9.4]) rbox([16,12,8.4],1.2);
        // Underside service hatch opening.
        translate([35,22,1.5]) rbox([24,24,4],2);
        for (dx=[-15,15], dy=[-15,15])
            translate([35+dx,22+dy,1.5]) cylinder(d=1.8,h=3.5,center=true,$fn=48);
    }
    // PCB standoffs integrated with the tray floor.
    for (p=holes) difference() {
        translate([p[0],p[1],7]) cylinder(d=7.4,h=8,center=true);
        translate([p[0],p[1],7]) cylinder(d=2.7,h=8.3,center=true,$fn=64);
    }
}

module switch_plate() {
    difference() {
        translate([60,60,plate_t/2]) rbox([outer,outer,plate_t],7);
        for (p=keys) translate([p[0],p[1],plate_t/2]) rbox([14.4,14.4,plate_t+2],0.25);
        translate([encoder[0],encoder[1],plate_t/2]) cylinder(d=7.4,h=plate_t+2,center=true);
        // Flush accent-ring recess, 0.8 mm deep.
        translate([encoder[0],encoder[1],plate_t-0.4]) difference() {
            cylinder(d=20,h=0.9,center=true);
            cylinder(d=16.3,h=1.2,center=true);
        }
        for (p=holes) {
            translate([p[0],p[1],plate_t/2]) cylinder(d=3.4,h=plate_t+2,center=true,$fn=64);
            translate([p[0],p[1],plate_t-0.4]) cylinder(d=6,h=0.9,center=true,$fn=64);
        }
        translate([usb_x,4.5,plate_t/2]) rbox([16,12,plate_t+2],1);
        translate([60,112,plate_t-0.35]) rbox([44,10,0.9],1.2);
    }
}

module service_hatch() {
    difference() {
        translate([35,22,0.9]) rbox([34,34,1.8],3);
        for (dx=[-15,15],dy=[-15,15])
            translate([35+dx,22+dy,0.9]) cylinder(d=2.2,h=2.4,center=true,$fn=48);
        // Shallow inset panel line.
        translate([35,22,1.62]) difference() {
            rbox([30,30,0.45],2.5);
            rbox([27,27,0.7],2);
        }
    }
}

module encoder_bezel() {
    difference() {
        cylinder(d=19.8,h=0.58);
        translate([0,0,-0.1]) cylinder(d=17,h=0.8);
    }
}

module hackpad16_badge() {
    // Raised lettering uses OpenSCAD's system font; change font if unavailable.
    union() {
        translate([0,0,0.34]) rbox([43.6,9.6,0.68],1);
        translate([0,0,0.68]) linear_extrude(height=0.18)
            text("Tejas got not chill\nHackpad", size=3.1, halign="center", valign="center", spacing=1, font="Liberation Sans:style=Bold");
    }
}

if (part == "lower_tray") lower_tray();
else if (part == "switch_plate") switch_plate();
else if (part == "service_hatch") service_hatch();
else if (part == "encoder_bezel") encoder_bezel();
else if (part == "hackpad16_badge") hackpad16_badge();
