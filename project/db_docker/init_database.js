var mongo_initdb_username = _getEnv("MONGO_INITDB_USERNAME")
var mongo_initdb_passwrod = _getEnv("MONGO_INITDB_PASSWORD")
var mongo_initdb_database = _getEnv("MONGO_INITDB_DATABASE")

admin = db.getSiblingDB("admin");
admin.createUser({
        user: mongo_initdb_username,
        pwd: mongo_initdb_passwrod,
        roles: [{ role: "readWrite", db: mongo_initdb_database }],
});

initdb = db.getSiblingDB(mongo_initdb_database);

initdb.createCollection("User");    

var resUser = initdb.User.insertMany([
        {
                "name": "User1",
        },
        {
                "name": "User2",
        },
        {
                "name": "User3",
        }
]);
