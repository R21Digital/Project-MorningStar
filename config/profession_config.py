"""Default profession skill requirements and trainer locations."""

REQUIRED_SKILLS = {
    "artisan": ["Novice Artisan"],
    "marksman": ["Novice Marksman"],
}

TRAINER_BY_PROFESSION = {
    "artisan": {
        "planet": "tatooine",
        "city": "mos_eisley",
        "coords": [3432, -4795],
        "name": "Artisan Trainer",
    },
    "marksman": {
        "planet": "corellia",
        "city": "coronet",
        "coords": [-150, 60],
        "name": "Marksman Trainer",
    },
}
