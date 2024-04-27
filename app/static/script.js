document.getElementById('calorie-form').addEventListener('submit', function(e) {
    e.preventDefault();
    const food = document.getElementById('food').value;
    const calories = parseInt(document.getElementById('calories').value);
    const date = document.getElementById('date').value;
    const data = { food, calories, date };

    fetch('/calories', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        showPopup("Calorie added successfully!");
        updateCaloriesTable();
    })
    .catch(error => {
        console.error('Error:', error);
        document.getElementById('message').innerText = 'Failed to add calories!';
    });
});

function showPopup(message) {
    const popup = document.getElementById('popup');
    popup.textContent = message;
    popup.style.display = 'block';
    setTimeout(() => popup.style.display = 'none', 3000);  // Hide popup after 3 seconds
}

function updateCaloriesTable() {
    fetch('/calories')
    .then(response => response.json())
    .then(data => {
        const tbody = document.getElementById('calories-table').getElementsByTagName('tbody')[0];
        tbody.innerHTML = '';  // Clear existing entries
        data.forEach(entry => {
            let row = tbody.insertRow();
            let dateCell = row.insertCell(0);
            dateCell.textContent = entry.date;
            let foodCell = row.insertCell(1);
            foodCell.textContent = entry.food;
            let caloriesCell = row.insertCell(2);
            caloriesCell.textContent = entry.calories;
        });
        updateTotalCalories();
    })
    .catch(error => console.error('Error:', error));
}

function updateTotalCalories() {
    fetch('/calories')
    .then(response => response.json())
    .then(data => {
        const totalCalories = data.reduce((total, entry) => total + entry.calories, 0);
        document.getElementById('total-calories').textContent = `Total Calories: ${totalCalories}`;
    })
    .catch(error => console.error('Error:', error));
}
