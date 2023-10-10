import csv

# Datos a guardar
datos = [
    ['Parametro', 'Valor'],
    ['Nombre Del Archivo', 1],
    ['Masa total de la aeronave (kg)', 2],
    ['Carga alar (kgf/m^2)', 3],
    ['Desnidad del aire en despegue (kg/m^3)', 4],
    ['Distancia de carrera en despegue (m)', 5],
    ['Coeficiente de sustentacion maximo', 6],
    ['Coeficiente de fricción de pista', 7],
    ['Coeficiente de arrastre mínimo', 8],
    ['Relación de ascenso / velocidad vertical (m/s)', 9],
    ['Factor de alargamiento', 10],
    ['Densidad del aire en vuelo crucero (kg/m^3)', 10],
    ['Velocidad en vuelo crucero (m/s)', 10],
    ['Coeficiente del estabilizador horizontal', 10],
    ['Factor de distancia entre centros aerodinamicos', 10],
    ['Coeficiente del estabilizador vertical', 10],
    ['Factor de alargamiento estabilizador horizontal', 10],
    ['Factor de alargamiento estabilizador vertical', 10],
    ['Velocidad Stall (m/s)', 10],
    ['Velocidad de rotación (m/s)', 10],
    ['Velocidad 1 - V1 (m/s)', 10],
    ['Velocidad 2 - V2 (m/s)', 10],
    ['Presión dinámica en despegue (Pa)', 10],
    ['Coeficiente de sustentación en despegue', 10],
    ['Coeficiente de arrastre en despegue', 10],
    ['Relacion empuje peso-peso en despegue', 10],
    ['Presión dinámica en ascenso (Pa)', 10],
    ['Factor de eficencia de Oswald', 10],
    ['Factor de attastre inducido', 10],
    ['Relacion empuje peso-peso en ascenso', 10],
    ['Presión dinámica en crucero (Pa)', 10],
    ['Relacion empuje peso-peso en crucero', 10],
    ['Factor de alabeo (rad)', 10],
    ['Factoe de carga', 10],
    ['Relacion empuje peso-peso en giro', 10],
    ['Peso total (N)', 10],
    ['Superficie alar (m^2)', 10],
    ['Empuje minimo en fase critica', 10],
    ['Envergadura', 10],
    ['Cuerda', 10],
    ['Superficie estabilizador horizontal', 10],
    ['Envergadura estabilizador horizontal', 10],
    ['Cuerda estabilizador horizontal', 10],
    ['Superficie estabilizador vertical', 10],
    ['Envergadura estabilizador vertical', 10],
    ['Cuerda estabilizador vertical', 10],
]

# Nombre del archivo CSV
nombre_archivo = 'datos.csv'

# Guardar los datos en el archivo CSV
with open(nombre_archivo, 'w', newline='') as archivo_csv:
    escritor_csv = csv.writer(archivo_csv)
    escritor_csv.writerows(datos)

print('Los datos se han guardado exitosamente en el archivo CSV.')
