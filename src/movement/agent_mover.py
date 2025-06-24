class MovementAgent:
    def __init__(self, session, current_location="Theed", destination="Mos Eisley"):
        self.session = session
        self.current_location = current_location
        self.destination = destination

    def move_to(self):
        # Simulate a movement sequence
        action = f"Moving from {self.current_location} to {self.destination}"
        print(action)
        self.session.add_action(action)
        self.current_location = self.destination  # For now, assume instant move
