from .BaseDataMoldel import BaseDataModel
from .db_schemes import Asset
from .enums.DataBaseEnum import BaseDataEnum
from bson import ObjectId

class AssetModel(BaseDataModel):
    def __init__(self, db_client: object):
        super().__init__(db_client=db_client)  
        self.collection = self.db_client[BaseDataEnum.COLLECTION_ASSETS_NAME.value]
        
    @classmethod
    async def create_instance(cls, db_client: object):
        instance = cls(db_client)
        await instance.init_collection()
        return instance
    
    
    async def init_collection(self):
        all_colections = await self.db_client.list_collection_names()
        if BaseDataEnum.COLLECTION_ASSETS_NAME.value not in all_colections:
            self.collection = self.db_client[BaseDataEnum.COLLECTION_ASSETS_NAME.value]
            indexes = Asset.get_indexes()
            for index in indexes:
                await self.collection.create_index(
                    index["key"],
                    name=index['name'],
                    unique=index['unique']
                )
                
    async def create_asset(self, asset: Asset):
        result = await self.collection.insert_one(asset.dict(by_alias=True, exclude_unset=True))
        asset.id = result.inserted_id
        return asset
    
    async def get_all_project_assets(self, assets_project_id: str, asset_type: str):
        
        records =  await self.collection.find({
            "assets_project_id" : ObjectId(assets_project_id) if isinstance(assets_project_id, str) else assets_project_id,
            "assets_type": asset_type
        }).to_list(length=None)
        
        return [
            Asset(**record)
            for record in records
        ]
        
    async def get_asset_record(self, assets_project_id: str, assets_name: str):
        record = await self.collection.find_one({
            "assets_project_id" : ObjectId(assets_project_id) if isinstance(assets_project_id, str) else assets_project_id,
            "assets_name": assets_name
        })
        
        if record:
            return Asset(**record)
        return None
        