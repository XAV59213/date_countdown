"""Textes générés côté Python (notifications, catégories d'âge, noces, médailles…).

Le code ne manipule que des clés stables (type d'événement, âge, clé de noces,
clé de médaille) ; les libellés suivent la langue de Home Assistant
(``hass.config.language``) :
- types d'événements, médailles et titre des notifications : les 22 langues de
  ``translations/*.json`` (mêmes textes que l'interface), repli anglais ;
- notifications, catégories d'âge (accordées au genre), noces, calendrier :
  français, anglais, allemand, espagnol, italien ; autres langues : anglais.
"""

from __future__ import annotations

import json
from pathlib import Path
import re
from typing import Any

from .const import WEDDING_ANNIVERSARIES
from .i18n_data import (
    AGE_CATEGORIES_DE,
    AGE_CATEGORIES_EN,
    AGE_CATEGORIES_ES,
    AGE_CATEGORIES_FR,
    AGE_CATEGORIES_IT,
    WEDDINGS_DE,
    WEDDINGS_EN,
    WEDDINGS_ES,
    WEDDINGS_FR,
    WEDDINGS_IT,
)

GENDER_UNSPECIFIED = "unspecified"
GENDER_MALE = "male"
GENDER_FEMALE = "female"
GENDERS = [GENDER_UNSPECIFIED, GENDER_MALE, GENDER_FEMALE]

SUPPORTED = ("fr", "en", "de", "es", "it")
FALLBACK = "en"

# ---------------------------------------------------------------------------
# Catalogue des 22 langues (translations/*.json, chargé une fois à l'import)
# ---------------------------------------------------------------------------

_TRANSLATIONS_DIR = Path(__file__).parent / "translations"


def _load_catalog() -> dict[str, dict[str, Any]]:
    catalog: dict[str, dict[str, Any]] = {}
    for path in sorted(_TRANSLATIONS_DIR.glob("*.json")):
        try:
            catalog[path.stem] = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):  # fichier illisible : la langue retombe sur l'anglais
            continue
    return catalog


_CATALOG = _load_catalog()
_CATALOG_LANGS = {lang.lower(): lang for lang in _CATALOG}
_LANG_ALIASES = {"no": "nb", "nn": "nb"}


def catalog_language(language: str | None) -> str:
    """'pt-BR', 'pt_br', 'de-AT', 'no'… → fichier translations/<langue>.json disponible (repli : anglais)."""
    lang = (language or "").strip().lower().replace("_", "-")
    if lang in _CATALOG_LANGS:
        return _CATALOG_LANGS[lang]
    base = lang.split("-", 1)[0]
    base = _LANG_ALIASES.get(base, base)
    return _CATALOG_LANGS.get(base, FALLBACK)


def _catalog_get(language: str | None, *path: str) -> str | None:
    for lang in (catalog_language(language), FALLBACK):
        node: Any = _CATALOG.get(lang, {})
        for key in path:
            node = node.get(key) if isinstance(node, dict) else None
        if isinstance(node, str) and node:
            return node
    return None


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


_AGE_CATEGORIES = {
    "fr": AGE_CATEGORIES_FR, "en": AGE_CATEGORIES_EN, "de": AGE_CATEGORIES_DE,
    "es": AGE_CATEGORIES_ES, "it": AGE_CATEGORIES_IT,
}
_WEDDINGS = {"fr": WEDDINGS_FR, "de": WEDDINGS_DE, "es": WEDDINGS_ES, "it": WEDDINGS_IT}

# Anciennes valeurs françaises (avant 1.2.22) → clés stables, pour compatibilité
LEGACY_MEDAL_KEYS = {"Argent": "silver", "Vermeil": "vermeil", "Or": "gold", "Grand Or": "grand_gold"}
MEDAL_KEYS = ("silver", "vermeil", "gold", "grand_gold")


def age_category(age: int | None, language: str, gender: str = GENDER_UNSPECIFIED) -> str | None:
    """Catégorie d'âge (clé = l'âge, 0 à 120) traduite et accordée au féminin si genre = femme."""
    if age is None or not 0 <= age < len(AGE_CATEGORIES_FR):
        return None
    lang = resolve_language(language)
    text = _AGE_CATEGORIES[lang][age]
    return _feminine(text, lang) if gender == GENDER_FEMALE else text


def wedding_key(years: int | None) -> str | None:
    """Clé stable des noces (« silver », « gold »…) pour un nombre d'années de mariage."""
    return WEDDING_ANNIVERSARIES.get(years) if years is not None else None


def wedding_name(years: int | None, language: str) -> str | None:
    """Nom des noces traduit (ex. 25 → « Noces d'Argent », « Silver anniversary »)."""
    if wedding_key(years) is None:
        return None
    lang = resolve_language(language)
    if lang in _WEDDINGS:
        return _WEDDINGS[lang][years - 1]
    return f"{WEDDINGS_EN[years - 1]} anniversary"


def medal_key(medal: str | None) -> str | None:
    """Clé stable d'une médaille (accepte aussi les anciennes valeurs françaises)."""
    if medal is None:
        return None
    key = LEGACY_MEDAL_KEYS.get(medal, medal)
    return key if key in MEDAL_KEYS else None


def medal_name(medal: str | None, language: str) -> str | None:
    """Nom de la médaille du travail dans la langue de HA (22 langues, comme le capteur)."""
    key = medal_key(medal)
    if key is None:
        return None
    return _catalog_get(language, "entity", "sensor", "work_medal", "state", key) or key


def no_medal_label(language: str) -> str:
    return _catalog_get(language, "entity", "sensor", "work_medal", "state", "none") or "None"


def event_type_label(event_type: str, language: str) -> str:
    """Libellé du type d'événement (22 langues, mêmes textes que la liste de l'assistant)."""
    return _catalog_get(language, "selector", "event_type", "options", event_type) or event_type


def notify_title(language: str) -> str:
    """Titre des notifications : nom de l'intégration traduit (22 langues)."""
    return _catalog_get(language, "config", "step", "user", "title") or "Memories and Celebrations"


def empty_entry_title(language: str) -> str:
    """Titre d'une entrée sans événement."""
    return Texts(language).raw("entry_empty")


# ---------------------------------------------------------------------------
# Messages de notification
# ---------------------------------------------------------------------------
# Clés suffixées _m / _f : variantes selon le genre (repli sur la clé neutre).

MESSAGES: dict[str, dict[str, str]] = {
    "fr": {
        "entry_empty": "Compte à rebours d'événements (vide)",
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
        "cal_memorial": "{name} (Âge si vivant : {age}, Depuis décès : {since})",
        "cal_memorial_nosince": "{name} (Âge si vivant : {age})",
        "cal_death": "{name} (Anniversaire du décès : {since})",
    },
    "en": {
        "entry_empty": "Event countdown (empty)",
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
        "cal_memorial": "{name} (Age if alive: {age}, Since death: {since})",
        "cal_memorial_nosince": "{name} (Age if alive: {age})",
        "cal_death": "{name} (Anniversary of passing: {since})",
    },
    "de": {
        "entry_empty": "Ereignis-Countdown (leer)",
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
        "cal_memorial": "{name} (Alter, wenn noch am Leben: {age}, seit dem Tod: {since})",
        "cal_memorial_nosince": "{name} (Alter, wenn noch am Leben: {age})",
        "cal_death": "{name} (Todestag: {since})",
    },
    "es": {
        "entry_empty": "Cuenta atrás de eventos (vacía)",
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
        "cal_memorial": "{name} (Edad si viviera: {age}, Desde el fallecimiento: {since})",
        "cal_memorial_nosince": "{name} (Edad si viviera: {age})",
        "cal_death": "{name} (Aniversario del fallecimiento: {since})",
    },
    "it": {
        "entry_empty": "Conto alla rovescia degli eventi (vuoto)",
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
