from sqlmodel import Session, SQLModel, select

from app.database import engine
from app.models import Hero, Mission, Team


def seed():
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        if session.exec(select(Team)).first() is not None:
            print("Already seeded")
            return

        avengers = Team(name="Avengers", headquarters="New York")
        xmen = Team(name="X-Men", headquarters="Westchester")
        sokovia = Mission(title="Battle of Sokovia")
        sentinel = Mission(title="Stop the Sentinels")

        # Twenty heroes for Part 10; assign relationships instead of IDs.
        avengers_data = [
            ("Tony", 45, "Iron Man"),
            ("Natasha", 35, "Black Widow"),
            ("Steve", 100, "Captain America"),
            ("Thor", 1500, "God of Thunder"),
            ("Bruce", 49, "Hulk"),
            ("Clint", 47, "Hawkeye"),
            ("Wanda", 29, "Scarlet Witch"),
            ("Vision", 3, "Vision"),
            ("Sam", 40, "Falcon"),
            ("Scott", 41, "Ant-Man"),
        ]
        xmen_data = [
            ("Logan", 150, "Wolverine"),
            ("Charles", 80, "Professor X"),
            ("Ororo", 35, "Storm"),
            ("Jean", 30, "Phoenix"),
            ("Scott Summers", 32, "Cyclops"),
            ("Hank", 45, "Beast"),
            ("Raven", 90, "Mystique"),
            ("Kurt", 28, "Nightcrawler"),
            ("Anna", 25, "Rogue"),
        ]
        heroes = [
            Hero(name=name, age=age, secret_name=alias,
                 team=avengers, missions=[sokovia])
            for name, age, alias in avengers_data
        ]
        heroes += [
            Hero(name=name, age=age, secret_name=alias,
                 team=xmen, missions=[sentinel])
            for name, age, alias in xmen_data
        ]
        heroes.append(Hero(name="Peter", age=16, secret_name="Spider-Man"))
        session.add_all([avengers, xmen, sokovia, sentinel, *heroes])
        session.commit()
        print("Seeded 2 teams, 20 heroes and 2 missions")


if __name__ == "__main__":
    seed()
