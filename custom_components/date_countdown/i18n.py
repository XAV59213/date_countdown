"""Textes générés côté Python (notifications, catégories d'âge, noces, médailles…).

Ils suivent la langue de Home Assistant (``hass.config.language``) :
- français, anglais, allemand, espagnol, italien : tous les textes
  (notifications, types, médailles, catégories d'âge accordées au genre, noces, calendrier) ;
- autres langues : anglais.
"""

from __future__ import annotations

import re
from typing import Any

from .i18n_data import (
    AGE_CATEGORIES_DE,
    AGE_CATEGORIES_ES,
    AGE_CATEGORIES_IT,
    WEDDINGS_DE,
    WEDDINGS_ES,
    WEDDINGS_IT,
)

GENDER_UNSPECIFIED = "unspecified"
GENDER_MALE = "male"
GENDER_FEMALE = "female"
GENDERS = [GENDER_UNSPECIFIED, GENDER_MALE, GENDER_FEMALE]

SUPPORTED = ("fr", "en", "de", "es", "it")
FALLBACK = "en"

_VOWELS = "aeiouyàâäéèêëîïôöùûüÿæœhAEIOUYÀÂÄÉÈÊËÎÏÔÖÙÛÜŸÆŒH"
_VOWELS_NO_H = _VOWELS.replace("h", "").replace("H", "")


def resolve_language(language: str | None) -> str:
    """'fr', 'fr-FR', 'pt-BR'… → langue prise en charge (repli : anglais)."""
    lang = (language or "").strip().lower().replace("_", "-")
    if lang in SUPPORTED:
        return lang
    base = lang.split("-", 1)[0]
    return base if base in SUPPORTED else FALLBACK


def normalize_gender(value: Any) -> str:
    return value if value in GENDERS else GENDER_UNSPECIFIED


# ---------------------------------------------------------------------------
# Libellés
# ---------------------------------------------------------------------------

EVENT_TYPE_LABELS: dict[str, dict[str, str]] = {
    "fr": {"birthday": "Anniversaire", "anniversary": "Anniversaire de mariage", "memorial": "Mémorial",
           "promotion": "Promotion", "special_event": "Événement spécial", "retirement": "Retraite"},
    "en": {"birthday": "Birthday", "anniversary": "Wedding anniversary", "memorial": "Memorial",
           "promotion": "Promotion", "special_event": "Special event", "retirement": "Retirement"},
    "de": {"birthday": "Geburtstag", "anniversary": "Hochzeitstag", "memorial": "Gedenktag",
           "promotion": "Beförderung", "special_event": "Besonderes Ereignis", "retirement": "Ruhestand"},
    "es": {"birthday": "Cumpleaños", "anniversary": "Aniversario de boda", "memorial": "Memorial",
           "promotion": "Ascenso", "special_event": "Evento especial", "retirement": "Jubilación"},
    "it": {"birthday": "Compleanno", "anniversary": "Anniversario di matrimonio", "memorial": "Commemorazione",
           "promotion": "Promozione", "special_event": "Evento speciale", "retirement": "Pensione"},
}

MEDALS: dict[str, dict[str, str]] = {
    "fr": {"Argent": "Argent", "Vermeil": "Vermeil", "Or": "Or", "Grand Or": "Grand Or"},
    "en": {"Argent": "Silver", "Vermeil": "Vermeil", "Or": "Gold", "Grand Or": "Grand Gold"},
    "de": {"Argent": "Silber", "Vermeil": "Vermeil", "Or": "Gold", "Grand Or": "Großgold"},
    "es": {"Argent": "Plata", "Vermeil": "Vermeil", "Or": "Oro", "Grand Or": "Gran Oro"},
    "it": {"Argent": "Argento", "Vermeil": "Vermeil", "Or": "Oro", "Grand Or": "Grande Oro"},
}

NOTIFY_TITLES = {
    "fr": "Souvenirs et Célébrations",
    "en": "Memories and Celebrations",
    "de": "Erinnerungen und Feiern",
    "es": "Recuerdos y Celebraciones",
    "it": "Ricordi e Celebrazioni",
}

# Catégories d'âge en anglais (index = âge, 0 à 120), même ordre que const.AGE_CATEGORIES
AGE_CATEGORIES_EN = [
    "Mini Big Bang", "Rocket Baby", "Scribble Tornado", "Sandbox Pirate", "Cake Ninja",
    "King of the Slides", "Sticker Artist", "Training-Wheels Champion", "Lego Master", "Emperor of Treehouses",
    "Pokémon Card Ace", "TikToker Tween", "Emoji Rebel", "Meme Guru", "Selfie Ninja",
    "Hashtag Philosopher", "King of Snapchat Stories", "Reels Visionary", "Grown-Up", "Festival Wizard",
    "Happy-Hour Ninja", "Improv Night Master", "Group Chat Jedi", "Spotify Playlist Guru", "Brunch Ace",
    "Superhero of To-Do Lists", "Netflix Sunday Rockstar", "Wizard of Creative Excuses", "Karaoke Emperor", "TikTok Challenge Master",
    "Brunch Guru", "Zoom Meeting Ninja", "Spreadsheet Jedi", "Wine Night Ace", "Multitasking Superhero",
    "Birthday Rockstar", "BBQ Wizard", "Master of Dad-Joke Candy", "Quiz Night Emperor", "Kitchen Hacks Guru",
    "Ninja of Swamped Parents", "Planned Holidays Jedi", "Board Game Ace", "Superhero of Epic Excuses", "Parent-Teacher Meeting Rockstar",
    "Tight Budget Wizard", "Master of Funny Anecdotes", "Barbecue Emperor", "Nostalgia Night Guru", "DIY Project Ninja",
    "Dad-Joke Rockstar", "Power-Nap Jedi", "Ace of Youth Stories", "Superhero of the 80s", "Wizard of Grandma's Recipes",
    "Card Game Master", "Hiking Emperor", "Wise Advice Guru", "Knitting Night Ninja", "Documentary Jedi",
    "Epic Nap Rockstar", "Crossword Ace", "Garden Superhero", "Wizard of Epic Stories", "Scrabble Night Master",
    "Emperor of Strolls", "Memories Guru", "Grandchildren Ninja", "Anecdote Jedi", "Bingo Night Ace",
    "Rockstar of Old Tales", "Vegetable Garden Superhero", "Fairy-Tale Wizard", "Puzzle Master", "Emperor of Memories",
    "Porch Swing Guru", "Story Ninja", "Nap Jedi", "Ace of Legendary Tales", "Memories Rockstar",
    "Sage of Epic Anecdotes", "Storytelling Superhero", "Wizard of Memoirs", "Master of Stories", "Emperor of Legends",
    "Guru of Epic Tales", "Memories Ninja", "Tales Jedi", "Anecdote Ace", "Memoirs Rockstar",
    "Sage of Legends", "Fairy-Tale Superhero", "Wizard of Memories", "Master of Epic Tales", "Emperor of Memoirs",
    "Story Guru", "Legend Ninja", "Anecdote Jedi", "Fairy-Tale Ace", "Memories Rockstar",
    "Cosmic Legend", "Intergalactic Superhero", "Wizard of the Stars", "Master of Constellations", "Emperor of Galaxies",
    "Guru of Universes", "Comet Ninja", "Jedi of the Heavens", "Nebula Ace", "Star Rockstar",
    "Sage of the Milky Ways", "Supernova Superhero", "Pulsar Wizard", "Quasar Master", "Black Hole Emperor",
    "Meteor Guru", "Aurora Ninja", "Eclipse Jedi", "Nova Ace", "Galaxy Rockstar",
    "Intergalactic Hero",
]

# Noces en anglais (index = années de mariage, 1 à 60)
WEDDINGS_EN = [
    "Cotton", "Leather", "Wheat", "Wax", "Wood", "Cypress", "Wool", "Poppy", "Earthenware", "Tin",
    "Coral", "Silk", "Lily of the Valley", "Lead", "Crystal", "Sapphire", "Rose", "Turquoise", "Cretonne", "Porcelain",
    "Opal", "Bronze", "Beryl", "Satin", "Silver", "Jade", "Mahogany", "Nickel", "Velvet", "Pearl",
    "Sheepskin", "Copper", "Porphyry", "Amber", "Ruby", "Muslin", "Paper", "Mercury", "Crepe", "Emerald",
    "Iron", "Mother-of-Pearl", "Flannel", "Topaz", "Vermeil", "Lavender", "Cashmere", "Amethyst", "Cedar", "Gold",
    "Camellia", "Tourmaline", "Cherry Wood", "Sable", "Orchid", "Lapis Lazuli", "Azurite", "Maple", "Mink", "Diamond",
]

# Formes féminines des catégories d'âge : (masculin, féminin), testées dans l'ordre,
# première correspondance seulement (mot entier). Les titres absents sont épicènes
# (Ninja, Jedi, Guru, As/Ass/Asso, Rockstar, Sage, Pirate, Artiste, Légende…).
_FEMININE: dict[str, list[tuple[str, str]]] = {
    "fr": [
        ("Super-Héros", "Super-Héroïne"), ("Héros", "Héroïne"), ("Roi", "Reine"), ("Empereur", "Impératrice"),
        ("Maître", "Maîtresse"), ("Sorcier", "Sorcière"), ("Champion", "Championne"), ("Majeur", "Majeure"),
        ("Pré-Ado TikTokeur", "Pré-Ado TikTokeuse"),
    ],
    "en": [
        ("Superhero", "Superheroine"), ("Hero", "Heroine"), ("King", "Queen"), ("Emperor", "Empress"),
        ("Wizard", "Sorceress"),
    ],
    "de": [
        ("Intergalaktischer Superheld", "Intergalaktische Superheldin"),
        ("Intergalaktischer Held", "Intergalaktische Heldin"),
        ("Superheld", "Superheldin"), ("König", "Königin"), ("Kaiser", "Kaiserin"), ("Meister", "Meisterin"),
        ("Zauberer", "Zauberin"), ("Sieger", "Siegerin"), ("Pirat", "Piratin"), ("Künstler", "Künstlerin"),
        ("Rebell", "Rebellin"), ("Philosoph", "Philosophin"), ("Visionär", "Visionärin"), ("Weiser", "Weise"),
        ("TikToker", "TikTokerin"),
    ],
    "es": [
        ("Superhéroe Intergaláctico", "Superheroína Intergaláctica"), ("Héroe Intergaláctico", "Heroína Intergaláctica"),
        ("Superhéroe", "Superheroína"), ("Rey", "Reina"), ("Emperador", "Emperatriz"), ("Maestro", "Maestra"),
        ("Mago", "Maga"), ("Campeón", "Campeona"), ("Filósofo", "Filósofa"), ("Visionario", "Visionaria"),
        ("Sabio", "Sabia"),
    ],
    "it": [
        ("Supereroe Intergalattico", "Supereroina Intergalattica"), ("Eroe Intergalattico", "Eroina Intergalattica"),
        ("Supereroe", "Supereroina"), ("Re", "Regina"), ("Imperatore", "Imperatrice"), ("Maestro", "Maestra"),
        ("Mago", "Maga"), ("Campione", "Campionessa"), ("Filosofo", "Filosofa"), ("Visionario", "Visionaria"),
        ("Saggio", "Saggia"),
    ],
}
# Langues romanes : le titre est le premier mot (« Sabio de los Sabios Consejos »…)
_TITLE_FIRST = ("fr", "es", "it")


def _feminine(text: str, lang: str) -> str:
    for masc, fem in _FEMININE.get(lang, []):
        pattern = ("^" if lang in _TITLE_FIRST else r"(?<![\wÀ-ÿ])") + re.escape(masc) + r"(?![\wÀ-ÿ])"
        new, count = re.subn(pattern, fem, text, count=1)
        if count:
            return new
    return text


_AGE_CATEGORIES = {"en": AGE_CATEGORIES_EN, "de": AGE_CATEGORIES_DE, "es": AGE_CATEGORIES_ES, "it": AGE_CATEGORIES_IT}
_WEDDINGS = {"de": WEDDINGS_DE, "es": WEDDINGS_ES, "it": WEDDINGS_IT}


def age_category(age: int, category_fr: str | None, language: str, gender: str = GENDER_UNSPECIFIED) -> str | None:
    """Catégorie d'âge traduite (et accordée au féminin si genre = femme)."""
    if category_fr is None:
        return None
    lang = resolve_language(language)
    if lang == "fr":
        text = category_fr
    else:
        table = _AGE_CATEGORIES[lang]
        text = table[age] if 0 <= age < len(table) else category_fr
    return _feminine(text, lang) if gender == GENDER_FEMALE else text


def wedding_name(years: int, wedding_fr: str | None, language: str) -> str | None:
    if wedding_fr is None:
        return None
    lang = resolve_language(language)
    if lang == "fr" or not 1 <= years <= len(WEDDINGS_EN):
        return wedding_fr
    if lang in _WEDDINGS:
        return _WEDDINGS[lang][years - 1]
    return f"{WEDDINGS_EN[years - 1]} anniversary"


def medal_name(medal_fr: str | None, language: str) -> str | None:
    if medal_fr is None:
        return None
    return MEDALS[resolve_language(language)].get(medal_fr, medal_fr)


def event_type_label(event_type: str, language: str) -> str:
    return EVENT_TYPE_LABELS[resolve_language(language)].get(event_type, event_type)


def notify_title(language: str) -> str:
    return NOTIFY_TITLES[resolve_language(language)]


# ---------------------------------------------------------------------------
# Messages de notification
# ---------------------------------------------------------------------------
# Clés suffixées _m / _f : variantes selon le genre (repli sur la clé neutre).

MESSAGES: dict[str, dict[str, str]] = {
    "fr": {
        "year_one": "{n} an", "year_other": "{n} ans",
        "day_birthday": "🎂 Aujourd’hui, {person} a {years} !",
        "day_birthday_noage": "🎂 Aujourd’hui, c’est l’anniversaire {de_person} !",
        "day_anniversary": "💍 Aujourd’hui, {full} fête {years} de mariage",
        "day_anniversary_wedding": " : {wedding} !",
        "day_anniversary_end": " !",
        "day_anniversary_noage": "💍 Aujourd’hui, c’est le mariage {de_full} !",
        "day_memorial": "🕯️ Aujourd’hui, {person} aurait eu {years}.",
        "day_memorial_noage": "🕯️ Aujourd’hui, nous pensons à {person}.",
        "memorial_since": " Disparu(e) depuis {since}.",
        "memorial_since_m": " Disparu depuis {since}.",
        "memorial_since_f": " Disparue depuis {since}.",
        "memorial_end": " Une pensée en sa mémoire.",
        "day_promotion": "🏆 Aujourd’hui, {full} fête {years} de promotion !",
        "day_promotion_noage": "🏆 Aujourd’hui : promotion {de_full} !",
        "day_special": "⭐ Aujourd’hui : {full} ({years}) !",
        "day_special_noage": "⭐ Aujourd’hui : {full} !",
        "day_retirement": "🏖️ Aujourd’hui, {person} part à la retraite",
        "day_retirement_worked": " après {worked} de travail !",
        "day_retirement_end": " !",
        "day_retirement_medal": " Médaille du travail : {medal}.",
        "day_other": "📅 Aujourd’hui : {full} !",
        "death_anniversary": "🕯️ Il y a {since} aujourd’hui, {person} nous quittait. Une pensée en sa mémoire.",
        "when_tomorrow": "Demain", "when_days": "Dans {days} jours",
        "reminder": "⏳ {when} : {body}",
        "rem_birthday": "anniversaire {de_person}{suffix}",
        "rem_anniversary": "anniversaire de mariage {de_full}{suffix}",
        "rem_wedding": " – {wedding}",
        "rem_memorial": "souvenir {de_person}",
        "rem_memorial_age": ", qui aurait eu {years}",
        "rem_promotion": "anniversaire de la promotion {de_full}{suffix}",
        "rem_promotion_noage": "promotion {de_full}",
        "rem_special": "{full}{suffix}",
        "rem_retirement": "départ à la retraite {de_person}",
        "rem_death": "anniversaire du décès {de_person} ({since})",
        "test": "🧪 Test – {message}",
        "cal_retired": "{name} (Retraite atteinte)",
        "cal_retirement": "{name} (Retraite dans {years}, Médaille : {medal})",
        "cal_retirement_event": "{name} (Retraite, Médaille : {medal})",
        "cal_no_medal": "Aucune",
        "cal_memorial": "{name} (Âge si vivant : {age}, Depuis décès : {since})",
        "cal_memorial_nosince": "{name} (Âge si vivant : {age})",
        "cal_death": "{name} (Anniversaire du décès : {since})",
    },
    "en": {
        "year_one": "{n} year", "year_other": "{n} years",
        "day_birthday": "🎂 Today, {person} turns {n}!",
        "day_birthday_noage": "🎂 Today is {person}’s birthday!",
        "day_anniversary": "💍 Today, {full} celebrate {years} of marriage",
        "day_anniversary_wedding": ": {wedding}!",
        "day_anniversary_end": "!",
        "day_anniversary_noage": "💍 Today is {full}’s wedding day!",
        "day_memorial": "🕯️ Today, {person} would have turned {n}.",
        "day_memorial_noage": "🕯️ Today, we remember {person}.",
        "memorial_since": " Passed away {since} ago.",
        "memorial_end": " Thinking of them.",
        "memorial_end_m": " Thinking of him.",
        "memorial_end_f": " Thinking of her.",
        "day_promotion": "🏆 Today, {full} celebrates {years} since the promotion!",
        "day_promotion_noage": "🏆 Today: {full}’s promotion!",
        "day_special": "⭐ Today: {full} ({years})!",
        "day_special_noage": "⭐ Today: {full}!",
        "day_retirement": "🏖️ Today, {person} retires",
        "day_retirement_worked": " after {worked} of work!",
        "day_retirement_end": "!",
        "day_retirement_medal": " Work medal: {medal}.",
        "day_other": "📅 Today: {full}!",
        "death_anniversary": "🕯️ {since} ago today, {person} passed away. Thinking of them.",
        "death_anniversary_m": "🕯️ {since} ago today, {person} passed away. Thinking of him.",
        "death_anniversary_f": "🕯️ {since} ago today, {person} passed away. Thinking of her.",
        "when_tomorrow": "Tomorrow", "when_days": "In {days} days",
        "reminder": "⏳ {when}: {body}",
        "rem_birthday": "{person}’s birthday{suffix}",
        "rem_anniversary": "{full}’s wedding anniversary{suffix}",
        "rem_wedding": " – {wedding}",
        "rem_memorial": "remembering {person}",
        "rem_memorial_age": ", who would have turned {n}",
        "rem_promotion": "anniversary of {full}’s promotion{suffix}",
        "rem_promotion_noage": "{full}’s promotion",
        "rem_special": "{full}{suffix}",
        "rem_retirement": "{person}’s retirement",
        "rem_death": "anniversary of {person}’s passing ({since})",
        "test": "🧪 Test – {message}",
        "cal_retired": "{name} (Retired)",
        "cal_retirement": "{name} (Retirement in {years}, Medal: {medal})",
        "cal_retirement_event": "{name} (Retirement, Medal: {medal})",
        "cal_no_medal": "None",
        "cal_memorial": "{name} (Age if alive: {age}, Since death: {since})",
        "cal_memorial_nosince": "{name} (Age if alive: {age})",
        "cal_death": "{name} (Anniversary of passing: {since})",
    },
    "de": {
        "year_one": "{n} Jahr", "year_other": "{n} Jahre",
        "day_birthday": "🎂 Heute wird {person} {n}!",
        "day_birthday_noage": "🎂 Heute hat {person} Geburtstag!",
        "day_anniversary": "💍 Heute feiern {full} {years} Ehe",
        "day_anniversary_wedding": ": {wedding}!",
        "day_anniversary_end": "!",
        "day_anniversary_noage": "💍 Heute ist der Hochzeitstag von {full}!",
        "day_memorial": "🕯️ Heute wäre {person} {n} geworden.",
        "day_memorial_noage": "🕯️ Heute denken wir an {person}.",
        "memorial_since": " Verstorben vor {since_dat}.",
        "memorial_end": " In liebevoller Erinnerung.",
        "day_promotion": "🏆 Heute feiert {full} {years} seit der Beförderung!",
        "day_promotion_noage": "🏆 Heute: Beförderung von {full}!",
        "day_special": "⭐ Heute: {full} ({years})!",
        "day_special_noage": "⭐ Heute: {full}!",
        "day_retirement": "🏖️ Heute geht {person} in den Ruhestand",
        "day_retirement_worked": " nach {worked} Arbeit!",
        "day_retirement_end": "!",
        "day_retirement_medal": " Arbeitsmedaille: {medal}.",
        "day_other": "📅 Heute: {full}!",
        "death_anniversary": "🕯️ Heute vor {since_dat} ist {person} von uns gegangen. In liebevoller Erinnerung.",
        "when_tomorrow": "Morgen", "when_days": "In {days} Tagen",
        "reminder": "⏳ {when}: {body}",
        "rem_birthday": "Geburtstag von {person}{suffix}",
        "rem_anniversary": "Hochzeitstag von {full}{suffix}",
        "rem_wedding": " – {wedding}",
        "rem_memorial": "Gedenken an {person}",
        "rem_memorial_age": ", der/die {n} geworden wäre",
        "rem_memorial_age_m": ", der {n} geworden wäre",
        "rem_memorial_age_f": ", die {n} geworden wäre",
        "rem_promotion": "Jahrestag der Beförderung von {full}{suffix}",
        "rem_promotion_noage": "Beförderung von {full}",
        "rem_special": "{full}{suffix}",
        "rem_retirement": "Ruhestand von {person}",
        "rem_death": "Todestag von {person} ({since})",
        "test": "🧪 Test – {message}",
        "cal_retired": "{name} (Im Ruhestand)",
        "cal_retirement": "{name} (Ruhestand in {years}, Medaille: {medal})",
        "cal_retirement_event": "{name} (Ruhestand, Medaille: {medal})",
        "cal_no_medal": "Keine",
        "cal_memorial": "{name} (Alter, wenn noch am Leben: {age}, seit dem Tod: {since})",
        "cal_memorial_nosince": "{name} (Alter, wenn noch am Leben: {age})",
        "cal_death": "{name} (Todestag: {since})",
    },
    "es": {
        "year_one": "{n} año", "year_other": "{n} años",
        "day_birthday": "🎂 ¡Hoy {person} cumple {years}!",
        "day_birthday_noage": "🎂 ¡Hoy es el cumpleaños de {person}!",
        "day_anniversary": "💍 ¡Hoy, {full} celebran {years} de casados",
        "day_anniversary_wedding": ": {wedding}!",
        "day_anniversary_end": "!",
        "day_anniversary_noage": "💍 ¡Hoy es el aniversario de boda de {full}!",
        "day_memorial": "🕯️ Hoy, {person} habría cumplido {years}.",
        "day_memorial_noage": "🕯️ Hoy recordamos a {person}.",
        "memorial_since": " Nos dejó hace {since}.",
        "memorial_end": " Siempre en nuestra memoria.",
        "day_promotion": "🏆 ¡Hoy {full} celebra {years} desde su ascenso!",
        "day_promotion_noage": "🏆 Hoy: ¡ascenso de {full}!",
        "day_special": "⭐ Hoy: ¡{full} ({years})!",
        "day_special_noage": "⭐ Hoy: ¡{full}!",
        "day_retirement": "🏖️ ¡Hoy {person} se jubila",
        "day_retirement_worked": " después de {worked} de trabajo!",
        "day_retirement_end": "!",
        "day_retirement_medal": " Medalla del trabajo: {medal}.",
        "day_other": "📅 Hoy: ¡{full}!",
        "death_anniversary": "🕯️ Hoy hace {since} que {person} nos dejó. Siempre en nuestra memoria.",
        "when_tomorrow": "Mañana", "when_days": "Dentro de {days} días",
        "reminder": "⏳ {when}: {body}",
        "rem_birthday": "cumpleaños de {person}{suffix}",
        "rem_anniversary": "aniversario de boda de {full}{suffix}",
        "rem_wedding": " – {wedding}",
        "rem_memorial": "recuerdo de {person}",
        "rem_memorial_age": ", que habría cumplido {years}",
        "rem_promotion": "aniversario del ascenso de {full}{suffix}",
        "rem_promotion_noage": "ascenso de {full}",
        "rem_special": "{full}{suffix}",
        "rem_retirement": "jubilación de {person}",
        "rem_death": "aniversario del fallecimiento de {person} ({since})",
        "test": "🧪 Prueba – {message}",
        "cal_retired": "{name} (Jubilación alcanzada)",
        "cal_retirement": "{name} (Jubilación en {years}, Medalla: {medal})",
        "cal_retirement_event": "{name} (Jubilación, Medalla: {medal})",
        "cal_no_medal": "Ninguna",
        "cal_memorial": "{name} (Edad si viviera: {age}, Desde el fallecimiento: {since})",
        "cal_memorial_nosince": "{name} (Edad si viviera: {age})",
        "cal_death": "{name} (Aniversario del fallecimiento: {since})",
    },
    "it": {
        "year_one": "{n} anno", "year_other": "{n} anni",
        "day_birthday": "🎂 Oggi {person} compie {years}!",
        "day_birthday_noage": "🎂 Oggi è il compleanno di {person}!",
        "day_anniversary": "💍 Oggi {full} festeggiano {years} di matrimonio",
        "day_anniversary_wedding": ": {wedding}!",
        "day_anniversary_end": "!",
        "day_anniversary_noage": "💍 Oggi è l’anniversario di matrimonio di {full}!",
        "day_memorial": "🕯️ Oggi {person} avrebbe compiuto {years}.",
        "day_memorial_noage": "🕯️ Oggi ricordiamo {person}.",
        "memorial_since": " Scomparso/a da {since}.",
        "memorial_since_m": " Scomparso da {since}.",
        "memorial_since_f": " Scomparsa da {since}.",
        "memorial_end": " Sempre nei nostri cuori.",
        "day_promotion": "🏆 Oggi {full} festeggia {years} dalla promozione!",
        "day_promotion_noage": "🏆 Oggi: promozione di {full}!",
        "day_special": "⭐ Oggi: {full} ({years})!",
        "day_special_noage": "⭐ Oggi: {full}!",
        "day_retirement": "🏖️ Oggi {person} va in pensione",
        "day_retirement_worked": " dopo {worked} di lavoro!",
        "day_retirement_end": "!",
        "day_retirement_medal": " Medaglia del lavoro: {medal}.",
        "day_other": "📅 Oggi: {full}!",
        "death_anniversary": "🕯️ {since} fa, oggi, {person} ci lasciava. Sempre nei nostri cuori.",
        "when_tomorrow": "Domani", "when_days": "Tra {days} giorni",
        "reminder": "⏳ {when}: {body}",
        "rem_birthday": "compleanno di {person}{suffix}",
        "rem_anniversary": "anniversario di matrimonio di {full}{suffix}",
        "rem_wedding": " – {wedding}",
        "rem_memorial": "ricordo di {person}",
        "rem_memorial_age": ", che avrebbe compiuto {years}",
        "rem_promotion": "anniversario della promozione di {full}{suffix}",
        "rem_promotion_noage": "promozione di {full}",
        "rem_special": "{full}{suffix}",
        "rem_retirement": "pensione di {person}",
        "rem_death": "anniversario della scomparsa di {person} ({since})",
        "test": "🧪 Test – {message}",
        "cal_retired": "{name} (Pensione raggiunta)",
        "cal_retirement": "{name} (Pensione tra {years}, Medaglia: {medal})",
        "cal_retirement_event": "{name} (Pensione, Medaglia: {medal})",
        "cal_no_medal": "Nessuna",
        "cal_memorial": "{name} (Età se in vita: {age}, Dalla scomparsa: {since})",
        "cal_memorial_nosince": "{name} (Età se in vita: {age})",
        "cal_death": "{name} (Anniversario della scomparsa: {since})",
    },
}


def _de(name: str) -> str:
    """'de Paul' / 'd’Océane' (français)."""
    return f"d’{name}" if name and name[0] in _VOWELS_NO_H else f"de {name}"


class Texts:
    """Accès aux messages d'une langue, avec accord selon le genre."""

    def __init__(self, language: str | None, gender: str = GENDER_UNSPECIFIED) -> None:
        self.lang = resolve_language(language)
        self.gender = normalize_gender(gender)
        self._msgs = MESSAGES[self.lang]

    def raw(self, key: str) -> str:
        suffix = {"male": "_m", "female": "_f"}.get(self.gender)
        if suffix and key + suffix in self._msgs:
            return self._msgs[key + suffix]
        return self._msgs.get(key, MESSAGES[FALLBACK].get(key, key))

    def years(self, n: int) -> str:
        return self.raw("year_one" if abs(n) == 1 else "year_other").format(n=n)

    def years_dative(self, n: int) -> str:
        """Allemand : « vor 8 Jahren »."""
        if self.lang == "de":
            return f"{n} Jahr" if abs(n) == 1 else f"{n} Jahren"
        return self.years(n)

    def fmt(self, key: str, **kwargs: Any) -> str:
        ctx = dict(kwargs)
        for name in ("person", "full"):
            if name in ctx:
                ctx[f"de_{name}"] = _de(str(ctx[name]))
        return self.raw(key).format_map(_Safe(ctx))


class _Safe(dict):
    def __missing__(self, key: str) -> str:
        return ""
