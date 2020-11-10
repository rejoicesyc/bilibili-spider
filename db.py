import pymongo

class DB:
    def __init__(self,db_name,collection_name):
        self.client = pymongo.MongoClient(host='localhost', port=27017)
        self.biliCollection=self.client[db_name][collection_name]

    def insert(self,entry:dict):
        return self.biliCollection.insert_one(entry)

    def delete_one(self,key):
        return self.biliCollection.delete_one(key)

    def find(self,key:dict):
        return self.biliCollection.find(key)

    def find_all(self):
        return self.biliCollection.find()

    def count_all(self):
        return self.biliCollection.find().count()

    def modify(self):
        pass

    def drop(self):
        return self.biliCollection.drop()

# db=DB('bili','title1') 
# result=db.find_all()
# for each in result:
#     print(each)

# print(db.count_all())