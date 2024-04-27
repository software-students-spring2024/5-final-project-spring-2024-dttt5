db.createUser({
    user: "yourUsername",
    pwd: "yourPassword",
    roles: [
        {
            role: "readWrite",
            db: "calorieDB"  // Match this case with your application
        }
    ]
});

db.createCollection("users");
db.createCollection("calories");

  