# Usa la imagen oficial de Python 3.10
FROM python:3.10.6
USER root
# Establece las variables de entorno para la configuración regional

# Evita la generación de archivos .pyc y .pyo
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1


# Establece el directorio de trabajo
WORKDIR /ITS-Asistencias/ITS-Asistencias

RUN apt-get update && apt-get install -y supervisor

RUN mkdir -p media/
RUN chmod -R 755 media/
# Copia la configuración de Nginx al contenedor

COPY supervisord.conf /supervisord.conf
# Copia el resto de los archivos del proyecto

# Copia solo los archivos necesarios para instalar las dependencias
COPY requirements.txt .
RUN python -m pip install -r requirements.txt
COPY . .


# Expone el puerto 8000
EXPOSE 8000

# Comando para ejecutar la aplicación
CMD ["supervisord", "-c", "/supervisord.conf"]
