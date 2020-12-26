#!/usr/bin/python3
import gdspy
from picwriter import toolkit as tk
import picwriter.components as pc

import LesStamps 
#-----------------------------------------------

#------------------------------------
MyStamps=LesStamps.Stamps()
top = gdspy.Cell("top")

LesLignes=MyStamps.LinesCell()  #-- waveguides with different w


MyStamps.MakesStampFromMotif(top,LesLignes,X0=0)
MyStamps.MakesStampFromMotif(top,LesLignes,Y0=20000)
MyStamps.MakesStampFromMotif(top,MyStamps.Spirales(),X0=20000)


tk.build_mask(top, MyStamps.wgt[1], final_layer=3, final_datatype=0)
#top.write_gds('top.gds', unit=1.0e-6, precision=1.0e-9)
gdspy.write_gds('test.gds', unit=1.0e-6, precision=1.0e-9)
# gds viewer KLayout 
#gdspy.LayoutViewer()
