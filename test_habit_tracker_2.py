import pytest
from datetime import datetime
from habit_tracker_2 import PersistenceLayer, Habit, HabitManager, AnalyticModule

# Fixture for a temporary database
@pytest.fixture
def temp_db():
    """Fixture to create a temporary database for testing."""
    db_name = ":memory:"  # Use an in-memory database for testing
    persistence = PersistenceLayer(db_name)
    # Ensure the database is clean
    persistence.connection.execute("DROP TABLE IF EXISTS habits;")
    persistence.connection.execute("DROP TABLE IF EXISTS completions;")
    persistence.create_tables()
    yield persistence
    persistence.connection.close()

# Fixture for a habit manager
@pytest.fixture
def habit_manager(temp_db):
    """Fixture to create a HabitManager instance with a temporary database."""
    return HabitManager(persistence=temp_db) # Inject the temp_db

# Fixture for a habit
@pytest.fixture
def sample_habit():
    """Fixture to create a sample habit."""
    return Habit("Test Habit", "daily")

# Fixture for a list of habits
@pytest.fixture
def sample_habits():
    """Fixture to create a list of sample habits."""
    return [
        Habit("Habit 1", "daily"),
        Habit("Habit 2", "weekly"),
        Habit("Habit 3", "monthly"),
    ]

# Test PersistenceLayer
def test_persistence_layer(temp_db):
    """Test the PersistenceLayer class."""
    # Test table creation
    temp_db.create_tables()
    cursor = temp_db.connection.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    assert ("habits",) in tables
    assert ("completions",) in tables

    # Test adding a habit
    temp_db.add_habit("Test Habit", "daily")
    cursor.execute("SELECT name FROM habits WHERE name = 'Test Habit';")
    result = cursor.fetchone()
    assert result is not None  # The habit should exist
    assert result[0] == "Test Habit"  # Verify the name

    # Test marking a completion
    habit_id = cursor.execute("SELECT id FROM habits WHERE name = 'Test Habit';").fetchone()[0]
    temp_db.mark_completion(habit_id, datetime.now())
    completions = temp_db.get_completions(habit_id)
    assert len(completions) == 1

# Test Habit class
def test_habit_class(sample_habit):
    """Test the Habit class."""
    assert sample_habit.name == "Test Habit"
    assert sample_habit.periodicity == "daily"
    assert len(sample_habit.completion_dates) == 0

    # Test completing a task
    sample_habit.complete_task(datetime.now())
    assert len(sample_habit.completion_dates) == 1

    # Test streaks
    assert sample_habit.current_streak() == 1
    assert sample_habit.longest_streak() == 1

# Test HabitManager class
def test_habit_manager(habit_manager):
    """Test the HabitManager class."""
    # Test predefined habits
    habits = habit_manager.persistence.get_habits()
    assert len(habits) == 5  # 5 predefined habits

    # Test creating a new habit
    habit_manager.create_habit("New Habit", "daily")
    habits = habit_manager.persistence.get_habits()
    assert len(habits) == 6  # 5 predefined + 1 new habit

    # Test marking a habit as completed
    habit_manager.mark_habit_completed("New Habit")
    habit_id = habit_manager.get_habit_id("New Habit")
    completions = habit_manager.persistence.get_completions(habit_id)
    assert len(completions) == 1

# Test AnalyticModule class
def test_analytic_module(sample_habits):
    """Test the AnalyticModule class."""
    analytics = AnalyticModule(sample_habits)

    # Test retrieving all habits
    assert len(analytics.retrieve_all_habits()) == 3

    # Test filtering habits by periodicity
    daily_habits = analytics.filter_habits_by_periodicity("daily")
    assert len(daily_habits) == 1
    assert daily_habits[0].name == "Habit 1"

    # Test calculating streaks
    completion_dates = [datetime(2023, 1, 1), datetime(2023, 1, 2), datetime(2023, 1, 4)]
    assert analytics.calculate_longest_streak(completion_dates) == 2

    # Test longest streak for a specific habit
    sample_habits[0].completion_dates = completion_dates
    assert analytics.determine_longest_streak_for_specific_habit("Habit 1") == 2

    # Test longest streak across all habits
    sample_habits[1].completion_dates = [datetime(2023, 1, 7), datetime(2023, 1, 8)]
    assert analytics.calculate_longest_streak_across_all_habits() == 2