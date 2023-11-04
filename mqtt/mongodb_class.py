import pymongo
import datetime

# Table structure:"entries"
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
  
		self.entries_collection_name = "entries"
		self.lots_collection_name = "lots"
  
		# Connect to database
		if username==None or password==None:
			self.client = pymongo.MongoClient(f"mongodb://{self.ip}:{self.port}/")
		else:
			self.client = pymongo.MongoClient(f"mongodb+srv://{username}:{password}@{self.ip}/")
		print(f"Connected to database")
   
		# Check if database exists
		db_list = self.client.list_database_names()
		if not self.db_name in db_list:
			if not force:
				raise Exception(f"Cannot find database {self.db_name}")
			print(f"Cannot find database {self.db_name} creating one")
		self.db = self.client[self.db_name]
  
		# Check if tables exist
		tb_list = self.db.list_collection_names()
		# Create entries table if does not exist
		if not self.entries_collection_name in tb_list:
			if not force:
				raise Exception("Cannot find table entries")
			print("Creating table entries")
		self.db[self.entries_collection_name]
		# Create lots table if does not exist
		if not self.lots_collection_name in tb_list:
			if not force:
				raise Exception("Cannot find table lots")
			print("Creating table lots")
		self.db[self.lots_collection_name]
  
		# Restore indices if keep previous data (by default)
		if keep_previous_data:
			self.restore_indices()
		else:
			self.hard_reset()
	
	def hard_reset(self):
		print("Warning: hard reseting database, all previous data will be lost")
		tb = self.db[self.lots_collection_name]
		tb.drop()
		tb = self.db[self.entries_collection_name]
		tb.drop()
		self.lots_index = 0
		self.db[self.entries_collection_name]
		self.db[self.lots_collection_name]
  
	def restore_indices(self):
		lots = self.db[self.lots_collection_name].find()
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
		result = None
		if update_all:
			result = tb.update_many(cond, set_val).modified_count
			return result
		else:
			result = tb.update_one(cond, set_val)
			if result.matched_count > 0:
				if result.modified_count > 0:
					print("The document was updated.")
				else:
					print("The document matched the query but was not updated.")
			else:
				print("No document matched the query.")
			return result.modified_count
			
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

	# add a new parking lot to the system
	def add_lot(self, availability: int):
		if availability<0:
			raise Exception("Invalid availability")
		record = {"lotId" : self.lots_index, "isAvailable": availability}
		self.lots_index = self.lots_index + 1
		self.insert(self.lots_collection_name, record)
		print(f'Added lot to collection {self.lots_collection_name}: {record}')
		return self.lots_index - 1

	# record down a new entry a car has made
	def add_entry(self, plate: str, lot_id: int = None):
		if plate==None:
			raise Exception("Invalid plate")
		record = {
    			# "entryId" : self.entries_index, 
    			"plate" : plate, 
    			"lotId": lot_id if lot_id is not None else -1, 
    			"time" : datetime.datetime.utcnow()
    	}
		self.insert(self.entries_collection_name, record)
		print(f'Added entry to collection {self.entries_collection_name}: {record}')

	def update_car_lot_entry(self, plate: str, lot_id: int):
		cond = {"plate" : plate}
		record = {"lotId" : lot_id}
		updates = self.update(self.entries_collection_name, cond, record)
		if updates==0:
			raise Exception("Cannot find plate {plate}")
		if updates>1:
			raise Exception(f"Internal Error: multiple plates {plate} found, check db manually")
		print(f'Updated plate {plate} parked at lot {lot_id}')

	# update the availability of a lot
	def update_availability(self, lot_id: int, new_availability: bool):
		lot_id = int(lot_id)
		cond = {"lotId" : lot_id}
		record = {"lotId" : lot_id, "isAvailable": new_availability}
		updates = self.update(self.lots_collection_name, cond, record, False)
		if updates==0:
			raise Exception(f"Cannot update availability of lot {lot_id}")
		if updates>1:
			raise Exception(f"Internal Error: multiple lots with lotId {lot_id} found, check db manually")
		print(f'Updated availability of lot {lot_id} to {new_availability}')

	# get the last entry a car has made, this is what u wanna used for calculation
	def get_last_entry(self, plate: str):
		cond = {"plate" : plate}
		results = self.select(self.entries_collection_name, cond)
		ans = []
		for result in results:
			ans.append(result)
		result = None
		for entry in ans:
			if result==None or entry["time"]>result["time"]:
				result = entry
		if result is None:
			raise Exception(f'Cannot find car {plate}')
		else:
			print(f'Car {plate} entered carpark at {result}')
			return result
 
	def get_last_entry_time(self, carplate):
		return self.get_last_entry(carplate)['time']

	# get all entries a car has made
	def get_all_entries(self, plate: str):
		cond = {"plate" : plate}
		results = self.select(self.entries_collection_name, cond)
		ans = []
		for result in results:
			ans.append(result)
		return ans

	# get number of free lots in parking lot lot_id
	def get_availability(self, lot_id: int):
		cond = {"lot_id" : lot_id}
		results = self.select(self.lots_collection_name, cond)
		ans = []
		for result in results:
			ans.append(result)
		if len(ans)==0:
			raise Exception(f"Cannot find lot with lot_id {str(lot_id)}")
		if len(ans)>1:
			raise Exception(f"Internal Error: multiple lots with lot_id {str(lot_id)} found, check db manually")	
		return ans[0]["availability"]

	def get_nearest_available_lot(self):
		nearest_lot = self.select("lots", {'isAvailable': True}).sort("lotId", 1).limit(1)
		if nearest_lot:
			print(f"Nearest Lot ID: {nearest_lot['lotId']}, Availability: {nearest_lot['isAvailable']}")
			return nearest_lot['lotId']
		else:
			print("No available lots.")
			return None
 
	def get_number_of_available_lots(self):
		count = self.db["lots"].count_documents({'isAvailable': True})
		print(f"Number of available lots in carpark: {count}")
		return count
 
	def get_number_of_lots(self):
		count = self.db["lots"].count_documents({})
		print(f"Number of lots in carpark: {count}")
		return count
