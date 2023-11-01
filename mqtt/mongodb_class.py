import pymongo
import datetime


# Table structure:
# entries: (__id, entry_id: int, plate: str, lot_id: int, time: datetime)
# lots: (__id, lot_id: int, availability: int )
class Database:
	
	# Username and password shall be provided by caller
	# these info are neither hardcoded nor stored in heap for security reasons
	# if either of these two fields is None, will try to connect in no auth mode
	# Errors are not catched at this level and shall be processed directly by the caller 
	# if force is set to true, tables will be created if not exist
	# if keep_previous_data is set to false, the two tables will be dropped and recreated (used for testing)
	# Username = CS3237_Group5, Password = cs3237555
	def __init__(self, username=None, password=None, force=True, keep_previous_data=True):
		self.ip = "cluster0.8tghxvd.mongodb.net"
		self.port = "27017"
		self.db_name = "parking_lot"
		self.lots_index = 0
		self.entries_index = 0
		if username==None or password==None:
			self.client = pymongo.MongoClient("mongodb://"+self.ip+":"+self.port+"/")
		else:
			self.client = pymongo.MongoClient("mongodb+srv://"+username+":"+password+"@"+self.ip+"/")
		db_list = self.client.list_database_names()
		if not self.db_name in db_list:
			if not force:
				raise Exception("Cannot find database "+self.db_name)
			print("Cannot find database \""+self.db_name+"\", creating one")
		self.db = self.client[self.db_name]
		tb_list = self.db.list_collection_names()
		if not "entries" in tb_list:
			if not force:
				raise Exception("Cannot find table entries")
			print("Creating table entries")
		self.db["entries"]
		if not "lots" in tb_list:
			if not force:
				raise Exception("Cannot find table lots")
			print("Creating table lots")
		self.db["lots"]
		if not keep_previous_data:
			self.hard_reset()
		else:
			self.restore_indices()
	
	def hard_reset(self):
		print("Warning: hard reseting database, all previous data will be lost")
		tb = self.db["lots"]
		tb.drop()
		tb = self.db["entries"]
		tb.drop()
		self.entries_index = 0
		self.lots_index = 0
		self.db["entries"]
		self.db["lots"]
  
	def restore_indices(self):
		entries = self.db["entries"].find()
		self.entries_index = 0
		for _ in entries:
			self.entries_index = self.entries_index + 1
		lots = self.db["lots"].find()
		self.lots_index = 0
		for _ in lots:
			self.lots_index = self.lots_index + 1

	# destructor, performs a proper exit
	# will be called directly by python interpreter
	def __del__(self):
		self.client.close()
		
	# INSERT INTO <tb_name> VALUES <val>
	# tb_name should be a string
	# val should be a dict, with correct column name - value pairs specified
	# returns the _id allocated by MongoDB
	def insert(self, tb_name, val):
		tb = self.db[tb_name]
		return tb.insert_one(val)

	# UPDATE <tb_name> SET <new_val> WHERE <cond>
	# tb_name should be a string
	# cond, new_val should both be dict of column name - value pairs
	# if update_all is true, all entries that matches with cond will be updated
	# otherwise only the first occurence will be updated
	# returns number of entries modified
	def update(self, tb_name, cond, new_val, update_all=True):
		tb = self.db[tb_name]
		set_val = {"$set" : new_val}
		if update_all:
			return tb.update_many(cond, set_val).modified_count
		tb.update_one(cond, set_val)
		return 1
			
	# DELETE FROM <tb_name> WHERE <cond>
	# tb_name should be a string
	# cond should be a dict of column name - value pairs
	# if delete_all is true, all entries that matches with cond will be deleted
	# otherwise only the first occurence will be deleted
	# returns number of entries deleted
	def delete(self, tb_name, cond, delete_all=True):
		tb = self.db[tb_name]
		if delete_all:
			return tb.delete_many(cond).deleted_count
		tb.delete_one(cond)
		return 1
	
	# SELECT * FROM <tb_name> WHERE <cond>
	# tb_name should be a string
	# cond should be a dict of column name - value pairs
	# returns the query result
	def select(self, tb_name, cond):
		tb = self.db[tb_name]
		return tb.find(cond)

	# TODO
	# add a new parking lot to the system
	def add_lot(self, availability: int):
		if availability<0:
			raise Exception("Invalid availability")
		record = {"lotId" : self.lots_index, "isAvailable": availability}
		self.lots_index = self.lots_index + 1
		self.insert("lots", record)
		return self.lots_index - 1

	# record down a new entry a car has made
	def add_entry(self, plate: str, lot_id: int = None):
		if plate==None:
			raise Exception("Invalid plate")
		record = {
    			"entryId" : self.entries_index, 
    			"plate" : plate, 
    			"lotId": lot_id if lot_id is not None else -1, 
    			"time" : datetime.datetime.utcnow()
    	}
		self.insert("entries", record)
		self.entries_index = self.entries_index + 1
		return self.entries_index - 1

	# update the availability of a lot
	def update_availability(self, lot_id: int, new_availability: int):
		# TODO
		if new_availability<0:
			raise Exception("Invalid availability")
		cond = {"lot_id" : lot_id}
		record = {"lot_id" : lot_id, "isAvailable": new_availability}
		updates = self.update("lots", cond, record)
		if updates==0:
			raise Exception("Cannot find lot with lot_id "+str(lot_id))
		if updates>1:
			raise Exception("Internal Error: multiple lots with lot_id"+str(lot_id)+" found, check db manually")

	# get the last entry a car has made, this is what u wanna used for calculation
	def get_last_entry(self, plate: str):
		cond = {"plate" : plate}
		results = self.select("entries", cond)
		ans = []
		for result in results:
			ans.append(result)
		result = None
		for entry in ans:
			if result==None or entry["time"]>result["time"]:
				result = entry
		return result

	# get all entries a car has made
	def get_all_entries(self, plate: str):
		cond = {"plate" : plate}
		results = self.select("entries", cond)
		ans = []
		for result in results:
			ans.append(result)
		return ans

	# TODO: Redo
	# get number of free lots in parking lot lot_id
	def get_availability(self, lot_id: int):
		cond = {"lot_id" : lot_id}
		results = self.select("lots", cond)
		ans = []
		for result in results:
			ans.append(result)
		if len(ans)==0:
			raise Exception("Cannot find lot with lot_id "+str(lot_id))
		if len(ans)>1:
			raise Exception("Internal Error: multiple lots with lot_id"+str(lot_id)+" found, check db manually")	
		return ans[0]["availability"]

	# def is_available(self, lot_id: int):
	# 	return self.get_availability(lot_id) > 0

	# def db_store_carplate(carplate):

	# def db_get_car_entrance_time(carplate):




	# def db_get_nearest_lot():

	# def db_store_carplate_and_lot_number(carplate, lot_number):

	# def db_update_lot_availability(lot_number, is_available):
					
	# def db_get_number_of_available_lots():
			
	# def db_get_lot_number(carplate):
 
	if __name__ == '__main__':
		db = Database()
