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
X_SIZE, Y_SIZE = 16_000, 20_000
X_OFF = 500 #region where no devices are to be fabricated
step = 100 #standard spacing between components
Far_from_border=2000 # the distance between X_OFF and the waveguide
#------------------------------------
class Stamps():
    def __init__(self,W_min=1.8,W_min_ch=1.2,Nmax_ch=40,pas_ch=0.1,Nmax=24,pas=0.1,Taper_out=10,bend_radius=300,
        spiral_width=3_000,grating_width=20,spiral_length=110_000,spiral_spacing=10,grating_focusing_distance=40,grating_length=100):
        """ creates Nmax waveguide templates with width (µm) from W_min to Nmax*pas """
        self.wgt=[];self.wgt_ch=[];self.Nmax=Nmax;self.pas=pas
        self.Nmax_ch=Nmax_ch
        self.Taper_out=Taper_out;self.bend_radius=bend_radius
        self.spiral_width=spiral_width;self.spiral_length=spiral_length
        self.spiral_spacing=spiral_spacing
        self.grating_focusing_distance=grating_focusing_distance
        self.grating_length=grating_length;self.grating_width=grating_width
        self.Taper_wg_Template=pc.WaveguideTemplate(wg_width=self.Taper_out, clad_width=1.0, bend_radius=self.bend_radius,
                                               resist='-', fab='ETCH', wg_layer=1, wg_datatype=0, clad_layer=2,
                                               clad_datatype=0)#Waveguide template for the Taper extention
        ch_width=[];spral_width=[]
        for i in range(self.Nmax):
            # pas=self.pas if W_min+pas*i >=3 or W_min+pas*i <= 1.8 else 0.1
            spral_width.append(np.around(W_min+pas*i,decimals=1))
            self.wgt.append( \
                    pc.WaveguideTemplate(wg_width=np.around(W_min+pas*i,decimals=1), clad_width=1.0,
                    bend_radius=self.bend_radius,resist='-', fab='ETCH', wg_layer=1, wg_datatype=0, clad_layer=2,
                    clad_datatype=0))
        for i in range(self.Nmax_ch):
            ch_width.append(np.around(W_min_ch+pas_ch*i,decimals=1))
            self.wgt_ch.append( \
                pc.WaveguideTemplate(wg_width=np.around(W_min_ch+pas_ch*i,decimals=1), clad_width=1.0,
                bend_radius=self.bend_radius,resist='-', fab='ETCH', wg_layer=1, wg_datatype=0, clad_layer=2,
                clad_datatype=0))
        print(ch_width)
        print(spral_width)
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
            # print((i*(Wmotif+step)+X0+Xoff+0.5*dec, Y0+Xoff))
            top.add(gdspy.CellReference(motif, (i*(Wmotif+step)+X0+Xoff+0.5*dec, Y0+Xoff)))
#-----------------------------------------------------------------------------------------------

#----------------------- lines with different width --------------
    def LinesCell(self,pas=50,Yl=Y_SIZE-2*X_OFF-Far_from_border, name='Lines_Grating'):
        """ a straight wg series with different width """
        Lines=gdspy.Cell(name)
        for i in range(self.Nmax_ch):
            wg = pc.Waveguide([(pas*i,Far_from_border),(pas*i, Yl)], self.wgt_ch[i])
            tk.add(Lines, wg)
            if name=='Lines_Grating':
                gc_top = pc.GratingCouplerFocusing(self.wgt_ch[i], focus_distance=self.grating_focusing_distance, width=self.grating_width,
                    length=self.grating_length, period=0.7, dutycycle=0.4, wavelength=0.6, sin_theta=np.sin(np.pi*8/180), **wg.portlist["input"])
                tk.add(Lines, gc_top)
                gc_down = pc.GratingCouplerFocusing(self.wgt_ch[i], focus_distance=self.grating_focusing_distance, width=self.grating_width,
                    length=self.grating_length,period=0.7, dutycycle=0.4, wavelength=0.6, sin_theta=np.sin(np.pi*8/180), **wg.portlist["output"])
                tk.add(Lines, gc_down)
            elif name=='Lines_Taper':
                tp_bot = pc.Taper(self.wgt_ch[i], length=50.0, end_width=self.Taper_out,end_clad_width=0,extra_clad_length=0, **wg.portlist["input"])
                tk.add(Lines, tp_bot)
                tp_up = pc.Taper(self.wgt_ch[i], length=50.0, end_width=self.Taper_out,end_clad_width=0,extra_clad_length=0, **wg.portlist["output"])
                tk.add(Lines, tp_up)
                wg_taper_bot=pc.Waveguide([tp_bot.portlist["output"]["port"], \
                                           (tp_bot.portlist["output"]["port"][0], Far_from_border-2000)],self.Taper_wg_Template)
                tk.add(Lines, wg_taper_bot)
                wg_taper_up=pc.Waveguide([tp_up.portlist["output"]["port"], \
                                      (tp_up.portlist["output"]["port"][0], Y_SIZE-2*X_OFF-Far_from_border+2000)],self.Taper_wg_Template)
                tk.add(Lines, wg_taper_up)
        return Lines

#-----------  Une  spirale avec un grating coupler at the top ---------------------
    def Spirales(self,name='Spiral_Grating'):
        spiral_unit = gdspy.Cell(name)
        two_spiral_space=1200
        deltaY=0.5*self.spiral_width
        for i in range(self.Nmax):
            if (i%2 ==0 ) :
                sp1 = pc.Spiral(self.wgt[i], width=self.spiral_width, length=self.spiral_length,spacing=self.spiral_spacing
                                ,
                                parity=1,direction=u'NORTH',port=(100+(two_spiral_space*i/2),Y_SIZE/2-1.8*self.spiral_width+deltaY))#port is cartisian cordinate of the inputport
                tk.add(spiral_unit, sp1)
                wg1=pc.Waveguide([sp1.portlist["input"]["port"],\
                    (sp1.portlist["input"]["port"][0], Far_from_border)],self.wgt[i])
                tk.add(spiral_unit, wg1)
                sp2 = pc.Spiral(self.wgt[i], width=self.spiral_width, length=self.spiral_length,spacing=self.spiral_spacing
                                ,
                                parity=1,direction=u'NORTH',port=(100+(two_spiral_space*i/2),Y_SIZE/1.8+deltaY))
            else :
                #-------------------------------------------------------------------------------------------------------------------
                sp1 = pc.Spiral(self.wgt[i], width=self.spiral_width, length=self.spiral_length,spacing=self.spiral_spacing
                                ,
                                parity=-1,direction=u'NORTH',port=(100+(two_spiral_space*(i-1)/2+0.9*two_spiral_space),Y_SIZE/2-1.8*self.spiral_width-deltaY))#port is cartisian cordinate of the inputport
                tk.add(spiral_unit, sp1)
                wg1=pc.Waveguide([sp1.portlist["input"]["port"],\
                    (sp1.portlist["input"]["port"][0], Far_from_border)],self.wgt[i])
                tk.add(spiral_unit, wg1)
                sp2 = pc.Spiral(self.wgt[i], width=self.spiral_width, length=self.spiral_length,spacing=self.spiral_spacing
                                ,
                                parity=-1,direction=u'NORTH',port=(100+(two_spiral_space*(i-1)/2+0.9*two_spiral_space),Y_SIZE/1.8-deltaY))

            tk.add(spiral_unit, sp2)
            wg2=pc.Waveguide([sp1.portlist["output"]["port"], \
                              (sp1.portlist["output"]["port"][0], sp2.portlist["input"]["port"][1])],self.wgt[i])
            tk.add(spiral_unit, wg2)
            wg3=pc.Waveguide([sp2.portlist["output"]["port"], \
                              (sp2.portlist["output"]["port"][0], Y_SIZE-2*X_OFF-Far_from_border)],self.wgt[i])
            tk.add(spiral_unit, wg3)
            if name=='Spiral_Grating':
                gc_top = pc.GratingCouplerFocusing(self.wgt[i], focus_distance=self.grating_focusing_distance,width=self.grating_width,
                    length=self.grating_length,period=0.7, dutycycle=0.4, wavelength=0.6, sin_theta=np.sin(np.pi*8/180), **wg3.portlist["output"])
                tk.add(spiral_unit, gc_top)
                gc_down = pc.GratingCouplerFocusing(self.wgt[i], focus_distance=self.grating_focusing_distance, width=self.grating_width,
                    length=self.grating_length, period=0.7, dutycycle=0.4, wavelength=0.6, sin_theta=np.sin(np.pi*8/180), **wg1.portlist["output"])
                tk.add(spiral_unit, gc_down)
            elif name=='Spiral_Taper':
                tp_bot = pc.Taper(self.wgt[i], length=50.0, end_width=self.Taper_out,end_clad_width=0,extra_clad_length=0, **wg1.portlist["output"])
                tk.add(spiral_unit, tp_bot)
                tp_up = pc.Taper(self.wgt[i], length=50.0, end_width=self.Taper_out,end_clad_width=0,extra_clad_length=0, **wg3.portlist["output"])
                tk.add(spiral_unit, tp_up)
                wg_taper_bot=pc.Waveguide([tp_bot.portlist["output"]["port"], \
                                       (tp_bot.portlist["output"]["port"][0], Far_from_border-2000)],self.Taper_wg_Template)
                tk.add(spiral_unit, wg_taper_bot)
                wg_taper_up=pc.Waveguide([tp_up.portlist["output"]["port"], \
                                           (tp_up.portlist["output"]["port"][0], Y_SIZE-2*X_OFF-Far_from_border+2000)],self.Taper_wg_Template)
                tk.add(spiral_unit, wg_taper_up)
        return spiral_unit


