from pymongo import MongoClient

class ConnectionDB():
    def __init__(self):
        pass

    @staticmethod
    def create_connection(mongodb_uri, database_name):
        try:
            client=MongoClient(host=mongodb_uri, connectTimeoutMS=2000, serverSelectionTimeoutMS=3000)
            # Si existe conexion debe poder ejecutarse la siguiente linea 
            client[database_name].list_collection_names()
            return client,"Conexion establecida exitosamente."
        except Exception as e:
            return None,"Exception: {}".format(e)
        
    @staticmethod
    def create_local_connection_db(username, password, database_name, replica_set_name):
        # Usar cuando se trabaje con el entorno virtual en local
        # URI para crear conexion local para aplicacion local
        mongodb_uri="mongodb://{}:{}@localhost:30001/replicaSet={}?authSource=admin&replicaSet={}&readPreference=primary&directConnection=true&ssl=false".format(username, password, replica_set_name, replica_set_name) 
        
        # Usar al momento de construir la imagen Docker
        # URI para crear conexion local para aplicacion Docker
        # mongodb_uri="mongodb://{}:{}@mongodb1:27017/replicaSet={}?authSource=admin&replicaSet={}&readPreference=primary&directConnection=true&ssl=false".format(username, password, replica_set_name, replica_set_name) 
        
        return ConnectionDB.create_connection(mongodb_uri=mongodb_uri, database_name=database_name)

    @staticmethod
    def create_cloud_connection_db(username, password, database_name, uri_cloud_cluster):
        # URI para crear conexion en la nube
        mongodb_uri="mongodb+srv://{}:{}@{}/{}?retryWrites=true&w=majority".format(username, password, uri_cloud_cluster, database_name)
        return ConnectionDB.create_connection(mongodb_uri=mongodb_uri, database_name=database_name)

