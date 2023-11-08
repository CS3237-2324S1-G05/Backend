import pymongo
import datetime
import constants

# entries: (__id, carplate: str, lotId: int, time: datetime)
# lots: (__id, lotId: int, isAvailable: bool )
class Database:  
	# Username and password shall be provided by caller
	# these info are neither hardcoded nor stored in heap for security reasons
	# if either of these two fields is None, will try to connect in no auth mode
	# Errors are not catched at this level and shall be processed directly by the caller 
	# if force is set to true, collections will be created if not exist
	# if keep_previous_data is set to false, the two collections will be dropped and recreated (used for testing)
	# Username = CS3237_Group5, Password = cs3237555
	# def __init__(self, username=None, password=None, force=True, keep_previous_data=True):
	def __init__(self, logger, username=None, password=None, force=True, keep_previous_data=True):
		self.logger = logger	
		self.ip = constants.MONGODB_IP
		self.port = constants.MONGODB_PORT
		self.db_name = constants.MONGODB_DATABASE_NAME
		self.lots_index = 0
  
		self.entry_collection_name = constants.MONGODB_ENTRY_COLLECTION_NAME
		self.lot_collection_name = constants.MONGODB_LOT_COLLECTION_NAME
  
		# Connect to database
		if username==None or password==None:
			self.client = pymongo.MongoClient(f"mongodb://{self.ip}:{self.port}/")
		else:
			self.client = pymongo.MongoClient(f"mongodb+srv://{username}:{password}@{self.ip}/")
   
		# Check if database exists
		db_list = self.client.list_database_names()
		if not self.db_name in db_list:
			if not force:
				raise Exception(f"Cannot find database {self.db_name}")
			self.logger.info(f"Cannot find database {self.db_name} creating one")
		self.db = self.client[self.db_name]
  
		# Check if collections exist
		col_list = self.db.list_collection_names()
		# Create entries collection if does not exist
		if not self.entry_collection_name in col_list:
			if not force:
				raise Exception(f"Cannot find collection {self.entry_collection_name}")
			self.logger.info(f"Creating collection {self.entry_collection_name}")
		self.db[self.entry_collection_name]
		# Create lots collection if does not exist
		if not self.lot_collection_name in col_list:
			if not force:
				raise Exception(f"Cannot find collection {self.lot_collection_name}")
			self.logger.info(f"Creating collection {self.lot_collection_name}")
		self.db[self.lot_collection_name]
  
		# Restore indices if keep previous data (by default)
		if keep_previous_data:
			self.restore_indices()
		else:
			self.hard_reset()
	
	def hard_reset(self):
		self.logger.info("Warning: hard reseting database, all previous data will be lost")
		col = self.db[self.lot_collection_name]
		col.drop()
		col = self.db[self.entry_collection_name]
		col.drop()
		self.lots_index = 0
		self.db[self.entry_collection_name]
		self.db[self.lot_collection_name]
  
	def restore_indices(self):
		lots = self.db[self.lot_collection_name].find()
		self.lots_index = 0
		for _ in lots:
			self.lots_index = self.lots_index + 1

	# destructor, performs a proper exit
	# will be called directly by python interpreter
	def __del__(self):
		self.client.close()
		
	# INSERT INTO <col_name> VALUES <val>
	# col_name should be a string
	# val should be a dict, with correct column name - value pairs specified
	# returns the _id allocated by MongoDB
	def insert(self, col_name, val):
		col = self.db[col_name]
		return col.insert_one(val)

	# UPDATE <col_name> SET <new_val> WHERE <cond>
	# col_name should be a string
	# cond, new_val should both be dict of column name - value pairs
	# if update_all is true, all entries that matches with cond will be updated
	# otherwise only the first occurence will be updated
	# returns number of entries modified
	def update(self, col_name, cond, new_val, update_all=True):
		col = self.db[col_name]
		set_val = {"$set" : new_val}
		result = None
		if update_all:
			result = col.update_many(cond, set_val).modified_count
			return result
		else:
			result = col.update_one(cond, set_val)
			if result.matched_count > 0:
				if result.modified_count > 0:
					self.logger.info("The document was updated.")
				else:
					self.logger.error("The document matched the query but was not updated.")
			else:
				self.logger.error("No document matched the query.")
			return result.modified_count
			
	# DELETE FROM <col_name> WHERE <cond>
	# col_name should be a string
	# cond should be a dict of column name - value pairs
	# if delete_all is true, all entries that matches with cond will be deleted
	# otherwise only the first occurence will be deleted
	# returns number of entries deleted
	def delete(self, col_name, cond, delete_all=True):
		col = self.db[col_name]
		if delete_all:
			return col.delete_many(cond).deleted_count
		col.delete_one(cond)
		return 1
	
	# SELECT * FROM <col_name> WHERE <cond>
	# col_name should be a string
	# cond should be a dict of column name - value pairs
	# returns the query result
	def select(self, col_name, cond):
		col = self.db[col_name]
		return col.find(cond)

	# add a new parking lot to the system
	def add_lot(self):
   # True by default
		record = {"lotId" : self.lots_index, "isAvailable": True}
		self.lots_index = self.lots_index + 1
		self.insert(self.lot_collection_name, record)
		self.logger.info(f'Added lot to collection {self.lot_collection_name}: {record}')
		return self.lots_index - 1

	# record down a new entry a car has made
	def add_entry(self, carplate: str, lot_id: int = None):
		if carplate==None:
			raise Exception("Invalid carplate")
		elif lot_id is not None and (lot_id < 0 or lot_id >= self.get_number_of_lots()):
			raise Exception("Invalid lot id")
		else:
			record = {
      	"carplate" : carplate,
      	"time" : datetime.datetime.utcnow()
			}
			self.insert(self.entry_collection_name, record)
			self.logger.info(f'Added entry to collection {self.entry_collection_name}: {record}')

	def update_car_lot_entry(self, carplate: str, lot_id: int):
		col = self.db[self.entry_collection_name]
		document_to_update = col.find_one({'carplate': carplate}, sort=[('time', pymongo.DESCENDING)])
		if document_to_update is None:
			raise Exception(f'Cannot find car {carplate}')
		# Add lotId to the entry
		result = col.update_one({'_id': document_to_update['_id']}, {'$set': {'lotId': lot_id}})
		if result.matched_count == 0:
			self.logger.error(f'Could not add lot id for entry for car {carplate}')
		else:
			self.logger.info(f'Updated entry to collection {self.entry_collection_name}: {carplate} at lot {lot_id}')

	# update the availability of a lot
	def update_lot_availability(self, lot_id: int, new_availability: bool):
		cond = {"lotId" : lot_id}
		record = {"lotId" : lot_id, "isAvailable": new_availability}
		updates = self.update(self.lot_collection_name, cond, record, False)
		if updates==0:
			raise Exception(f"Cannot update availability of lot {lot_id}")
		if updates>1:
			raise Exception(f"Internal Error: multiple lots with lotId {lot_id} found, check db manually")
		self.logger.info(f'Updated availability of lot {lot_id} to {new_availability}')

	# get the last entry a car has made, this is what u wanna used for calculation
	def get_last_entry(self, carplate: str):
		cond = {"carplate" : carplate}
		results = self.select(self.entry_collection_name, cond)
		ans = []
		for result in results:
			ans.append(result)
		result = None
		for entry in ans:
			if result==None or entry["time"]>result["time"]:
				result = entry
		if result is None:
			raise Exception(f'Cannot find car {carplate}')
		else:
			self.logger.info(f'Car {carplate} entered carpark at {result}')
			return result
 
	def get_last_entry_time(self, carplate):
		return self.get_last_entry(carplate)['time']

	# get all entries a car has made
	def get_all_entries(self, carplate: str):
		cond = {"carplate" : carplate}
		results = self.select(self.entry_collection_name, cond)
		ans = []
		for result in results:
			ans.append(result)
		return ans

	# get number of free lots in parking lot lot_id
	def get_availability(self, lot_id: int):
		cond = {"lotId" : lot_id}
		cursor = self.select(self.lot_collection_name, cond)
		try:
			return cursor.next()["isAvailable"]
		except:
			raise Exception(f"Cannot find lot with lotId {str(lot_id)}")	

	def get_nearest_available_lot(self):
		nearest_lot = self.select(constants.MONGODB_LOT_COLLECTION_NAME, {'isAvailable': True}).sort("lotId", 1).limit(1)
		for lot in nearest_lot:
			self.logger.info(f"Nearest Lot ID: {lot['lotId']}, Availability: {lot['isAvailable']}")
			return lot['lotId']
		else:
			self.logger.info("No available lots.")
			return None
 
	def get_number_of_available_lots(self):
		count = self.db[self.lot_collection_name].count_documents({'isAvailable': True})
		self.logger.info(f"Number of available lots in carpark: {count}")
		return count
 
	def get_number_of_lots(self):
		count = self.db[self.lot_collection_name].count_documents({})
		self.logger.info(f"Number of lots in carpark: {count}")
		return count

	def get_car_lot(self, carplate: str):
		cursor = self.select(constants.MONGODB_ENTRY_COLLECTION_NAME, {'carplate': carplate}).sort("time", -1).limit(1)
		try:
			lot = cursor.next()['lotId']
			self.logger.info(f"Car {carplate} is parked at lot {lot}")
			return str(lot)
		except:
			self.logger.error(f"Cannot find lot where car {carplate} is parked")
			return None
 