"""Constants for Date Countdown integration."""

import logging

_LOGGER = logging.getLogger(__name__)

DOMAIN = "date_countdown"
PLATFORMS = ["sensor", "binary_sensor", "calendar"]
DATE_FORMAT = "DD/MM/YYYY"

# Carte Lovelace native (servie par l'intégration)
URL_BASE = "/date_countdown"
CARD_FILENAME = "date-countdown-card.js"
STATIC_CARD_PATH = f"{URL_BASE}/{CARD_FILENAME}"
VERSION = "1.2.24"  # aligné sur manifest.json (cache ?v=)

EVENT_TYPES = ["birthday", "anniversary", "memorial", "promotion", "special_event", "retirement"]

# Catégories d'âge pour les anniversaires, une pour chaque âge de 0 à 120 ans
# Catégories d'âge des anniversaires : une par âge, de 0 à AGE_CATEGORY_MAX ans.
# Clé stable = l'âge ; libellés traduits dans i18n_data.py (AGE_CATEGORIES_<LANGUE>).
AGE_CATEGORY_MAX = 120

# Icônes associées à chaque catégorie d'âge
# Icône de chaque catégorie d'âge (index = âge, 0 à AGE_CATEGORY_MAX)
AGE_CATEGORY_ICONS = [
    "mdi:star-shooting", "mdi:rocket", "mdi:draw", "mdi:shovel", "mdi:cupcake", "mdi:slide",
    "mdi:sticker", "mdi:bicycle", "mdi:toy-brick", "mdi:home-roof", "mdi:pokeball", "mdi:cellphone-play",
    "mdi:emoticon-cool", "mdi:emoticon-lol", "mdi:camera", "mdi:pound", "mdi:snapchat", "mdi:instagram",
    "mdi:account-check", "mdi:music", "mdi:glass-cocktail", "mdi:party-popper", "mdi:chat", "mdi:music-note",
    "mdi:food", "mdi:check-all", "mdi:television-play", "mdi:lightbulb-on", "mdi:microphone", "mdi:cellphone-video",
    "mdi:food", "mdi:video", "mdi:table", "mdi:glass-wine", "mdi:head-sync", "mdi:cake",
    "mdi:grill", "mdi:emoticon-happy", "mdi:help-circle", "mdi:chef-hat", "mdi:run-fast", "mdi:airplane",
    "mdi:chess-king", "mdi:lightbulb-on", "mdi:school", "mdi:cash", "mdi:comment-quote", "mdi:grill",
    "mdi:vinyl", "mdi:hammer", "mdi:emoticon-happy", "mdi:sleep", "mdi:book-open", "mdi:cassette",
    "mdi:pot-mix", "mdi:cards", "mdi:hiking", "mdi:owl", "mdi:yarn", "mdi:television-classic",
    "mdi:sleep", "mdi:pencil", "mdi:flower", "mdi:book-open", "mdi:alphabetical", "mdi:walk",
    "mdi:image-album", "mdi:human-child", "mdi:comment-quote", "mdi:slot-machine", "mdi:book-open", "mdi:carrot",
    "mdi:book-open", "mdi:puzzle", "mdi:image-album", "mdi:seat", "mdi:comment-quote", "mdi:sleep",
    "mdi:book-open", "mdi:image-album", "mdi:owl", "mdi:book-open", "mdi:book-open", "mdi:comment-quote",
    "mdi:medal", "mdi:book-open", "mdi:image-album", "mdi:comment-quote", "mdi:book-open", "mdi:image-album",
    "mdi:owl", "mdi:book-open", "mdi:image-album", "mdi:comment-quote", "mdi:medal", "mdi:book-open",
    "mdi:run-fast", "mdi:comment-quote", "mdi:book-open", "mdi:image-album", "mdi:star-circle", "mdi:rocket",
    "mdi:star", "mdi:star-circle", "mdi:orbit", "mdi:universe", "mdi:meteor", "mdi:star",
    "mdi:cloud-circle", "mdi:star-shooting", "mdi:orbit", "mdi:star-shooting", "mdi:pulse", "mdi:radiobox-marked",
    "mdi:circle-off", "mdi:meteor", "mdi:weather-sunset", "mdi:moon-waning-crescent", "mdi:star-circle", "mdi:orbit",
    "mdi:medal",
]

# Échelons de la médaille du travail (clés stables, traduites via translations/*.json :
# entity.sensor.work_medal.state.<clé>)
WORK_MEDAL_LEVELS = {20: "silver", 30: "vermeil", 35: "gold", 40: "grand_gold"}

# Échelons réduits pour travaux pénibles
WORK_MEDAL_PENIBLE_LEVELS = {18: "silver", 25: "vermeil", 30: "gold", 35: "grand_gold"}

# Noces (années de mariage → clé stable) ; libellés traduits dans i18n_data.py (WEDDINGS_<LANGUE>)
WEDDING_ANNIVERSARIES = {
    1: "cotton",
    2: "leather",
    3: "wheat",
    4: "wax",
    5: "wood",
    6: "cypress",
    7: "wool",
    8: "poppy",
    9: "earthenware",
    10: "tin",
    11: "coral",
    12: "silk",
    13: "lily_of_the_valley",
    14: "lead",
    15: "crystal",
    16: "sapphire",
    17: "rose",
    18: "turquoise",
    19: "cretonne",
    20: "porcelain",
    21: "opal",
    22: "bronze",
    23: "beryl",
    24: "satin",
    25: "silver",
    26: "jade",
    27: "mahogany",
    28: "nickel",
    29: "velvet",
    30: "pearl",
    31: "sheepskin",
    32: "copper",
    33: "porphyry",
    34: "amber",
    35: "ruby",
    36: "muslin",
    37: "paper",
    38: "mercury",
    39: "crepe",
    40: "emerald",
    41: "iron",
    42: "mother_of_pearl",
    43: "flannel",
    44: "topaz",
    45: "vermeil",
    46: "lavender",
    47: "cashmere",
    48: "amethyst",
    49: "cedar",
    50: "gold",
    51: "camellia",
    52: "tourmaline",
    53: "cherry_wood",
    54: "sable",
    55: "orchid",
    56: "lapis_lazuli",
    57: "azurite",
    58: "maple",
    59: "mink",
    60: "diamond",
}

# Notifications natives (options de chaque entrée, clé "notifications")
CONF_NOTIFICATIONS = "notifications"
CONF_NOTIFY_ENABLED = "enabled"
CONF_NOTIFY_TARGETS = "targets"
CONF_NOTIFY_TIME = "time"
CONF_NOTIFY_REMINDER_DAYS = "reminder_days"
CONF_NOTIFY_PERSISTENT = "persistent"
CONF_NOTIFY_ENTITIES = "entities"  # entités notify.* modernes (service notify.send_message)
CONF_NOTIFY_DEATH = "death_anniversary"  # rappel de l'anniversaire du décès (mémoriaux)

DEFAULT_NOTIFY_TIME = "09:00:00"
DEFAULT_NOTIFY_REMINDER_DAYS = 0
MAX_NOTIFY_REMINDER_DAYS = 60

NOTIFY_STORAGE_KEY = f"{DOMAIN}.notifications"
NOTIFY_STORAGE_VERSION = 1

SERVICE_SEND_TEST_NOTIFICATION = "send_test_notification"
