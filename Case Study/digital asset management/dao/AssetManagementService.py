from abc import ABC, abstractmethod
from entity.Asset import Asset
class AssetManagementService(ABC):
    @abstractmethod
    def addAsset(self,asset:Asset)->bool:
        pass
    @abstractmethod
    def updateAsset(self,asset:Asset)->bool:
        pass
    @abstractmethod
    def deleteAsset(self,asset_id:int)->bool:
        pass
    @abstractmethod
    def allocateAsset(self,asset_id:int,employee_id:int,allocation_date:str)->bool:
        pass
    @abstractmethod
    def deallocateAsset(self,asset_id:int,employee_id:int,return_date:str)->bool:
        pass
    @abstractmethod
    def performMaintenance(self,asset_id:int,maintenance_date:str,description:str,cost:float)->bool:
        pass
    @abstractmethod
    def reserveAsset(self,asset_id:int,employee_id:int,reservation_date:str,start_date:str,end_date:str)->bool:
        pass
    @abstractmethod
    def withdrawReservation(self,reservation_id:int)->bool:
        pass
