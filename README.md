![app_ci](https://github.com/software-students-spring2024/5-final-project-spring-2024-dttt5/actions/workflows/app_ci.yml/badge.svg)
![ci](https://github.com/software-students-spring2024/5-final-project-spring-2024-dttt5/actions/workflows/ci.yml/badge.svg)
![event-logger](https://github.com/software-students-spring2024/5-final-project-spring-2024-dttt5/actions/workflows/event-logger.yml/badge.svg)
# Final Project

An exercise to put to practice software development teamwork, subsystem communication, containers, deployment, and CI/CD pipelines. See [instructions](./instructions.md) for details.

## Team members

Deniz Qian: https://github.com/dq2024  
Somyung Kim: https://github.com/troy-skim  
Terrance Chen: https://github.com/tchen0125  
Kim Young: https://github.com/Kyoung655

## Project Description
This project is a fitness journal app that helps users manage their weight loss by allowing them to log meals, workouts, and track their weight goals. Users can see the calorie deficit needed to reach their desired weight through a simple, user-friendly interface.

## Project Instructions

### System Requirements
- Python 3.9 or higher

### Install Dependencies
Dependencies should be automatically installed.  
If not:
```
pip install flask pymongo python-dotenv pytest pytest-flask
```

### Run the Application

#### 1. Initialize
Enter in your browser: http://104.236.9.46:8080/

#### 2. Login / Register
Click **Register Here** button to register. Enter username and password, and click login.

#### 3. Main Page
You can see your calorie status, logout, set your weight goals, add calorie and workout entries.

#### 4. Set Your Weight Goals (Optional)
You can set your weight goals to check total calorie deficit needed to reach the target weight. The value is calculated with your current and target weight.

#### 5. Add Calorie Entries
You can add your previous meals. Enter food, calorie, date, and click **Add Food** button. The entires will show in the calorie entries table where you can edit or delete the entries.

#### 6. Add Workout Entries
You can add your workouts. Enter workout name, calorie, date and click **Add Workout** button. The entries will show in the workout entries table where you can edit or delete the entries.

### Shutdown the Application
Enter in your terminal:
```
docker-compose down
```

## Link to Dockerhub Container Images
[Link to dockerhub](https://hub.docker.com/r/tchen0125/app)