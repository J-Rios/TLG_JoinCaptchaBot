# -*- coding: utf-8 -*-

'''
Script:
    tsjson.py
Description:
    Thread-Safe JSON files read/write library.
Author:
    Jose Miguel Rios Rubio
Creation date:
    20/07/2017
Last modified date:
    30/12/2022
Version:
    1.2.1
'''

###############################################################################
### Standard Libraries

# Operating System Library
import os

# JSON Library
import json

# Collections Data Types Library
from collections import OrderedDict

# Threads and Multi-tasks Library
from threading import Lock

###############################################################################
### Thread-Safe JSON Class

class TSjson(object):
    '''
    Thread-Safe JSON files read/write class.
    '''

    def __init__(self, file_name):
        '''
        Class Constructor.
        It initializes the Mutex Lock element and get the file path.
        '''
        self.lock = Lock()
        self.file_name = file_name


    def read(self):
        '''
        Thread-Safe Read of JSON file.
        It locks the Mutex access to the file, checks if the file exists
        and is not empty, and then reads it content and try to parse as
        JSON data and store it in an OrderedDict element. At the end,
        the lock is released and the read and parsed JSON data is
        returned. If the process fails, it returns None.
        '''
        read = {}
        # Try to read the file
        try:
            self.lock.acquire()
            # Check if file exists and is not empty
            if os.path.exists(self.file_name):
                # Check if file is not empty
                if os.stat(self.file_name).st_size:
                    # Read the file and parse to JSON
                    with open(self.file_name, "r", encoding="utf-8") as f:
                        read = json.load(f, object_pairs_hook=OrderedDict)
        except Exception as error:
            print(str(error))
            print("Error reading JSON file {}".format(self.file_name))
            read = None
        finally:
            self.lock.release()
        return read


    def write(self, data):
        '''
        Thread-Safe Write of JSON file.
        It checks and creates all the needed directories to file path if
        any doesn't exists. Then it locks the Mutex access to the file,
        opens and overwrites the file with the provided JSON data.
        '''
        write_result_ok = False
        if not data:
            return False
        # Check for directory path and create all needed directories
        directory = os.path.dirname(self.file_name)
        if not os.path.exists(directory):
            os.makedirs(directory)
        # Try to write the file
        try:
            self.lock.acquire()
            with open(self.file_name, 'w', encoding="utf-8") as f:
                json.dump(data, fp=f, ensure_ascii=False, indent=4)
            write_result_ok = True
        except Exception as error:
            print(str(error))
            print("Error writing JSON file {}".format(self.file_name))
        finally:
            self.lock.release()
        return write_result_ok


    def read_content(self):
        '''
        Read JSON file content data.
        It call to read() function to get the OrderedDict element of the
        file JSON data and then return the specific JSON data from the
        dict ("content" key).
        '''
        read = self.read()
        if read is None:
            return {}
        if read == {}:
            return {}
        return read['Content']


    def write_content(self, data):
        '''
        Write JSON file content data.
        It checks and creates all the needed directories to file path if
        any doesn't exists.
        '''
        write_result_ok = False
        if not data:
            return False
        # Check for directory path and create all needed directories
        directory = os.path.dirname(self.file_name)
        if not os.path.exists(directory):
            os.makedirs(directory)
        # Try to write the file
        try:
            self.lock.acquire()
            # Check if file exists and is not empty
            if os.path.exists(self.file_name) \
            and os.stat(self.file_name).st_size:
                # Read the file, parse to JSON and add read data to
                # dictionary content key
                with open(self.file_name, "r", encoding="utf-8") as f:
                    content = json.load(f, object_pairs_hook=OrderedDict)
                content['Content'].append(data)
                # Overwrite the file with the new content data
                with open(self.file_name, 'w', encoding="utf-8") as f:
                    json.dump(content, fp=f, ensure_ascii=False, indent=4)
                write_result_ok = True
            # If the file doesn't exist or is empty
            else:
                # Write the file with an empty content data
                with open(self.file_name, 'w', encoding="utf-8") as f:
                    f.write('\n{\n    "Content": []\n}\n')
                # Read the file, parse to JSON and add read data to
                # dictionary content key
                with open(self.file_name, "r", encoding="utf-8") as f:
                    content = json.load(f)
                content['Content'].append(data)
                # Overwrite the file with the new content data
                with open(self.file_name, 'w', encoding="utf-8") as f:
                    json.dump(content, fp=f, ensure_ascii=False, indent=4)
                write_result_ok = True
        except IOError as error:
            print("I/O error({0}): {1}".format(error.errno, error.strerror))
        except ValueError:
            print("Data conversion error")
        except Exception as error:
            print(str(error))
            print("Error writing content JSON file {}".format(self.file_name))
        finally:
            self.lock.release()
        return write_result_ok


    def is_in(self, data):
        '''
        Check if provided key exists in JSON file data.
        It reads all the JSON file data and check if the key is present.
        '''
        # Read the file data
        file_data = self.read()
        if file_data is None:
            return False
        if file_data == {}:
            return False
        # Search element with UID
        for _data in file_data['Content']:
            if data == _data:
                return True
        return False


    def is_in_position(self, data):
        '''
        Check if provided key exists in JSON file data and get the
        index from where it is located.
        '''
        i = 0
        found = False
        # Read the file data
        file_data = self.read()
        if file_data is None:
            return False, -1
        if file_data == {}:
            return False, -1
        # Search and get index of element with UID
        for _data in file_data['Content']:
            if data == _data:
                found = True
                break
            i = i + 1
        return found, i


    def remove_by_uide(self, element_value, uide):
        '''
        From the JSON file content, search and remove an element that
        has a specified Unique Identifier (UID) key.
        Note: If there are elements with same UIDs, only the first one
        detected will be removed.
        '''
        found = False
        # Read the file data
        file_content = self.read_content()
        if file_content == {}:
            return False
        # Search and remove element with UID
        for data in file_content:
            if data[uide] == element_value:
                found = True
                file_content.remove(data)
                break
        # Rewrite to file after deletion
        self.clear_content()
        if file_content:
            self.write_content(file_content[0])
        return found


    def search_by_uide(self, element_value, uide):
        '''
        From the JSON file content, search and get an element that has
        a specified Unique Identifier (UID) key.
        Note: If there are elements with same UIDs, only the first one
        detected will be detected.
        '''
        result = dict()
        result['found'] = False
        result['data'] = None
        # Read the file data
        file_data = self.read()
        if file_data is None:
            return result
        if file_data == {}:
            return result
        # Search and get element with UID
        for element in file_data['Content']:
            if element:
                if element_value == element[uide]:
                    result['found'] = True
                    result['data'] = element
                    break
        return result


    def update(self, data, uide):
        '''
        From the JSON file content, search and update an element that
        has a specified Unique Identifier (UID) key.
        Note: If there are elements with same UID, only the first one
        detected will be updated.
        '''
        i = 0
        found = False
        # Read the file data
        file_data = self.read()
        if file_data is None:
            return False
        if file_data == {}:
            return False
        # Search and get index of element with UID
        for msg in file_data['Content']:
            if data[uide] == msg[uide]:
                found = True
                break
            i = i + 1
        # Update UID element data and overwrite JSON file
        if found:
            file_data['Content'][i] = data
            self.write(file_data)
        else:
            print("Error: Element with UID no found in JSON file.")
        return found


    def update_twice(self, data, uide1, uide2):
        '''
        From the JSON file content, search and update an element that
        has two specified Unique Identifier (UID) keys.
        Note: If there are elements with same UIDs, only the first one
        detected will be updated.
        '''
        i = 0
        found = False
        file_data = self.read()
        # Read the file data
        file_data = self.read()
        if file_data is None:
            return False
        if file_data == {}:
            return False
        # Search and get index of element with both UIDs
        for msg in file_data['Content']:
            if (data[uide1] == msg[uide1]) and (data[uide2] == msg[uide2]):
                found = True
                break
            i = i + 1
        # Update UID element data and overwrite JSON file
        if found:
            file_data['Content'][i] = data
            self.write(file_data)
        else:
            print("Error: Element with UID no found in JSON file.")
        return found


    def clear_content(self):
        '''
        Funcion para limpiar todos los datos de un archivo json.
        It locks the Mutex access to the file, and if the file exists
        and is not empty, the content is cleared to a default skelleton.
        '''
        clear_ok = False
        try:
            self.lock.acquire()
            if os.path.exists(self.file_name) \
            and os.stat(self.file_name).st_size:
                with open(self.file_name, 'w', encoding="utf-8") as f:
                    f.write('\n{\n    "Content": [\n    ]\n}\n')
                clear_ok = True
        except Exception as error:
            print(str(error))
            print("Fail to clear JSON file {}".format(self.file_name))
        finally:
            self.lock.release()
        return clear_ok


    def delete(self):
        '''
        Remove a JSON file.
        '''
        self.lock.acquire()
        if os.path.exists(self.file_name):
            os.remove(self.file_name)
        self.lock.release()
