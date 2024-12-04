from components.database_mysql_component import DataBaseMySQLManager

dbMySQLManager = DataBaseMySQLManager()

asesor = dbMySQLManager.obtener_asesor_disponible("40")

print(asesor)