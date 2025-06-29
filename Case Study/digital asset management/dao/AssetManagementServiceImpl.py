from exception.AssetNotFoundException import AssetNotFoundException
from exception.AssetNotMaintainException import AssetNotMaintainException
import mysql.connector
from dao.AssetManagementService import AssetManagementService
from util.DBConnUtil import DBConnUtil
from datetime import datetime

class AssetManagementServiceImpl(AssetManagementService):
    def addAsset(self,asset):
        try:
            conn=DBConnUtil.getConnection()
            if conn is None:
                print("Connection failed.")
                return False
            cursor=conn.cursor()
            query="insert into assets (name,type,serial_number,purchase_date,location,status,owner_id)" \
            " values (%s,%s,%s,%s,%s,%s,%s)"
            values=(asset.get_name(),asset.get_type(),asset.get_serial_number(),asset.get_purchase_date(),
                    asset.get_location(),asset.get_status(),asset.get_owner_id())
            cursor.execute(query,values)
            conn.commit()
            print("Asset added successfully.")
            return True
        except mysql.connector.Error as e:
            print(f"Database error during addAsset: {e}")
            return False
        finally:
            if conn:
                conn.close()

    def updateAsset(self,asset):
        try:
            conn=DBConnUtil.getConnection()
            if conn is None:
                print("Connection failed.")
                return False
            cursor=conn.cursor()
            query="update assets set name=%s,type=%s,serial_number=%s,purchase_date=%s,location=%s," \
            "status=%s,owner_id=%s where asset_id=%s"
            values=(asset.get_name(),asset.get_type(),asset.get_serial_number(),asset.get_purchase_date(),
                    asset.get_location(),asset.get_status(),asset.get_owner_id(),asset.get_asset_id())
            cursor.execute(query,values)
            conn.commit()
            if cursor.rowcount>0:
                print("Asset updated successfully.")
                return True
            else:
                print("Asset ID not found. No update performed.")
                return False
        except mysql.connector.Error as e:
            print(f"Database error during updateAsset: {e}")
            return False
        finally:
            if conn:
                conn.close()

    def deleteAsset(self, asset_id):
        try:
            conn = DBConnUtil.getConnection()
            if conn is None:
                print("Connection failed.")
                return False
            cursor = conn.cursor()

            # Step 1: Delete child records first
            cursor.execute("DELETE FROM reservations WHERE asset_id = %s", (asset_id,))
            cursor.execute("DELETE FROM asset_allocations WHERE asset_id = %s", (asset_id,))
            cursor.execute("DELETE FROM maintenance_records WHERE asset_id = %s", (asset_id,))

            # Step 2: Delete the asset itself
            cursor.execute("DELETE FROM assets WHERE asset_id = %s", (asset_id,))
            conn.commit()

            if cursor.rowcount > 0:
                print("Asset deleted successfully.")
                return True
            else:
                print("Asset ID not found.")
                return False

        except mysql.connector.Error as e:
            print(f"Database error during deleteAsset: {e}")
            return False
        finally:
            if conn:
                conn.close()


    def allocateAsset(self,asset_id,employee_id,allocation_date):
        try:
            conn=DBConnUtil.getConnection()
            if conn is None:
                print("Connection failed.")
                return False
            cursor=conn.cursor()
            check_query="select * from asset_allocations where asset_id=%s and return_date is null"
            cursor.execute(check_query,(asset_id,))
            if cursor.fetchone():
                print("Asset is already allocated and not returned.")
                return False
            insert_query="insert into asset_allocations (asset_id,employee_id,allocation_date,return_date) " \
            "values (%s,%s,%s,null)"
            cursor.execute(insert_query,(asset_id,employee_id,allocation_date))
            conn.commit()
            print("Asset allocated successfully.")
            return True
        except mysql.connector.Error as e:
            print(f"Database error during allocateAsset: {e}")
            return False
        finally:
            if conn:
                conn.close()

    def deallocateAsset(self,asset_id,employee_id,return_date):
        try:
            conn=DBConnUtil.getConnection()
            if conn is None:
                print("Connection failed.")
                return False
            cursor=conn.cursor()
            update_query="update asset_allocations set return_date=%s where asset_id=%s and employee_id=%s " \
            "and return_date is null"
            cursor.execute(update_query,(return_date,asset_id,employee_id))
            conn.commit()
            if cursor.rowcount>0:
                print("Asset deallocated successfully.")
                return True
            else:
                print("No active allocation found for given asset and employee.")
                return False
        except mysql.connector.Error as e:
            print(f"Database error during deallocateAsset: {e}")
            return False
        finally:
            if conn:
                conn.close()

    def performMaintenance(self,asset_id,maintenance_date,description,cost):
        try:
            conn=DBConnUtil.getConnection()
            if conn is None:
                print("Connection failed.")
                return False
            cursor=conn.cursor()
            #check if asset exists
            cursor.execute("select * from assets where asset_id=%s",(asset_id,))
            if cursor.fetchone() is None:
                raise AssetNotFoundException(f"Asset with ID {asset_id} not found.")
             # Check if asset has been maintained in the last 2 years
            cursor.execute("select max(maintenance_date) from maintenance_records where asset_id=%s",(asset_id,))
            row=cursor.fetchone()
            if row[0] is not None:
                last_maintenance=row[0]
                if (datetime.now().date()-last_maintenance).days>730:
                    raise AssetNotMaintainException(f"Asset {asset_id} has not been maintained in the last 2 years.")
                # Insert maintenance record
            insert_query="insert into maintenance_records (asset_id,maintenance_date,description,cost) " \
            "values (%s,%s,%s,%s)"
            cursor.execute(insert_query,(asset_id,maintenance_date,description,cost))
            conn.commit()
            print("Maintenance record added successfully.")
            return True
        except AssetNotFoundException as e:
            print("error",e)
            return False
        except AssetNotMaintainException as e:
            print("error",e)
            return False
        except mysql.connector.Error as e:
            print(f"Database error during performMaintenance: {e}")
            return False
        finally:
            if conn:
                conn.close()

    def reserveAsset(self,asset_id,employee_id,reservation_date,start_date,end_date):
        try:
            conn=DBConnUtil.getConnection()
            if conn is None:
                print("Connection failed.")
                return False
            cursor=conn.cursor()
            insert_query="insert into reservations (asset_id,employee_id,reservation_date,start_date,end_date,status) " \
            "values (%s,%s,%s,%s,%s,'pending')"
            cursor.execute(insert_query,(asset_id,employee_id,reservation_date,start_date,end_date))
            conn.commit()
            print("Reservation added successfully.")
            return True
        except mysql.connector.Error as e:
            print(f"Database error during reserveAsset: {e}")
            return False
        finally:
            if conn:
                conn.close()

    def withdrawReservation(self,reservation_id):
        try:
            conn=DBConnUtil.getConnection()
            if conn is None:
                print("Connection failed.")
                return False
            cursor=conn.cursor()
            update_query="update reservations set status='canceled' where reservation_id=%s and status!='canceled'"
            cursor.execute(update_query,(reservation_id,))
            conn.commit()
            if cursor.rowcount>0:
                print("Reservation withdrawn successfully.")
                return True
            else:
                print("Reservation not found or already canceled.")
                return False
        except mysql.connector.Error as e:
            print(f"Database error during withdrawReservation: {e}")
            return False
        finally:
            if conn:
                conn.close()
    
