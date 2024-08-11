from __future__ import annotations

import numpy as np
import customtkinter  as ctk
import tkinter as tk
from pymongo import timeout
from bson import ObjectId
from decouple import Config, RepositoryEnv

DOTENV_FILE = './.env'
env_config = Config(RepositoryEnv(DOTENV_FILE))

from components.create_frame import CreateFrame
from components.create_scrollable_frame import CreateScrollableFrame
from components.grid_frame import GridFrame
from db.connection_db import ConnectionDB
from db.models.user import User

class FrameApplication(CreateScrollableFrame):
    def __init__(self, master, name, **kwargs):
        CreateScrollableFrame.__init__(self, master=master, name=name, grid_frame=GridFrame(dim=(8,1), arr=None), **kwargs)
        self.init_connection_variables()

        label_username=ctk.CTkLabel(master=self, text="Username")
        self.var_username=ctk.StringVar(value="")
        entry_username=ctk.CTkEntry(master=self, width=200, textvariable=self.var_username)
        label_password=ctk.CTkLabel(master=self, text="Password")
        self.var_password=ctk.StringVar(value="")
        entry_password=ctk.CTkEntry(master=self, width=200, show="*", textvariable=self.var_password)
        button_connect=ctk.CTkButton(master=self, text="Connect", command=self.connect)
        button_disconnect=ctk.CTkButton(master=self, text="Disconnect", command=self.disconnect)
        button_make_operations=ctk.CTkButton(master=self, text="Make operations", command=self.make_operations)
        self.var_db=ctk.StringVar(value="")
        label_db=ctk.CTkLabel(master=self, textvariable=self.var_db)
        
        self.insert_element(cad_pos="0,0", element=label_username, padx=5, pady=5, sticky="")
        self.insert_element(cad_pos="1,0", element=entry_username, padx=5, pady=5, sticky="")
        self.insert_element(cad_pos="2,0", element=label_password, padx=5, pady=5, sticky="")
        self.insert_element(cad_pos="3,0", element=entry_password, padx=5, pady=5, sticky="")
        self.insert_element(cad_pos="4,0", element=button_connect, padx=5, pady=5, sticky="")
        self.insert_element(cad_pos="5,0", element=button_disconnect, padx=5, pady=5, sticky="")
        self.insert_element(cad_pos="6,0", element=button_make_operations, padx=5, pady=5, sticky="")
        self.insert_element(cad_pos="7,0", element=label_db, padx=5, pady=5, sticky="")

    def destroy(self):
        self.disconnect()
        CreateScrollableFrame.destroy(self)

    def init_connection_variables(self):
        self.client=None 
        self.mongodb=None
        self.dict_collections={}

    def get_collections(self):
        self.dict_collections={}
        for collection_name in self.mongodb.list_collection_names():
            collection=self.mongodb[collection_name]
            result=collection.find({},{})
            self.dict_collections[collection_name]=list(map(lambda elem: User.from_json(obj=elem), result))

    def connect(self):
        try:
            if self.client is None:
                username=self.var_username.get()
                password=self.var_password.get()
                database_name=env_config.get("MONGO_INITDB_DATABASE")
                replica_set_name=env_config.get("MONGO_REPLICA_SET_NAME")
                # print("username: {}\npassword: {}\ndatabase_name: {}\nreplica_set_name: {}\n".format(username, password, database_name, replica_set_name))
                if tk.messagebox.askyesnocancel(title="Conectar", message="¿Esta seguro de conectar con la base de datos?", parent=self):
                    self.client,connection_message=ConnectionDB.create_local_connection_db(username=username, password=password, database_name=database_name, replica_set_name=replica_set_name)
                    if self.client is not None:
                        # Para tener referencia a la base de datos
                        self.mongodb=self.client[database_name]
                        self.get_collections()
                        self.show_users()
                    else:
                        tk.messagebox.showinfo(title="Conectar", message=connection_message, parent=self)
            else:
                tk.messagebox.showinfo(title="Conectar", message="Ya hay una conexion.", parent=self)
        except Exception as e:
                self.init_connection_variables()
                tk.messagebox.showinfo(title="Conectar", message="Exception: {}".format(e), parent=self)

    def disconnect(self):
        try:
            if self.client is not None:
                self.client.close() 
        except Exception as e:
            pass 
        finally:
            self.init_connection_variables()
            self.var_db.set(value="")

    def show_users(self):
        text="USERS\n\n"
        for user in self.dict_collections["User"]:
            text+="{}\n".format(user.name)
        self.var_db.set(value=text)

    def make_operations(self):
        session=None
        try:
            if self.client is not None:
                with timeout(5000):
                    session=self.client.start_session(causal_consistency=True)
                    session.start_transaction()

                    # Coleccion de usuario
                    mongodb_collection=self.mongodb["User"]
                    # Insertar usuario
                    new_user=User.from_json(obj={
                        "_id": ObjectId(),
                        "name": "User{}".format(np.random.randint(1,100)),
                    })
                    mongodb_collection.insert_many([new_user.to_json()], session=session)
                    # Eliminar usuario
                    user0=self.dict_collections["User"][0]
                    mongodb_collection.delete_many({"_id": {"$in": [user0._id]}}, session=session)
                    # Actualizar usuario
                    user1=self.dict_collections["User"][1]
                    mongodb_collection.update_one({"_id": [user1._id]}, {"$set": {
                        "name": "User{}".format(np.random.randint(1,100))
                    }}, session=session)   
 
                    session.commit_transaction()
                    self.get_collections()
                    self.show_users()
            else:
                tk.messagebox.showinfo(title="Hacer operaciones", message="No hay una conexion.", parent=self)
        except Exception as e:
            tk.messagebox.showinfo(title="Hacer operaciones", message="Exception: {}".format(e), parent=self) 
        finally:
            if session is not None:
                session.end_session()

class App(ctk.CTk):
    def __init__(self):
        ctk.CTk.__init__(self)

        # Configuramos nuestra aplicacion
        self.geometry("1366x768")
        self.title("Plantilla")

        # Configuramos el sistema de cuadricula
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Creamos un frame root
        self.frame_root=CreateFrame(master=self, name="FrameRoot", grid_frame=GridFrame(dim=(1,1), arr=None))
        
        # Colocamos el frame root en la cuadricula
        self.frame_root.grid(row=0, column=0, padx=5, pady=5, sticky="nsew") # Al agregar sticky='nsew' el frame pasa de widthxheight a abarcar todo el espacio disponible

        # Creamos el elemento principal 
        self.frame_application=FrameApplication(master=self.frame_root, name="FrameApplication", fg_color="lightcoral")

        # Insertamos el elemento principal
        self.frame_root.insert_element(cad_pos="0,0", element=self.frame_application, padx=5, pady=5, sticky="nsew")

        # Configuramos el cerrado de la ventana
        self.protocol("WM_DELETE_WINDOW", self.destroy)

    def destroy(self):
        ctk.CTk.quit(self)
        ctk.CTk.destroy(self)

if __name__ == "__main__":
    # Configuramos e iniciamos la aplicacion
    ctk.set_appearance_mode("Light")
    ctk.set_default_color_theme("green")
    app=App()
    app.mainloop()