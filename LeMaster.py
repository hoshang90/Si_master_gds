#!/usr/bin/python3
import gdspy
from picwriter import toolkit as tk
import picwriter.components as pc
import LesStamps

inch=2
#-----------------------------------------------
circle = gdspy.Round((0, 0), radius=(inch/2)*25400, tolerance=0.01)
#------------------------------------
MyStamps=LesStamps.Stamps()
top = gdspy.Cell("top")

MyStamps.MakesStampFromMotif(top,MyStamps.LinesCell(name='Lines_Grating'),X0=-16_000,Y0=0)
MyStamps.MakesStampFromMotif(top,MyStamps.LinesCell(name='Lines_Taper'),X0=0,Y0=0)
# X0=20_000,Y0=0)

MyStamps.MakesStampFromMotif(top,MyStamps.Spirales(name='Spiral_Grating'),X0=-16_000,Y0=-20_000)
MyStamps.MakesStampFromMotif(top,MyStamps.Spirales(name='Spiral_Taper'),X0=0,Y0=-20_000)

tk.add(top, circle)#circle for the wafer size

tk.build_mask(top, MyStamps.wgt[1], final_layer=3, final_datatype=0)
gdspy.write_gds('tests.gds', unit=1.0e-6, precision=1.0e-9)
# gds viewer KLayout 
# gdspy.LayoutViewer()
