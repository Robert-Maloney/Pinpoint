import ctypes
import os

gdal_path = os.environ.get('GDAL_LIBRARY_PATH', r'C:\OSGeo4W\bin\gdal309.dll')

try:
    gdal = ctypes.CDLL(gdal_path)
    print("GDAL loaded successfully")
except OSError as e:
    print("Failed to load GDAL:", e)