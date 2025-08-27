# tarot_scores.py
# Оценки карт для определения «тона» расклада

CARD_SCORES = {
    "Шут": {"upright": +1, "reversed": -1},
    "Маг": {"upright": +1, "reversed": -1},
    "Жрица": {"upright": 0, "reversed": -1},
    "Императрица": {"upright": +1, "reversed": -1},
    "Император": {"upright": +1, "reversed": -1},
    "Иерофант": {"upright": 0, "reversed": -1},
    "Влюблённые": {"upright": +1, "reversed": -1},
    "Колесница": {"upright": +1, "reversed": -1},
    "Сила": {"upright": +1, "reversed": -1},
    "Отшельник": {"upright": 0, "reversed": -1},
    "Колесо Фортуны": {"upright": +1, "reversed": -1},
    "Справедливость": {"upright": 0, "reversed": -1},
    "Повешенный": {"upright": 0, "reversed": -1},
    "Смерть": {"upright": 0, "reversed": -1},
    "Умеренность": {"upright": +1, "reversed": -1},
    "Дьявол": {"upright": -1, "reversed": 0},
    "Башня": {"upright": -1, "reversed": -1},
    "Звезда": {"upright": +1, "reversed": 0},
    "Луна": {"upright": 0, "reversed": -1},
    "Солнце": {"upright": +1, "reversed": 0},
    "Суд": {"upright": +1, "reversed": 0},
    "Мир": {"upright": +1, "reversed": 0}
}