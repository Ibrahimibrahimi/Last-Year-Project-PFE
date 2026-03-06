import os
import sqlite3

dbName = "./db/education_platform.db"
conn = sqlite3.connect(dbName)
cursor = conn.cursor()

def createTables():
    global cursor
    # Enable foreign keys
    cursor.execute("PRAGMA foreign_keys = ON;")

    # =======================
    # Level Table
    # =======================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Level (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        points INTEGER NOT NULL
    );
    """)

    # =======================
    # Utilisateur Table
    # =======================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Utilisateur (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nom TEXT NOT NULL,
        numero TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        birth_date DATE NOT NULL,
        level INTEGER DEFAULT 1,
        profile TEXT ,
        total_points INTEGER DEFAULT 0,
        solved_exes INTEGER DEFAULT 0,
        join_date DATE DEFAULT CURRENT_DATE,
        FOREIGN KEY (level) REFERENCES Level(id)
    );
    """)

    # =======================
    # Professeur Table
    # =======================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Professeur (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nom TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        profile TEXT
    );
    """)

    # =======================
    # Cours Table
    # =======================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Cours (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        nbr_parties INTEGER NOT NULL
    );
    """)

    # =======================
    # PartieCours Table
    # =======================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS PartieCours (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        id_cour INTEGER NOT NULL,
        title_partie TEXT NOT NULL,
        content_partie TEXT NOT NULL,
        example_partie TEXT,
        FOREIGN KEY (id_cour) REFERENCES Cours(id) ON DELETE CASCADE
    );
    """)

    # =======================
    # Exercices Table
    # =======================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Exercices (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        id_cour INTEGER NOT NULL,
        id_partie INTEGER NOT NULL,
        level INTEGER NOT NULL,
        points INTEGER NOT NULL,
        answer TEXT NOT NULL,
        FOREIGN KEY (id_cour) REFERENCES Cours(id) ON DELETE CASCADE,
        FOREIGN KEY (id_partie) REFERENCES PartieCours(id) ON DELETE CASCADE,
        FOREIGN KEY (level) REFERENCES Level(id)
    );
    """)

    # =======================
    # QCM Table
    # =======================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Qcm (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        id_course INTEGER NOT NULL,
        choiceA TEXT NOT NULL,
        choiceB TEXT NOT NULL,
        choiceC TEXT NOT NULL,
        right_choice TEXT NOT NULL,
        FOREIGN KEY (id_course) REFERENCES Cours(id) ON DELETE CASCADE
    );
    """)

    # =======================
    # SolvedQCM Table
    # =======================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS SolvedQCM (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        id_qcm INTEGER NOT NULL,
        FOREIGN KEY (id_qcm) REFERENCES Qcm(id) ON DELETE CASCADE
    );
    """)
    print("DB CREATED")
    # Commit & close
    conn.commit()

# create db if not exists
if not os.path.exists(dbName):
    createTables()