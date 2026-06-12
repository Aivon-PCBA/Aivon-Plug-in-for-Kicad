# AIVON Plug-in for KiCad

### Send your layout to AIVON for instant production with just one click.

Click this plugin for high quality prototyping and assembly services, AIVON will commit to meeting your needs to the greatest extent.

When you click AIVON Plug-in button, we will export these files in your project:
1. Gerber files in correct format for production
2. IPC-Netlist file
3. Bom-file that includes all information of components
4. Pick and Place-file used in assembly

You can place an order immediately after uploading the files (usually only takes a few seconds). Our engineers will double check the files before production.

**Note: For KiCad 8 and later, you can place assembly orders directly. Please add component MPN in schematic footprint fields and run "Update Board from Schematic".**

### Manual installation

Download the latest ZIP from this repository, then open the "Plugin and Content Manager" from the KiCad main window and install the ZIP file via "Install from File".

### About BOM

We can get all information of components used in your design. To speed up component quotation, please provide:
1. Designator (necessary)
2. Quantity (necessary)
3. MPN/Part Number (necessary)
4. Package/Footprint (necessary)
5. Manufacturer (optional)
6. Description/value (optional)

You can add properties in your schematic footprint fields. The plugin also recognizes the `Aivon_MPN` field.

### About AIVON

AIVON is a one-stop PCB manufacturing and assembly platform. Standard PCB prototypes can be built in 24 hours. Visit [www.aivon.com](https://www.aivon.com) for online quote and order tracking.

Based on the MIT-licensed AIVON KiCad plugin.
