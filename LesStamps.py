#!/usr/bin/python3
import gdspy
from picwriter import toolkit as tk
import picwriter.components as pc
import numpy as np
#-----------------------------------------------
#---- general definition
#-----------------------------------------
#====== ALL LENGTHS IN MICRON ==========
#---- dimensions of the stamp   
X_SIZE, Y_SIZE = 15000, 15000
X_OFF = 2000.0 #region where no devices are to be fabricated
step = 100.0 #standard spacing between components

#------------------------------------
class Stamps():
    def __init__(self,wmin=1.5,Nmax=15,pas=0.3):
        """ creates Nmax waveguide templates with width (µm) from wmin to Nmax*pas """
        self.wgt=[]
        self.Nmax=Nmax
        for i in range(Nmax):
            self.wgt.append( \
                    pc.WaveguideTemplate(wg_width=1+0.3*i, clad_width=1.0, bend_radius=100,
                resist='-', fab='ETCH', wg_layer=1, wg_datatype=0, clad_layer=2,
                clad_datatype=0)
                    )


#------------ Makes a stamp from a given "motif" repeated many times  
    def MakesStampFromMotif(self,top,motif,X0=0,Y0=0,\
            Wst=X_SIZE,Hst=Y_SIZE,Xoff=X_OFF,step=100,titre="Stamp1"):
        """ add a stamp to the layer "top" filled with "motif" repeated as much
            as possible. (X0,Y0) bottom left position """

            #Add a die outline, with exclusion, from gdspy geometries found at
            #http://gdspy.readthedocs.io/en/latest/

        top.add(gdspy.Rectangle((X0,Y0), (X0+X_SIZE,Y0+ Y_SIZE), layer=6, datatype=0))
        top.add(gdspy.Rectangle((X0, Y0+Y_SIZE-Xoff), (X0+X_SIZE,Y0+ Y_SIZE), layer=7, datatype=0))
        top.add(gdspy.Rectangle((X0, Y0), (X0+X_SIZE,Y0+ Xoff), layer=7, datatype=0))
        top.add(gdspy.Rectangle((X0, Y0), (X0+Xoff,Y0+ Y_SIZE), layer=7, datatype=0))
        top.add(gdspy.Rectangle((X0+X_SIZE-Xoff, Y0), (X0+X_SIZE,Y0+ Y_SIZE), layer=7, datatype=0))

        """ fill the stamp with the motif """
        #1 size of the motif:
        Wmotif=motif.get_bounding_box()[1,0]-motif.get_bounding_box()[0,0]
        Hmotif=motif.get_bounding_box()[1,1]-motif.get_bounding_box()[0,1]
        #2 how many?
        Nmotifs=int((Wst-2*Xoff)/ (Wmotif+step) )
        dec= int(Wst-2*Xoff) % int(Wmotif+step)
        #3 plot :
        for i in range(Nmotifs):
            top.add(gdspy.CellReference(motif, (i*(Wmotif+step)+X0+Xoff+0.5*dec, Y0+Xoff)))
#-----------------------------------------------------------------------------------------------

#----------------------- lines with different width --------------
    def LinesCell(self,Nmin=0,Nsup=15,step=50,Yl=Y_SIZE-2*X_OFF):
        """ a straight wg series with different width """
        Lines=gdspy.Cell("Lines")

        for i in range(Nsup):
            wg = pc.Waveguide([(50*i,0),(50*i, Yl)], self.wgt[i])
            tk.add(Lines, wg)
        return Lines


#-----------  Une  spirale avec un grating coupler at the top ---------------------
    def Spirales(self):
        spiral_unit = gdspy.Cell("spiral_unit")
        #width (float): distance between input/output ports
        sp1 = pc.Spiral(self.wgt[5], width=4000.0, length=100000,spacing=7, parity=1, port=(100,5000))
        tk.add(spiral_unit, sp1)

        wg1=pc.Waveguide([sp1.portlist["input"]["port"],\
                (sp1.portlist["input"]["port"][0], 0.0)],self.wgt[5])
        wg2=pc.Waveguide([sp1.portlist["output"]["port"],\
                (sp1.portlist["output"]["port"][0], Y_SIZE-2*X_OFF-1000)],self.wgt[5])
        tk.add(spiral_unit, wg1)
        tk.add(spiral_unit, wg2)
        gc_top = pc.GratingCouplerFocusing(self.wgt[5], focus_distance=40,
                width=20, length=100,
                                      period=0.7, dutycycle=0.4, wavelength=0.6,
                                      sin_theta=np.sin(np.pi*8/180), **wg2.portlist["output"])
        tk.add(spiral_unit, gc_top)
        
        return spiral_unit


