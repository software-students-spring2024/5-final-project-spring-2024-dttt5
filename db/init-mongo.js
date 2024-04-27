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

db.users.updateMany(
    {},
    {
        $set: {
            "current_weight": null,
            "target_weight": null,
            "total_calorie_deficit_needed": 0
        }
    }
);

db.createCollection("users");
db.createCollection("calories");
