"""
Seed database with realistic example pets, community users, and adoption records.
Uses standard library sqlite3 for 100% portable execution across Windows/Linux/Docker.
Author: Sagar / DevOps Team
"""
import os
import sqlite3
import hashlib
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "pets.db")


def hash_pwd(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


SAMPLE_USERS = [
    (1, "rohit.sharma@example.com", "rohit_s", hash_pwd("Pass@1234"), "Rohit Sharma", 0, "2026-01-15 10:30:00"),
    (2, "priya.patil@example.com", "priya_p", hash_pwd("Pass@1234"), "Priya Patil", 0, "2026-02-20 14:15:00"),
    (3, "ananya.deshmukh@example.com", "ananya_d", hash_pwd("Pass@1234"), "Ananya Deshmukh", 0, "2026-03-05 09:45:00"),
    (4, "sagar.admin@example.com", "sagar_admin", hash_pwd("Admin@1234"), "Sagar Patade", 1, "2026-01-01 00:00:00"),
]

SAMPLE_PETS = [
    (
        "PET-001",
        "Bella",
        "Dog",
        "Golden Retriever",
        2,
        "Bella is a cheerful, affectionate golden girl who loves morning jogs, playing fetch at the park, and gentle belly rubs. She is completely house-trained, vaccinated, and gets along wonderfully with kids and other pets.",
        "available",
        "Female",
        "Medium",
        "Young",
    ),
    (
        "PET-002",
        "Milo",
        "Cat",
        "Ginger Tabby",
        1,
        "Milo is an inquisitive little sweetheart who loves napping in sunbeams and chasing feather toys. Litter-box trained, neutered, and very affectionate once he gets to know you.",
        "available",
        "Male",
        "Small",
        "Young",
    ),
    (
        "PET-003",
        "Rocky",
        "Dog",
        "German Shepherd",
        3,
        "Rocky is an alert, intelligent, and fiercely loyal boy. He has completed basic obedience training, walks calmly on a leash, and loves outdoor adventures. Best suited for an active family.",
        "available",
        "Male",
        "Large",
        "Adult",
    ),
    (
        "PET-004",
        "Luna",
        "Cat",
        "Siamese",
        2,
        "Luna has striking blue eyes and a calm, dignified personality. She loves perching by windows and curling up on your lap during quiet evenings. Fully vaccinated and dewormed.",
        "available",
        "Female",
        "Small",
        "Young",
    ),
    (
        "PET-005",
        "Charlie",
        "Dog",
        "Beagle",
        4,
        "Charlie is a goofy, treat-loving beagle with soulful brown eyes. He loves sniffing every corner of the yard, making friends with neighbors, and snuggling under cozy blankets.",
        "available",
        "Male",
        "Medium",
        "Adult",
    ),
    (
        "PET-006",
        "Daisy",
        "Dog",
        "Indie / Desi Dog",
        1,
        "Daisy was rescued as an abandoned pup in Pune and nurtured back to full health. She is super smart, resilient, extremely friendly, and has boundless love to give to a caring family.",
        "available",
        "Female",
        "Medium",
        "Young",
    ),
    (
        "PET-007",
        "Simba",
        "Cat",
        "Persian",
        3,
        "Simba is a regal, fluffy indoor prince. Very gentle, quiet, and enjoys brushing sessions. He has already found his forever family and was happily adopted!",
        "adopted",
        "Male",
        "Medium",
        "Adult",
    ),
    (
        "PET-008",
        "Bruno",
        "Dog",
        "Labrador Retriever",
        5,
        "Bruno is a friendly giant who was successfully adopted by a lovely family in Mumbai. He enjoys swimming, fetching tennis balls, and playing with his new human siblings.",
        "adopted",
        "Male",
        "Large",
        "Adult",
    ),
]

SAMPLE_REQUESTS = [
    (
        "REQ-001",
        "PET-007",
        "Aarav Mehta",
        "aarav.mehta@example.com",
        "We have a peaceful apartment and plenty of time to care for Simba's grooming. We fell in love with him instantly!",
        "approved",
        1,
    ),
    (
        "REQ-002",
        "PET-008",
        "Vikram Singhania",
        "vikram.s@example.com",
        "We have a large home with a fenced lawn. Our previous lab lived with us for 12 years. We'd love to give Bruno a wonderful home.",
        "approved",
        2,
    ),
    (
        "REQ-003",
        "PET-001",
        "Sunita Deshmukh",
        "sunita.d@example.com",
        "Our family loves dogs and we work remotely. We would love to arrange a meet and greet with Bella this weekend!",
        "pending",
        3,
    ),
]


def seed_database():
    """Populate database tables with realistic user and pet data."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # 1. Users
    cur.executemany(
        """
        INSERT OR IGNORE INTO users (id, email, username, hashed_password, full_name, is_admin, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        SAMPLE_USERS,
    )

    # 2. Pets
    cur.executemany(
        """
        INSERT OR REPLACE INTO pets (pet_id, name, species, breed, age, description, status, gender, size, age_category)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        SAMPLE_PETS,
    )

    # 3. Adoption Requests
    cur.executemany(
        """
        INSERT OR REPLACE INTO adoption_requests (request_id, pet_id, adopter_name, adopter_email, message, status, user_id)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        SAMPLE_REQUESTS,
    )

    conn.commit()

    cur.execute("SELECT COUNT(*) FROM pets")
    pets_count = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM users")
    users_count = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM adoption_requests")
    req_count = cur.fetchone()[0]

    conn.close()
    print(f"Database successfully seeded! Pets: {pets_count}, Users: {users_count}, Adoption Requests: {req_count}")


if __name__ == "__main__":
    seed_database()
