class MongoDBRepository:
    def __init__(self, database: AsyncIOMotorDatabase):
        self.db = database