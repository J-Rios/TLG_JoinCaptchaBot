#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
Script:
    tsjson.py
Description:
    Thread-Safe json files read/write library.
Author:
    Jose Rios Rubio
Creation date:
    20/07/2017
Last modified date:
    25/08/2017
Version:
    1.2.0
'''

####################################################################################################

### Modulos importados ###
import os
import json
from threading import Lock
from collections import OrderedDict

####################################################################################################

### Clase ###
class TSjson(object):
    '''
    Thread-Safe json files read/write library
    '''

    def __init__(self, file_name):
        '''Constructor de la clase'''
        self.lock = Lock() #Inicializa el Lock
        self.file_name = file_name # Adquiere el nombre del archivo a controlar


    def read(self):
        '''Funcion para leer de un archivo json'''
        try: # Intentar abrir el archivo
            self.lock.acquire() # Cerramos (adquirimos) el mutex
            if not os.path.exists(self.file_name): # Si el archivo no existe
                read = {} # Devolver un diccionario vacio
            else: # Si el archivo existe
                if not os.stat(self.file_name).st_size: # Si el archivo esta vacio
                    read = {} # Devolver un diccionario vacio
                else: # El archivo existe y tiene contenido
                    with open(self.file_name, "r", encoding="utf-8") as f: # Abrir el archivo en modo lectura
                        read = json.load(f, object_pairs_hook=OrderedDict) # Leer todo el archivo y devolver la lectura de los datos json usando un diccionario ordenado
        except Exception as e: # Error intentando abrir el archivo
            print("    Error reading json file {}. {}".format(self.file_name, str(e))) # Escribir en consola el error
            read = None # Devolver None
        finally: # Para acabar, haya habido excepcion o no
            self.lock.release() # Abrimos (liberamos) el mutex

        return read # Devolver el resultado de la lectura de la funcion


    def write(self, data):
        '''Funcion para escribir en un archivo json'''
        # Si no existe el directorio que contiene los archivos de datos, lo creamos
        directory = os.path.dirname(self.file_name) # Obtener el nombre del directorio que contiene al archivo
        if not os.path.exists(directory): # Si el directorio (ruta) no existe
            os.makedirs(directory) # Creamos el directorio

        try: # Intentar abrir el archivo
            self.lock.acquire() # Cerramos (adquirimos) el mutex
            with open(self.file_name, 'w', encoding="utf-8") as f: # Abrir el archivo en modo escritura (sobre-escribe)
                json.dump(data, fp=f, ensure_ascii=False, indent=4) # Escribimos en el archivo los datos json asegurando todos los caracteres ascii, codificacion utf-8 y una "indentacion" de 4 espacios
        except: # Error intentando abrir el archivo
            print("    Error cuando se abria para escritura, el archivo {}".format(self.file_name)) # Escribir en consola el error
        finally: # Para acabar, haya habido excepcion o no
            self.lock.release() # Abrimos (liberamos) el mutex


    def read_content(self):
        '''Funcion para leer el contenido de un archivo json (datos json)'''
        read = self.read() # Leer todo el archivo json

        if read != {}: # Si la lectura no es vacia
            return read['Content'] # Devolvemos el contenido de la lectura (datos json)
        else: # Lectura vacia
            return read # Devolvemos la lectura vacia


    def write_content(self, data):
        '''Funcion para añadir al contenido de un archivo json, nuevos datos json'''
        # Si no existe el directorio que contiene los archivos de datos, lo creamos
        directory = os.path.dirname(self.file_name) # Obtener el nombre del directorio que contiene al archivo
        if not os.path.exists(directory): # Si el directorio (ruta) no existe
            os.makedirs(directory) # Creamos el directorio

        try: # Intentar abrir el archivo
            self.lock.acquire() # Cerramos (adquirimos) el mutex

            if data: # Si el dato no esta vacio
                if os.path.exists(self.file_name) and os.stat(self.file_name).st_size: # Si el archivo existe y no esta vacio
                    with open(self.file_name, "r", encoding="utf-8") as f: # Abrir el archivo en modo lectura
                        content = json.load(f, object_pairs_hook=OrderedDict) # Leer todo el archivo y devolver la lectura de los datos json usando un diccionario ordenado

                    content['Content'].append(data) # Añadir los nuevos datos al contenido del json

                    with open(self.file_name, 'w', encoding="utf-8") as f: # Abrir el archivo en modo escritura (sobre-escribe)
                        json.dump(content, fp=f, ensure_ascii=False, indent=4)
                else: # El archivo no existe o esta vacio
                    with open(self.file_name, 'w', encoding="utf-8") as f: # Abrir el archivo en modo escritura (sobre-escribe)
                        f.write('\n{\n    "Content": []\n}\n') # Escribir la estructura de contenido basica

                    with open(self.file_name, "r", encoding="utf-8") as f: # Abrir el archivo en modo lectura
                        content = json.load(f) # Leer todo el archivo

                    content['Content'].append(data) # Añadir los datos al contenido del json

                    with open(self.file_name, 'w', encoding="utf-8") as f:  # Abrir el archivo en modo escritura (sobre-escribe)
                        json.dump(content, fp=f, ensure_ascii=False, indent=4)
        except IOError as e:
            print("    I/O error({0}): {1}".format(e.errno, e.strerror))
        except ValueError:
            print("    Error en conversion de dato")
        except: # Error intentando abrir el archivo
            print("    Error cuando se abria para escritura, el archivo {}".format(self.file_name)) # Escribir en consola el error
        finally: # Para acabar, haya habido excepcion o no
            self.lock.release() # Abrimos (liberamos) el mutex


    def is_in(self, data):
        '''Funcion para determinar si el archivo json contiene un dato json concreto'''
        found = False # Dato inicialmente no encontrado
        file_data = self.read() # Leer todo el archivo json
        for _data in file_data['Content']: # Para cada dato en el archivo json
            if data == _data: # Si el contenido del json tiene dicho dato
                found = True # Marcar que se ha encontrado la posicion
                break # Interrumpir y salir del bucle
        return found


    def is_in_position(self, data):
        '''Funcion para determinar si el archivo json contiene un dato json concreto y la posicion de este'''
        found = False # Dato inicialmente no encontrado
        i = 0 # Posicion inicial del dato a 0
        file_data = self.read() # Leer todo el archivo json
        for _data in file_data['Content']: # Para cada dato en el archivo json
            if data == _data: # Si el contenido del json tiene dicho dato
                found = True # Marcar que se ha encontrado la posicion
                break # Interrumpir y salir del bucle
            i = i + 1 # Incrementar la posicion del dato
        return found, i # Devolvemos la tupla (encontrado, posicion)


    def remove_by_uide(self, element_value, uide):
        '''
        Funcion para eliminar un dato json concreto dentro del archivo json a partir de un elemento identificador unico (uide)
        [Nota: Cada dato json necesita al menos 1 elemento identificador unico (uide), si no es asi, la eliminacion se producira en el primer dato con dicho elemento uide que se encuentre]
        '''
        file_content = self.read_content() # Leer el contenido del archivo json
        for data in file_content: # Para cada dato json contenido
            if data[uide] == element_value: # Si el dato coincide con el buscado
                file_content.remove(data) # Eliminamos el dato
                break # Interrumpir y salir del bucle
        self.clear_content() # Eliminamos el contenido del archivo
        if file_content: # Si hay algun dato en el contenido modificado
            self.write_content(file_content[0]) # Write the modified content (without the item)


    def search_by_uide(self, element_value, uide):
        '''
        Funcion para buscar un dato json concreto dentro del archivo json a partir de un elemento identificador unico (uide)
        [Nota: Cada dato json necesita al menos 1 elemento identificador unico (uide), si no es asi, la actualizacion se producira en el primer dato con dicho elemento uide que se encuentre]
        '''
        result = dict() # Diccionario para el resultado de la busqueda
        result['found'] = False # Dato inicialmente no encontrado
        result['data'] = None # Dato encontrado inicialmente con ningun valor
        file_data = self.read() # Leer todo el archivo json
        for element in file_data['Content']: # Para cada elemento en el archivo json
            if element: # Si el contenido no esta vacio
                if element_value == element[uide]: # Si el dato json tiene el UIDE buscado
                    result['found'] = True # Marcar que se ha encontrado la posicion
                    result['data'] = element # Obtenemos el dato encontrado
                    break # Interrumpir y salir del bucle
        return result # Devolver si se ha encontrado o no y el dato encontrado


    def update(self, data, uide):
        '''
        Funcion para actualizar datos de un archivo json
        [Nota: Cada dato json necesita al menos 1 elemento identificador unico (uide), si no es asi, la actualizacion se producira en el primer dato con dicho elemento uide que se encuentre]
        '''
        file_data = self.read() # Leer todo el archivo json

        # Buscar la posicion del dato en el contenido json
        found = 0 # Posicion encontrada a 0
        i = 0 # Posicion inicial del dato a 0
        for msg in file_data['Content']: # Para cada dato json en el archivo json
            if data[uide] == msg[uide]: # Si el dato json tiene el UIDE buscado
                found = 1 # Marcar que se ha encontrado la posicion
                break # Interrumpir y salir del bucle
            i = i + 1 # Incrementar la posicion del dato

        if found: # Si se encontro en el archivo json datos con el UIDE buscado
            file_data['Content'][i] = data # Actualizamos los datos json que contiene ese UIDE
            self.write(file_data) # Escribimos el dato actualizado en el archivo json
        else: # No se encontro ningun dato json con dicho UIDE
            print("    Error: UIDE no encontrado en el archivo, o el archivo no existe") # Escribir en consola el error


    def update_twice(self, data, uide1, uide2):
        '''
        Funcion para actualizar datos de un archivo json
        [Nota: Cada dato json necesita al menos 1 elemento identificador unico (uide), si no es asi, la actualizacion se producira en el primer elemento que se encuentre]
        '''
        file_data = self.read() # Leer todo el archivo json

        # Buscar la posicion del dato en el contenido json
        found = 0 # Posicion encontrada a 0
        i = 0 # Posicion inicial del dato a 0
        for msg in file_data['Content']: # Para cada dato json en el archivo json
            if (data[uide1] == msg[uide1]) and (data[uide2] == msg[uide2]): # Si el dato json tiene el UIDE buscado
                found = 1 # Marcar que se ha encontrado la posicion
                break # Interrumpir y salir del bucle
            i = i + 1 # Incrementar la posicion del dato

        if found: # Si se encontro en el archivo json datos con el UIDE buscado
            file_data['Content'][i] = data # Actualizamos los datos json que contiene ese UIDE
            self.write(file_data) # Escribimos el dato actualizado en el archivo json
        else: # No se encontro ningun dato json con dicho UIDE
            print("    Error: UIDE no encontrado en el archivo, o el archivo no existe") # Escribir en consola el error


    def clear_content(self):
        '''Funcion para limpiar todos los datos de un archivo json'''
        try: # Intentar abrir el archivo
            self.lock.acquire() # Cerramos (adquirimos) el mutex
            if os.path.exists(self.file_name) and os.stat(self.file_name).st_size: # Si el archivo existe y no esta vacio
                with open(self.file_name, 'w', encoding="utf-8") as f: # Abrir el archivo en modo escritura (sobre-escribe)
                    f.write('\n{\n    "Content": [\n    ]\n}\n') # Escribir la estructura de contenido basica
        except: # Error intentando abrir el archivo
            print("    Error cuando se abria para escritura, el archivo {}".format(self.file_name)) # Escribir en consola el error
        finally: # Para acabar, haya habido excepcion o no
            self.lock.release() # Abrimos (liberamos) el mutex


    def delete(self):
        '''Funcion para eliminar un archivo json'''
        self.lock.acquire() # Cerramos (adquirimos) el mutex
        if os.path.exists(self.file_name): # Si el archivo existe
            os.remove(self.file_name) # Eliminamos el archivo
        self.lock.release() # Abrimos (liberamos) el mutex
