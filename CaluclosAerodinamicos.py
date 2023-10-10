# Importar modulos
import math
import numpy as np
from ipywidgets import interact
from ipywidgets import *
import matplotlib.pyplot as plt


def NACA4(P,TT,M):
    Npoints = 50
    a0 = 0.2969
    a1 = -0.126
    a2 = -0.3516
    a3 = 0.2843
    a4 = -0.1036 # En caso de querer mantener el borde de fuga abierto, usar > que -0.1015

    YU = []
    YB = []
    X  = []
    YC = []

    b = np.linspace(0,math.pi,Npoints)
    x = (1-np.cos(b))/2
    TT = TT/100
    M  = M/100
    P  = P/10
    for xc in x:

        if xc<P:
            yc = (M/math.pow(P,2))*(2*P*xc-math.pow(xc,2))
            dyc =(2*M/math.pow(P,2))*(P-xc)
        else:
            yc = (M/(math.pow(1-P,2)))*(1-2*P+2*P*xc-math.pow(xc,2))
            dyc =(2*M/(math.pow(1-P,2)))*(P-xc)

        theta = np.arctan(dyc)

        yt = (TT/0.2)*(a0*math.sqrt(xc) + a1*xc + a2*math.pow(xc,2) + a3*math.pow(xc,3) + a4*math.pow(xc,4))

        X.append(xc-yt*np.sin(theta))
        YU.append(yc+yt*np.cos(theta))
        YB.append(yc-yt*np.cos(theta))
        YC.append(yc)

    X  = np.array(X)
    YU = np.array(YU)
    YC = np.array(YC)
    YB = np.array(YB)

    fig = plt.figure(figsize=(10, 6), dpi=80, facecolor='w', edgecolor='k')
    ax = fig.add_subplot(2, 1, 1)
    ax.plot(X, YC,color="black")
    ax.plot(X, YU,color="blue")
    ax.plot(X,YB,color="red")
    ax.grid(True)
    ax.title.set_text('Perfil NACA %d%d%0.2d'%(int(M*100),int(P*10),int(TT*100)))
    ax.set_xlabel('Cuerda relativa')
    ax.set_ylabel('Espesura relativa')
    ax.set_aspect('equal', 'datalim')
    ax.legend(['Curvatura media','Extradorso','Intradorso'], loc=0)
    fig.canvas.draw()

interact(NACA4, P=widgets.IntSlider(min=0,max=9,step=1,value=0),TT=widgets.IntSlider(min=1,max=30,step=1,value=10),M=widgets.IntSlider(min=0,max=9,step=1,value=0));