# Habit_tracker_app_Backend
Portfolio Creating a backend Habit Tracker Application with Python
This is a Python-based habit tracker application that allows users to create, track, and analyze their habits. The application is built using SQLite for data persistence and includes a command-line interface (CLI) for interaction.
Features

    Create Habits: Users can create new habits with a name and periodicity (daily, weekly, or monthly).

    Mark Completions: Users can mark habits as completed on specific dates.

    List Habits: Users can view a list of all their habits.

    Analytics: Users can view analytics for their habits, including current streaks and longest streaks.

    Predefined Habits: The application comes with a set of predefined habits that are automatically added to the database if they don't already exist.
   Installation
   Clone the repository (bash):
   git clone https://github.com/Taboh250/Habit_tracker_app_Backend.git
   cd habit-tracker
   Install dependencies (bash):
   Ensure you have Python 3.7 or later version installed. The application uses the click library for the CLI, which can be installed via pip:
   pip install click
   Run the application (bash):
   python habit_tracker_2.py

   Usage
   The application provides a CLI with the following commands:
   
   Create a new habit (bash):
   python habit_tracker_2.py create <name> <periodicity>
   Example (bash):
   python habit_tracker_2.py create "Drink Water" daily
   
   Mark a habit as completed (bash):
   python habit_tracker_2.py complete <name>
   Example (bash):
   python habit_tracker_2.py complete "Drink Water"
   
   List all habits (bash):
   python habit_tracker_2.py list

   View analytics (bash):
   python habit_tracker_2.py analytics

   Code Structure
   The code is organized into several classes:
   PersistenceLayer: Handles database operations, including creating tables, adding habits, and marking completions.

  Habit: Represents a habit with properties like name, periodicity, and completion dates.

  HabitManager: Manages habits, including loading them from the database, creating new habits, and marking completions.

  AnalyticModule: Provides analytics for habits, such as calculating streaks and filtering habits by periodicity.

  CLI Implementation: Uses the click library to provide a command-line interface for interacting with the habit tracker.


  Contributing
  Contributions are welcome! Please fork the repository and submit a pull request with your changes.
   
Acknowledgments

    Thanks to the click library for making CLI creation easy.
    
    The video galery of DLBDSOOFPP01 on mycampus

    Inspired by various habit-tracking applications and methodologies.

    Enjoy tracking your habits and building better routines!
    


   




   
   
   
   
