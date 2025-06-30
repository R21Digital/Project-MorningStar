import json
import os
from utils.travel import travel_to
from utils.skills import get_player_skills
from .trainer_travel import start_travel_to_trainer

class TrainManager:
    def __init__(
        self,
        build_path: str = 'config/builds/rifleman_medic.json',
        trainer_db: str = 'data/trainers_simple.json',
        *,
        auto_travel: bool = False,
    ) -> None:
        self.build_path = build_path
        self.trainer_db = trainer_db
        self.auto_travel = auto_travel
        self.trained_skills = set()
        self.load_build()

    def load_build(self):
        if os.path.exists(self.build_path):
            with open(self.build_path, 'r') as f:
                self.desired_skills = set(json.load(f).get('skills', []))
        else:
            self.desired_skills = set()

    def load_trainers(self):
        if os.path.exists(self.trainer_db):
            with open(self.trainer_db, 'r') as f:
                data = json.load(f)
            for entry in data:
                coords = entry.get('coords') or [entry.get('x'), entry.get('y')]
                if coords and len(coords) >= 2:
                    entry['coords'] = [float(coords[0]), float(coords[1])]
                entry.setdefault('planet', entry.get('zone', 'unknown'))
                entry.setdefault('city', entry.get('zone', 'unknown'))
                entry.setdefault('zone', entry.get('city', 'unknown'))
            return data
        return []

    def find_trainer_for_skill(self, skill, current_planet):
        trainers = self.load_trainers()
        local = [t for t in trainers if skill in t['skills'] and t['planet'] == current_planet]
        global_ = [t for t in trainers if skill in t['skills']]
        return local[0] if local else (global_[0] if global_ else None)

    def train_missing_skills(self, current_planet):
        current_skills = set(get_player_skills())
        missing = self.desired_skills - current_skills - self.trained_skills
        for skill in missing:
            trainer = self.find_trainer_for_skill(skill, current_planet)
            if trainer:
                if self.auto_travel:
                    start_travel_to_trainer(trainer)
                travel_to(trainer['planet'], trainer['city'], trainer['coords'])
                print(f"[TRAIN] Training {skill} at {trainer['name']} in {trainer['city']}")
                self.trained_skills.add(skill)
            else:
                print(f"[TRAIN] No trainer found for skill: {skill}")
