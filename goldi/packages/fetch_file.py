import pickle
import os
import sys

def fetch_data(file_name, var_name):
	data_dir = os.path.join(os.getcwd(), 'goldi/modules/data')
	file_dir = os.path.join(data_dir, file_name)
	try:
		with open(file_dir, 'rb') as handle:
			tmp_dict = pickle.load(handle)
	except Exception:
		return None
	try:
		return tmp_dict[var_name]
	except KeyError:
		return None

def write_new_data(file_name, var_name, var_val):
	data_dir = os.path.join(os.getcwd(), 'goldi/modules/data')
	file_dir = os.path.join(data_dir, file_name)
	try:
		with open(file_dir, 'rb') as handle:
			tmp_dict = pickle.load(handle)
	except Exception:
		return False
	try:
		trash = tmp_dict[var_name]
		return False
	except KeyError:
		tmp_dict[var_name] = var_val
	try:
		with open(file_dir, 'wb') as handle:
			pickle.dump(tmp_dict, handle)
		return True
	except Exception:
		return False

def write_data(file_name, var_name, var_val):
	data_dir = os.path.join(os.getcwd(), 'goldi/modules/data')
	file_dir = os.path.join(data_dir, file_name)
	try:
		with open(file_dir, 'rb') as handle:
			tmp_dict = pickle.load(handle)
	except Exception:
		return False
	try:
		trash = tmp_dict[var_name]
		tmp_dict[var_name] = var_val
	except KeyError:
		return False
	try:
		with open(file_dir, 'wb') as handle:
			pickle.dump(tmp_dict, handle)
		return True
	except Exception:
		return False
