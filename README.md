# Final Project

An exercise to put to practice software development teamwork, subsystem communication, containers, deployment, and CI/CD pipelines. See [instructions](./instructions.md) for details.

## Team members

Deniz Qian: https://github.com/dq2024 \
Somyung Kim: https://github.com/troy-skim \
Terrance Chen: https://github.com/tchen0125 \
Kim Young: https://github.com/Kyoung655

## Project Description
This project is a calorie tracker app that helps users manage their weight loss by allowing them to log meals, workouts, and track their weight goals. Users can see the calorie deficit needed to reach their desired weight through a simple, user-friendly interface.

## Project Layout
This project consists of two parts. Each part operates
in its own docker container.

### App
The web app uses flask, HTML, and some javascript to allow visitors make use of the app. 

### Db
Mongodb is used to store user data. Users can log in and out when/wherever they want.

## Project Instructions

### System Requirements
- Python 3.9 or higher

### Install Dependencies
Ensure Flask, etc are installed. They should be automatically installed. \
If not:
```
pip install Flask
```

### Run the Application
```
docker-compose up --build
```
It should be running at http://127.0.0.1:8080.


### Shutdown the Application
docker-compose down    