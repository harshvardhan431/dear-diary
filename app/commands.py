from app.extension import db
from app.models import State, City, Badge


def register_commands(app):

    @app.cli.command("seed")  # creates terminal command named seed
    def seed_data():
        """Insert default states and cities."""

        # this function runs when `flask seed` is executed in terminal
        # prevent duplicate seeding of states and cities
        if State.query.first():
            print("Data already seeded.")
            return

        # dictionary containing states and their cities
        # key = state name
        # value = list of cities belonging to that state
        data = {
            "Madhya Pradesh": ["Indore","Bhopal","Jabalpur","Gwalior","Ujjain","Sagar"],
            "Telangana": ["Hyderabad","Warangal","Nizamabad","Karimnagar","Khammam"],
            "Maharashtra": ["Mumbai","Pune","Nagpur","Thane","Nashik"],
            "Andhra Pradesh": ["Visakhapatnam","Vijayawada","Guntur","Nellore","Kurnool"]
        }

        # loop through each state and its list of cities
        for state_name, cities in data.items(): #the loop doesn't know anything it simply know dictionary has a key and value

            # create state object
            state = State(sname=state_name)

            # add state to session
            db.session.add(state)

            # flush generates the state.id before commit
            # so we can use it as foreign key in City table
            db.session.flush()

            # insert all cities belonging to this state
            db.session.add_all(
                [City(cname=city, state_id=state.id) for city in cities] #here for each city object we see that the state id becomes a foreign key object 
            )

        # prevent duplicate badge creation
        if not Badge.query.first():

            badges = [
                Badge(bname="Keep Going", description="You have written less than 10 diaries"),
                Badge(bname="Fantastic", description="You have written diaries between 10 and 50"),
                Badge(bname="Star", description="You have written diaries between 50 and 100"),
                Badge(bname="Champion", description="You have written more than 100 diaries")
            ]

            # insert all badges
            db.session.add_all(badges)

     # commit all database changes
        db.session.commit()
        print("✅ Seeding complete.")