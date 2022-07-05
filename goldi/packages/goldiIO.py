import json
import os
import sys

def fetch_data(filename, attr):
    attr = str(attr)
    dataDir = os.path.join(os.getcwd(), 'data/')
    fileDir = os.path.join(dataDir, filename + '.json')
    try:
        with open(fileDir, 'r') as jsonData:
            tmp = json.load(jsonData)
    except Exception:
        return None
    try:
        return tmp[attr]
    except KeyError:
        return None

def fetch_all_data(filename):
    dataDir = os.path.join(os.getcwd(), 'data/')
    fileDir = os.path.join(dataDir, filename + '.json')
    try:
        with open(fileDir, 'r') as jsonData:
            return json.load(jsonData)
    except Exception:
        return None

def write_data(filename, attr, val):
    attr = str(attr)
    dataDir = os.path.join(os.getcwd(), 'data/')
    fileDir = os.path.join(dataDir, filename + '.json')
    try:
        with open(fileDir, 'r') as jsonData:
            tmp = json.load(jsonData)
    except Exception:
        return False
    tmp[attr] = val
    try:
        with open(fileDir, 'w') as jsonData:
            json.dump(tmp, jsonData)
        return True
    except Exception:
        return False

def clear_data(filename, attr = None):
    dataDir = os.path.join(os.getcwd(), 'data/')
    fileDir = os.path.join(dataDir, filename + '.json')
    if attr is None: # Clear all
        try:
            with open(fileDir, 'w') as jsonData:
                json.dump({}, jsonData)
            return True
        except Exception:
            return False
    else:
        try:
            with open(fileDir, 'r') as jsonData:
                tmp = json.load(jsonData)
        except Exception:
            return False
        try:
            del tmp[attr]
        except Exception:
            pass
        try:
            with open(fileDir, 'w') as jsonData:
                json.dump(tmp, jsonData)
            return True
        except Exception:
            return False