from PyQt5.QtWidgets import *
from AppMainDesign import Ui_TabWidget
import sys, numpy as np
import csv
import tkinter as tk
from tkinter import filedialog

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt


class MainApp(QTabWidget):
    def __init__(self):
        super(MainApp, self).__init__()
        self.ui = Ui_TabWidget()
        self.ui.setupUi(self)

        # Tab Parametros iniciales
        self.ui.btn_calcular.clicked.connect(lambda: self.CalculoDatosAerodinamicos())
        self.ui.btn_guardarDatos.clicked.connect(lambda: self.GuardaDatos())
        self.ui.btn_cargarDatos.clicked.connect(lambda: self.CargarDatos())
        self.ui.btn_curvaPolarArrastre.clicked.connect(lambda: self.MostrarCurvaPolarArrastre())

    def CalculoDatosAerodinamicos(self):
        # Obtener datos
        self.masaMaxima = float(self.ui.edt_masaTotal.text())  # kg
        self.gravedad = 9.81  # m/s^2
        self.cargaAlar = float(self.ui.edt_cargaAlar.text())  # kgf/m^2
        self.densidadDelAire = float(self.ui.edt_densidadAireDespegue.text())  # kg/m^3

        # Despegue
        self.distanciaEnCarrera = float(self.ui.edt_distanciaCarrera_2.text())  # m
        self.coefSusMaximo = float(self.ui.edt_coefSusMax.text())
        self.coefFriccionDespegue = float(self.ui.edt_coefFric.text())

        # Ascenso
        self.velocidadVerticalEnAscenso = float(self.ui.edt_velocidadAscenso.text())  # m/s
        self.coefArrasMin = float(self.ui.edt_coefArrasMin.text())
        self.alargamiento = float(self.ui.edt_alargamiento.text())

        # Crucero
        self.densidadDelAireCrucero = float(self.ui.edt_densidadAireCrucero.text())  # kg/m^3
        self.velocidadCrucero = float(self.ui.edt_velocidadCrucero.text())  # m/s

        # Giro
        self.anguloAlabeo = float(self.ui.edt_anguloAlabeo.text())

        # Estabilizadores y ala
        self.coefEstabHorizontal = float(self.ui.edt_coefEstabHorizontal.text())
        self.factorDistanciaCentrosAerodinamicos = float(self.ui.edt_factorDistanciaCentrosAerodin.text())
        self.coefEstabVertical = float(self.ui.edt_coefEstabVertical.text())
        self.alargamientoEstabHorizontal = float(self.ui.edt_alargamientoEstabHorizontal.text())
        self.alargamientoEstabVertical = float(self.ui.edt_alargamientoEstabVertical.text())

        # ********************************************************
        # Calculo relacion empuje-peso distintas fases
        # Despegue
        self.cargaAlarNewton = self.cargaAlar * self.gravedad  # N/m^2
        self.velocidadStall = np.sqrt(2 * self.cargaAlarNewton / (self.densidadDelAire * self.coefSusMaximo))  # m/s
        self.velocidadRotacion = 1.1 * self.velocidadStall  # m/s
        self.presionDinamicaDespegue = 0.5 * self.densidadDelAire * (self.velocidadRotacion ** 2)  # Pa
        self.coefSusDespegue = 2 * self.cargaAlarNewton / (self.densidadDelAire * (self.velocidadRotacion ** 2))
        self.coefArrasDepegue = 0.15 * self.coefSusDespegue
        self.relacionEmpujePesoDespegue = ((self.velocidadRotacion ** 2) / (
                2 * self.gravedad * self.distanciaEnCarrera)) + (
                                                  (self.presionDinamicaDespegue * self.coefArrasDepegue) / (
                                              self.cargaAlarNewton)) + (self.coefFriccionDespegue * (
                1 - ((self.presionDinamicaDespegue * self.coefSusDespegue) / (self.cargaAlarNewton))))

        # Ascenso
        self.velocidadAscensoV2 = 1.2 * self.velocidadStall  # m/s
        self.presionDinamicaAscenso = 0.5 * self.densidadDelAire * (self.velocidadAscensoV2 ** 2)  # m/s
        self.factorEficenciaOswald = 1.78 * (1 - (0.045 * (self.alargamiento ** 0.68))) - 0.64
        self.factorArrastreInducido = 1 / (np.pi * self.alargamiento * self.factorEficenciaOswald)
        self.relacionEmpujePesoAscenso = (self.velocidadVerticalEnAscenso / self.velocidadAscensoV2) + (
                (self.presionDinamicaAscenso * self.coefArrasMin) / (self.cargaAlarNewton)) + (
                                                 self.factorArrastreInducido * self.cargaAlarNewton / self.presionDinamicaAscenso)

        # Crucero
        self.presionDinamicaCrucero = 0.5 * self.densidadDelAireCrucero * (self.velocidadCrucero ** 2)  # m/s
        self.relacionEmpujePesoCrucero = ((self.presionDinamicaCrucero * self.coefArrasMin) * (
                1 / self.cargaAlarNewton)) + (
                                                 self.factorArrastreInducido * self.cargaAlarNewton / self.presionDinamicaCrucero)

        # Giro
        self.anguloAlabeoRadianes = self.anguloAlabeo * 2 * np.pi / 362
        self.factorCarga = 1 / np.cos(self.anguloAlabeoRadianes)
        self.relacionEmpujePesoGiro = self.presionDinamicaCrucero * ((self.coefArrasMin / self.cargaAlarNewton) + (
                self.factorArrastreInducido * (
                (self.factorCarga / self.presionDinamicaCrucero) ** 2) * self.cargaAlarNewton))

        # ********************************************************
        # Conocer mayor
        self.empujePeso = (
            self.relacionEmpujePesoDespegue, self.relacionEmpujePesoAscenso, self.relacionEmpujePesoCrucero,
            self.relacionEmpujePesoGiro)

        if self.empujePeso.index(max(self.empujePeso)) == 0:
            faseCritica = "Despegue"
        elif self.empujePeso.index(max(self.empujePeso)) == 1:
            faseCritica = "Ascenso"
        elif self.empujePeso.index(max(self.empujePeso)) == 2:
            faseCritica = "Crucero"
        else:
            faseCritica = "Giro"

        # ********************************************************
        # Dimensionamiento inicial
        # General
        self.pesoTotal = self.masaMaxima * self.gravedad
        self.superficieAlar = self.pesoTotal / self.cargaAlarNewton
        self.empujeMinimo = self.empujePeso[self.empujePeso.index(max(self.empujePeso))] * self.pesoTotal

        # Ala rectangular
        self.envergadura = np.sqrt(self.alargamiento * self.superficieAlar)
        self.cuerda = self.superficieAlar / self.envergadura
        self.cuerdaMediaAerodinamica = self.cuerda

        # Establizador horizontal rectangular
        self.superficieEstabHorizontal = self.coefEstabHorizontal * self.cuerdaMediaAerodinamica * self.superficieAlar / (
                self.factorDistanciaCentrosAerodinamicos * self.cuerdaMediaAerodinamica)
        self.envergaduraEstabHorizontal = np.sqrt(self.alargamientoEstabHorizontal * self.superficieEstabHorizontal)
        self.cuerdaEstabilizadorHorizontal = self.superficieEstabHorizontal / self.envergaduraEstabHorizontal

        # Establizador vertical rectangular
        self.superficieEstabVertical = self.coefEstabVertical * self.envergadura * self.superficieAlar / (
                self.factorDistanciaCentrosAerodinamicos * self.cuerdaMediaAerodinamica)
        self.envergaduraEstabVertical = np.sqrt(self.alargamientoEstabVertical * self.superficieEstabVertical)

        # superficieEstabVertical = superficieEstabVertical/numeroEstabVerciales
        self.cuerdaEstabilizadorVertical = self.superficieEstabVertical / self.envergaduraEstabVertical
        # ********************************************************

        self.ui.lbl_velStallRes.setText(str(self.velocidadStall))
        self.ui.lbl_velRotRes.setText(str(self.velocidadRotacion))
        self.ui.lbl_velV1Res.setText(str(self.velocidadRotacion))
        self.ui.lbl_velV2_2.setText(str(self.velocidadAscensoV2))
        self.ui.lbl_presDinDespeRes.setText(str(self.presionDinamicaDespegue))
        self.ui.lbl_CoefSusDespRes.setText(str(self.coefSusDespegue))
        self.ui.lbl_CoefArrasDespRes.setText(str(self.coefArrasDepegue))
        self.ui.lbl_empujePesoDespRes.setText(str(self.relacionEmpujePesoDespegue))

        self.ui.lbl_presDinAscRes.setText(str(self.presionDinamicaAscenso))
        self.ui.lbl_factOswaldRes.setText(str(self.factorEficenciaOswald))
        self.ui.lbl_factArrasInducRes.setText(str(self.factorArrastreInducido))
        self.ui.lbl_empujePesoAscenRes.setText(str(self.relacionEmpujePesoAscenso))

        self.ui.lbl_presDinCrucRes.setText(str(self.presionDinamicaCrucero))
        self.ui.lbl_empujePesoCrucRes.setText(str(self.relacionEmpujePesoCrucero))
        self.ui.lbl_factAlabeoRes.setText(str(self.anguloAlabeoRadianes))
        self.ui.lbl_factCargaRes.setText(str(self.factorCarga))
        self.ui.lbl_empujePesoGiroRes.setText(str(self.relacionEmpujePesoGiro))

        self.ui.lbl_pesoTotRes.setText(str(self.pesoTotal))
        self.ui.lbl_superAlarRes.setText(str(self.superficieAlar))
        self.ui.lbl_empujeMinRes.setText(str(self.empujeMinimo))

        self.ui.lbl_envergaduraRes.setText(str(self.envergadura))
        self.ui.lbl_cuerdaRes.setText(str(self.cuerda))

        self.ui.lbl_superEstabHoriRes.setText(str(self.superficieEstabHorizontal))
        self.ui.lbl_envergadEstabHorizRes.setText(str(self.envergaduraEstabHorizontal))
        self.ui.lbl_cuerdaEstabHorizRes.setText(str(self.cuerdaEstabilizadorHorizontal))

        self.ui.lbl_superEstabVertiRes.setText(str(self.superficieEstabVertical))
        self.ui.lbl_envergadEstabVertiRes.setText(str(self.envergaduraEstabVertical))
        self.ui.lbl_cuerdaEstabVertiRes.setText(str(self.cuerdaEstabilizadorVertical))

        self.ui.btn_guardarDatos.setEnabled(True)
        self.ui.btn_curvaPolarArrastre.setEnabled(True)

    def GuardaDatos(self):
        # Datos a guardar
        datos = [
            ['Parametro', 'Valor'],
            ['Nombre Del Archivo', self.ui.edt_nombre.text()],
            ['Masa total de la aeronave (kg)', str(self.masaMaxima)],
            ['Carga alar (kgf/m^2)', str(self.cargaAlar)],
            ['Densidad del aire en despegue (kg/m^3)', str(self.densidadDelAire)],
            ['Distancia de carrera en despegue (m)', str(self.distanciaEnCarrera)],
            ['Coeficiente de sustentacion maximo', str(self.coefSusMaximo)],
            ['Coeficiente de fricción de pista', str(self.coefFriccionDespegue)],
            ['Coeficiente de arrastre mínimo', str(self.coefArrasMin)],
            ['Relación de ascenso / velocidad vertical (m/s)', str(self.velocidadVerticalEnAscenso)],
            ['Factor de alargamiento', str(self.alargamiento)],
            ['Densidad del aire en vuelo crucero (kg/m^3)', str(self.densidadDelAireCrucero)],
            ['Velocidad en vuelo crucero (m/s)', str(self.velocidadCrucero)],
            ['Angulo de alabeo en giro (°)', str(self.anguloAlabeo)],
            ['Coeficiente del estabilizador horizontal', str(self.coefEstabHorizontal)],
            ['Factor de distancia entre centros aerodinamicos', str(self.factorDistanciaCentrosAerodinamicos)],
            ['Coeficiente del estabilizador vertical', str(self.coefEstabVertical)],
            ['Factor de alargamiento estabilizador horizontal', str(self.alargamientoEstabHorizontal)],
            ['Factor de alargamiento estabilizador vertical', str(self.alargamientoEstabVertical)],
            ['Velocidad Stall (m/s)', str(self.velocidadStall)],
            ['Velocidad de rotación (m/s)', str(self.velocidadRotacion)],
            ['Velocidad 1 - V1 (m/s)', str(self.velocidadRotacion)],
            ['Velocidad 2 - V2 (m/s)', str(self.velocidadAscensoV2)],
            ['Presión dinámica en despegue (Pa)', str(self.presionDinamicaDespegue)],
            ['Coeficiente de sustentación en despegue', str(self.coefSusDespegue)],
            ['Coeficiente de arrastre en despegue', str(self.coefArrasDepegue)],
            ['Relacion empuje peso-peso en despegue', str(self.relacionEmpujePesoDespegue)],
            ['Presión dinámica en ascenso (Pa)', str(self.presionDinamicaAscenso)],
            ['Factor de eficencia de Oswald', str(self.factorEficenciaOswald)],
            ['Factor de attastre inducido', str(self.factorArrastreInducido)],
            ['Relacion empuje peso-peso en ascenso', str(self.relacionEmpujePesoAscenso)],
            ['Presión dinámica en crucero (Pa)', str(self.presionDinamicaCrucero)],
            ['Relacion empuje peso-peso en crucero', str(self.relacionEmpujePesoCrucero)],
            ['Factor de alabeo (rad)', str(self.anguloAlabeoRadianes)],
            ['Factoe de carga', str(self.factorCarga)],
            ['Relacion empuje peso-peso en giro', str(self.relacionEmpujePesoGiro)],
            ['Peso total (N)', str(self.pesoTotal)],
            ['Superficie alar (m^2)', str(self.superficieAlar)],
            ['Empuje minimo en fase critica', str(self.empujeMinimo)],
            ['Envergadura', str(self.envergadura)],
            ['Cuerda', str(self.cuerda)],
            ['Superficie estabilizador horizontal', str(self.superficieEstabHorizontal)],
            ['Envergadura estabilizador horizontal', str(self.envergaduraEstabHorizontal)],
            ['Cuerda estabilizador horizontal', str(self.cuerdaEstabilizadorHorizontal)],
            ['Superficie estabilizador vertical', str(self.superficieEstabVertical)],
            ['Envergadura estabilizador vertical', str(self.envergaduraEstabVertical)],
            ['Cuerda estabilizador vertical', str(self.cuerdaEstabilizadorVertical)]
        ]

        try:
            root = tk.Tk()
            root.withdraw()
            ruta_archivo = filedialog.asksaveasfilename(defaultextension='.csv', filetypes=[('Archivos CSV', '*.csv')])

            with open(ruta_archivo, 'w', newline='') as archivo_csv:
                escritor_csv = csv.writer(archivo_csv)
                escritor_csv.writerows(datos)
        except:
            pass

    def CargarDatos(self):
        root = tk.Tk()
        root.withdraw()
        ruta_archivo = filedialog.askopenfilename(filetypes=[('Archivos CSV', '*.csv')])

        try:
            with open(ruta_archivo, 'r') as archivo_csv:
                lector_csv = csv.reader(archivo_csv)
                datos = []
                for fila in lector_csv:
                    datos.append(fila)
            self.ui.edt_nombre.setText(datos[1][1])

            self.ui.edt_masaTotal.setText(datos[2][1])
            self.ui.edt_cargaAlar.setText(datos[3][1])
            self.ui.edt_densidadAireDespegue.setText(datos[4][1])
            self.ui.edt_distanciaCarrera_2.setText(datos[5][1])
            self.ui.edt_coefSusMax.setText(datos[6][1])
            self.ui.edt_coefFric.setText(datos[7][1])
            self.ui.edt_coefArrasMin.setText(datos[8][1])
            self.ui.edt_velocidadAscenso.setText(datos[9][1])
            self.ui.edt_alargamiento.setText(datos[10][1])
            self.ui.edt_densidadAireCrucero.setText(datos[11][1])
            self.ui.edt_velocidadCrucero.setText(datos[12][1])
            self.ui.edt_anguloAlabeo.setText(datos[13][1])
            self.ui.edt_coefEstabHorizontal.setText(datos[14][1])
            self.ui.edt_factorDistanciaCentrosAerodin.setText(datos[15][1])
            self.ui.edt_coefEstabVertical.setText(datos[16][1])
            self.ui.edt_alargamientoEstabHorizontal.setText(datos[17][1])
            self.ui.edt_alargamientoEstabVertical.setText(datos[18][1])

            self.CalculoDatosAerodinamicos()
        except:
            pass

    def MostrarCurvaPolarArrastre(self):

        # Parámetros de la curva polar de arrastre
        self.coefSusMinArras = self.coefArrasMin / 0.15  # El factor puede variar entre 0.10 y 0.15

        # Cálculo de la curva polar de arrastre
        rango = []

        self.inicioRangoCurvaPolarArrastre = -1
        self.finRangoCurvaPolarArrastre = 1
        self.pasoRangoCurvaPolarArrastre = 0.2

        valor = self.inicioRangoCurvaPolarArrastre
        while valor <= self.finRangoCurvaPolarArrastre:
            rango.append(valor)
            valor += self.pasoRangoCurvaPolarArrastre
        self.coefArrastre = []
        for coefSus in rango:
            self.coefArrastre.append(self.coefArrasMin + self.factorArrastreInducido * ((coefSus - self.coefSusMinArras) ** 2))

        # Crear DataFrame con los datos
        df = pd.DataFrame({"CL": rango, "CD": self.coefArrastre})

        # Graficar la curva polar de arrastre con scatterplot
        sns.scatterplot(data=df, x="CD", y="CL")

        # Unir los puntos con una línea utilizando plot
        plt.plot(df["CD"], df["CL"], color='blue', linewidth=1)

        # Configurar aspecto del gráfico
        plt.xlabel('CD')
        plt.ylabel('CL')

        # Mostrar el gráfico
        plt.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    App = MainApp()
    App.show()
    sys.exit(app.exec())

# pyuic5 -x AppMainDesign.ui -o AppMainDesign.py
