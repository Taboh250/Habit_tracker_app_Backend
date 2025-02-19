# Import required modules and libraries
from datetime import datetime
import sqlite3
import click


# Persistence Layer Class
class PersistenceLayer:
    """Handles database operations for habit tracking."""

    def __init__(self, db_name='habit_tracker_2.db'):
        self.connection = sqlite3.connect(db_name)
        self.cursor = self.connection.cursor()
        self.create_tables()

    def create_tables(self):
        """Create tables for habits and completions if they don't exist."""
        with self.connection:
            self.connection.execute('''
                CREATE TABLE IF NOT EXISTS habits (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    periodicity TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            ''')
            self.connection.execute('''
                CREATE TABLE IF NOT EXISTS completions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    habit_id INTEGER NOT NULL,
                    completion_date TIMESTAMP NOT NULL,
                    FOREIGN KEY(habit_id) REFERENCES habits(id)
                );
            ''')

    def get_habit_completions(self, habit_id):
        """Retrieve completion dates for a given habit."""
        with self.connection:
            rows = self.connection.execute(
                "SELECT completion_date FROM completions WHERE habit_id = ?", (habit_id,)
            )
            return [datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S.%f") for row in rows]

    def add_habit(self, name, periodicity):
        """Add a new habit to the database."""
        with self.connection:
            self.connection.execute(
                "INSERT INTO habits (name, periodicity, created_at) VALUES (?, ?, ?)",
                (name, periodicity, datetime.now())
            )

    def mark_completion(self, habit_id, completion_date):
        """Mark a habit as completed on a specific date."""
        with self.connection:
            self.connection.execute(
                "INSERT INTO completions (habit_id, completion_date) VALUES (?, ?)",
                (habit_id, completion_date)
            )

    def get_habits(self):
        """Retrieve all habits from the database."""
        with self.connection:
            return self.connection.execute("SELECT * FROM habits").fetchall()

    def get_completions(self, habit_id):
        """Retrieve all completions for a specific habit."""
        with self.connection:
            return self.connection.execute(
                "SELECT * FROM completions WHERE habit_id = ?", (habit_id,)
            ).fetchall()

    def fetch_one(self, query, params=()):
        """Execute a query and return a single row."""
        with self.connection:
            self.cursor.execute(query, params)
            return self.cursor.fetchone()


# Habit Class
class Habit:
    """Represents a habit with its properties and methods."""

    def __init__(self, name, periodicity, completion_dates=None):
        self.name = name
        self.periodicity = periodicity
        self.created_at = datetime.now()
        self.completion_dates = completion_dates if completion_dates else []

    def complete_task(self, date_time):
        """Mark the habit as completed on a specific date."""
        self.completion_dates.append(date_time)

    def current_streak(self):
        """Calculate the current streak of completions."""
        return len(self.completion_dates)

    def longest_streak(self):
        """Calculate the longest streak of completions."""
        return len(self.completion_dates)


# Habit Manager Class
class HabitManager:
    def __init__(self, persistence=None): # Allow injecting a PersistenceLayer
        self.persistence = persistence or PersistenceLayer()  # Initialize the database connection
        self.initialize_predefined_habits()  # Add predefined habits if they don't exist
        self.habits = self.load_habits_from_db()  # Then load all habits from the database

    def initialize_predefined_habits(self):
        """Ensure predefined habits exist in the database."""
        predefined_habits = [
            ("Morning Exercise", "daily"),
            ("Read a Book", "daily"),
            ("Weekly Meditation", "weekly"),
            ("Call Family", "weekly"),
            ("Budget Review", "monthly")
        ]

        for name, periodicity in predefined_habits:
            self.persistence.connection.execute(
                "INSERT OR IGNORE INTO habits (name, periodicity, created_at) VALUES (?, ?, ?)",
                (name, periodicity, datetime.now())
            )
            self.persistence.connection.commit()

    def load_habits_from_db(self):
        """Load habits from the database and attach completion dates."""
        habits = []
        for habit_data in self.persistence.get_habits():
            habit_id, name, periodicity, created_at = habit_data
            completion_dates = self.persistence.get_habit_completions(habit_id)
            habits.append(Habit(name, periodicity, completion_dates))
        return habits

    def create_habit(self, name, periodicity):
        """Create a new habit and add it to the database."""
        if name in [habit.name for habit in self.habits]:
            return  # Avoid duplicates

        habit = Habit(name, periodicity)
        self.habits.append(habit)
        self.persistence.add_habit(name, periodicity)
        self.persistence.connection.commit()

    def mark_habit_completed(self, name):
        """Mark a habit as completed."""
        habit_id = self.get_habit_id(name)
        if habit_id is None:
            raise ValueError(f"Habit '{name}' does not exist.")

        completion_time = datetime.now()
        self.persistence.mark_completion(habit_id, completion_time)
        self.persistence.connection.commit()

    def get_habit_id(self, name):
        """Retrieve the ID of a habit by its name."""
        result = self.persistence.fetch_one("SELECT id FROM habits WHERE name = ?", (name,))
        return result[0] if result else None

    def list_habits(self):
        """List all habits."""
        if not self.habits:
            click.echo("No habits found.")
            return
        for habit in self.habits:
            click.echo(f"Habit: {habit.name}, Periodicity: {habit.periodicity}")

    def view_analytics(self):
        """Display analytics for all habits."""
        for habit in self.habits:
            click.echo(
                f"Habit: {habit.name}, Current Streak: {habit.current_streak()}, Longest Streak: {habit.longest_streak()}"
            )


# Analytic Module
class AnalyticModule:
    """Provides analytics for habits."""

    def __init__(self, habits):
        self.habits = habits

    def retrieve_all_habits(self):
        """Return a list of all habits."""
        return self.habits

    def filter_habits_by_periodicity(self, periodicity):
        """Filter habits by their periodicity."""
        return [habit for habit in self.habits if habit.periodicity == periodicity]

    def calculate_longest_streak(self, completion_dates):
        """Calculate the longest streak of consecutive completions."""
        if not completion_dates:
            return 0

        completion_dates = sorted(set(completion_dates))
        max_streak, current_streak = 0, 1

        for i in range(1, len(completion_dates)):
            if (completion_dates[i] - completion_dates[i - 1]).days == 1:
                current_streak += 1
            else:
                max_streak = max(max_streak, current_streak)
                current_streak = 1

        return max(max_streak, current_streak)

    def determine_longest_streak_for_specific_habit(self, habit_name):
        """Determine the longest streak for a specific habit."""
        habit = next((h for h in self.habits if h.name == habit_name), None)
        return self.calculate_longest_streak(habit.completion_dates) if habit else 0

    def calculate_longest_streak_across_all_habits(self):
        """Calculate the longest streak across all habits."""
        return max(
            (self.calculate_longest_streak(habit.completion_dates) for habit in self.habits),
            default=0,
        )


# CLI Implementation
habit_manager = HabitManager()


@click.group()
def cli():
    """Habit Tracker CLI."""
    pass


@click.command()
@click.argument('name')
@click.argument('periodicity', type=click.Choice(["daily", "weekly", "monthly"]))
def create(name, periodicity):
    """Create a new habit."""
    habit_manager.create_habit(name, periodicity)


@click.command()
@click.argument('name')
def complete(name):
    """Mark a habit as completed."""
    habit_manager.mark_habit_completed(name)


@click.command()
def list():
    """List all habits."""
    habit_manager.list_habits()


@click.command()
def analytics():
    """View analytics for habits."""
    habit_manager.view_analytics()


# Add commands to CLI
cli.add_command(create)
cli.add_command(complete)
cli.add_command(list)
cli.add_command(analytics)


if __name__ == '__main__':
    cli()

    # Example usage
    habits = [
        Habit("Daily Exercise", "daily", [datetime(2023, 1, 1), datetime(2023, 1, 2), datetime(2023, 1, 4)]),
        Habit("Weekly Reading", "weekly", [datetime(2023, 1, 7), datetime(2023, 1, 14), datetime(2023, 1, 21)])
    ]

    analytics = AnalyticModule(habits)
    print(analytics.retrieve_all_habits())
    print(analytics.filter_habits_by_periodicity("daily"))
    print(analytics.calculate_longest_streak_across_all_habits())
    print(analytics.determine_longest_streak_for_specific_habit("Daily Exercise"))