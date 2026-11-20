/*
 * Cartes Lovelace — Souvenirs et Célébrations (date_countdown)
 * Informations, Liste / Agenda, Compte à rebours, Frise des mois, Mémoriaux.
 * Servies et enregistrées automatiquement par l'intégration.
 * Vanilla JS + shadow DOM, aucune dépendance externe.
 * Langue : hass.locale.language / hass.language (fr, en, de, es, it ; repli anglais).
 */
const CARD_TAG = "date-countdown-informations-card";
const CARD_VERSION = "1.2.18";
const DC_DOMAIN = "date_countdown";
const DC_DOC = "https://github.com/XAV59213/date_countdown#-cartes-lovelace";

const _asList = (v) => (Array.isArray(v) ? v : v ? [v] : []);
const _esc = (s) =>
  String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c]);

/* ---------------------------------------------------------------------- */
/* Traductions                                                             */
/* ---------------------------------------------------------------------- */
// Suffixes _m / _f : variantes selon l'attribut « gender » du capteur (repli sur la clé neutre).
const DC_I18N = {
  fr: {
    "type.birthday": "Anniversaires", "type.anniversary": "Mariages", "type.memorial": "Mémoriaux",
    "type.promotion": "Promotions", "type.special_event": "Événements", "type.retirement": "Retraites",
    "one.birthday": "Anniversaire", "one.anniversary": "Anniversaire de mariage", "one.memorial": "Mémorial",
    "one.promotion": "Promotion", "one.special_event": "Événement spécial", "one.retirement": "Retraite",
    "next.birthday": "Prochain anniversaire", "next.anniversary": "Prochain anniversaire de mariage", "next.memorial": "Prochain souvenir",
    "next.promotion": "Prochaine promotion", "next.special_event": "Prochain événement", "next.retirement": "Prochaine retraite",
    year_one: "{n} an", year_other: "{n} ans",
    turns_today: "fête ses {y} 🎉", will_turn: "aura {y}", married: "{y} de mariage",
    would_have: "aurait eu {y}",
    since_death: "disparu(e) depuis {y}", since_death_m: "disparu depuis {y}", since_death_f: "disparue depuis {y}",
    retired_since: "retraité(e) depuis {y}", retired_since_m: "retraité depuis {y}", retired_since_f: "retraitée depuis {y}",
    retired_year: "retraité(e) cette année", retired_year_m: "retraité cette année", retired_year_f: "retraitée cette année",
    leaves_in: "départ dans {y}", leaves_soon: "départ dans moins d'un an", career: "{y} de carrière", medal: "🏅 médaille {m}",
    s_turns_today: "{n} fête ses {y} !", s_will_turn: "{n} aura {y}", s_married_today: "{n} : {y} de mariage aujourd'hui !",
    s_married: "{n} : {y} de mariage", s_would_have: "{n} aurait eu {y}",
    s_retired_since: "{n} est retraité(e) depuis {y}", s_retired_since_m: "{n} est retraité depuis {y}", s_retired_since_f: "{n} est retraitée depuis {y}",
    s_retired: "{n} est retraité(e)", s_retired_m: "{n} est retraité", s_retired_f: "{n} est retraitée",
    s_retires_today: "{n} part à la retraite aujourd'hui !", s_retires: "{n} part à la retraite",
    today: "Aujourd'hui !", today_plain: "Aujourd'hui", tomorrow: "Demain", in_days: "dans {d} jours", dminus: "J-{d}",
    notif_on: "Notifications actives", list_title: "Souvenirs et Célébrations", no_events: "Aucun événement à afficher.",
    no_upcoming: "Aucun événement à venir.", retired_badge: "retraité(e)", retired_badge_m: "retraité", retired_badge_f: "retraitée",
    day_j: "Jour J", day_one: "jour", day_other: "jours", is_today: "C'est aujourd'hui !", on_date: "le {date}",
    timeline_title: "Frise des célébrations", no_months: "Aucun événement sur les {m} prochains mois.",
    memorial_title: "En mémoire", m_would_have: "aurait eu <b>{y}</b> le {date}", m_would_have_today: "Aurait eu <b>{y}</b> aujourd'hui",
    at_age: "à {y}", no_memorial: "Aucun mémorial trouvé.",
    info_title: "Informations", info_today: "🎉 Aujourd'hui, c'est l'anniversaire de <b>{n}</b> !", info_celebrates: "{n} fête ses <b>{y}</b>",
    info_none_today: "Aujourd'hui, pas d'anniversaire.", info_next: "Le prochain anniversaire est <b>{when}</b>",
    info_tomorrow: "demain", info_in_days: "dans {d} jours", info_will: "{n} aura <b>{y}</b>",
    info_cat_future: "et sera un(e) <b>{c}</b> !", info_cat_future_m: "et sera un <b>{c}</b> !", info_cat_future_f: "et sera une <b>{c}</b> !",
    info_cat_now: "et devient un(e) <b>{c}</b> !", info_cat_now_m: "et devient un <b>{c}</b> !", info_cat_now_f: "et devient une <b>{c}</b> !",
    info_no_sensor: "Aucun capteur d'anniversaire trouvé. Choisis des capteurs dans l'éditeur de la carte.",
  },
  en: {
    "type.birthday": "Birthdays", "type.anniversary": "Weddings", "type.memorial": "Memorials",
    "type.promotion": "Promotions", "type.special_event": "Events", "type.retirement": "Retirements",
    "one.birthday": "Birthday", "one.anniversary": "Wedding anniversary", "one.memorial": "Memorial",
    "one.promotion": "Promotion", "one.special_event": "Special event", "one.retirement": "Retirement",
    "next.birthday": "Next birthday", "next.anniversary": "Next wedding anniversary", "next.memorial": "Next remembrance",
    "next.promotion": "Next promotion", "next.special_event": "Next event", "next.retirement": "Next retirement",
    year_one: "{n} year", year_other: "{n} years",
    turns_today: "turns {y} today 🎉", will_turn: "will turn {y}", married: "{y} of marriage",
    would_have: "would have turned {y}", since_death: "passed away {y} ago",
    retired_since: "retired for {y}", retired_year: "retired this year",
    leaves_in: "retires in {y}", leaves_soon: "retires in less than a year", career: "{y} of career", medal: "🏅 {m} medal",
    s_turns_today: "{n} turns {y} today!", s_will_turn: "{n} will turn {y}", s_married_today: "{n}: {y} of marriage today!",
    s_married: "{n}: {y} of marriage", s_would_have: "{n} would have turned {y}",
    s_retired_since: "{n} has been retired for {y}", s_retired: "{n} is retired",
    s_retires_today: "{n} retires today!", s_retires: "{n} is retiring",
    today: "Today!", today_plain: "Today", tomorrow: "Tomorrow", in_days: "in {d} days", dminus: "D-{d}",
    notif_on: "Notifications enabled", list_title: "Memories and Celebrations", no_events: "No events to show.",
    no_upcoming: "No upcoming events.", retired_badge: "retired",
    day_j: "Today", day_one: "day", day_other: "days", is_today: "It's today!", on_date: "on {date}",
    timeline_title: "Celebrations timeline", no_months: "No events in the next {m} months.",
    memorial_title: "In memory", m_would_have: "would have turned <b>{y}</b> on {date}", m_would_have_today: "Would have turned <b>{y}</b> today",
    at_age: "aged {y}", no_memorial: "No memorial found.",
    info_title: "Information", info_today: "🎉 Today is <b>{n}</b>'s birthday!", info_celebrates: "{n} turns <b>{y}</b>",
    info_none_today: "No birthday today.", info_next: "The next birthday is <b>{when}</b>",
    info_tomorrow: "tomorrow", info_in_days: "in {d} days", info_will: "{n} will turn <b>{y}</b>",
    info_cat_future: "and will become a <b>{c}</b>!", info_cat_now: "and becomes a <b>{c}</b>!",
    info_no_sensor: "No birthday sensor found. Pick sensors in the card editor.",
  },
  de: {
    "type.birthday": "Geburtstage", "type.anniversary": "Hochzeitstage", "type.memorial": "Gedenktage",
    "type.promotion": "Beförderungen", "type.special_event": "Ereignisse", "type.retirement": "Ruhestand",
    "one.birthday": "Geburtstag", "one.anniversary": "Hochzeitstag", "one.memorial": "Gedenktag",
    "one.promotion": "Beförderung", "one.special_event": "Besonderes Ereignis", "one.retirement": "Ruhestand",
    "next.birthday": "Nächster Geburtstag", "next.anniversary": "Nächster Hochzeitstag", "next.memorial": "Nächstes Gedenken",
    "next.promotion": "Nächste Beförderung", "next.special_event": "Nächstes Ereignis", "next.retirement": "Nächster Ruhestand",
    year_one: "{n} Jahr", year_other: "{n} Jahre",
    turns_today: "wird heute {n} 🎉", will_turn: "wird {n}", married: "{y} verheiratet",
    would_have: "wäre {n} geworden", since_death: "verstorben vor {yd}",
    retired_since: "seit {yd} im Ruhestand", retired_year: "seit diesem Jahr im Ruhestand",
    leaves_in: "Ruhestand in {yd}", leaves_soon: "Ruhestand in weniger als einem Jahr", career: "{y} Berufsleben", medal: "🏅 Medaille {m}",
    s_turns_today: "{n} wird heute {a}!", s_will_turn: "{n} wird {a}", s_married_today: "{n}: heute {y} verheiratet!",
    s_married: "{n}: {y} verheiratet", s_would_have: "{n} wäre {a} geworden",
    s_retired_since: "{n} ist seit {yd} im Ruhestand", s_retired: "{n} ist im Ruhestand",
    s_retires_today: "{n} geht heute in den Ruhestand!", s_retires: "{n} geht in den Ruhestand",
    today: "Heute!", today_plain: "Heute", tomorrow: "Morgen", in_days: "in {d} Tagen", dminus: "T-{d}",
    notif_on: "Benachrichtigungen aktiv", list_title: "Erinnerungen und Feiern", no_events: "Keine Ereignisse.",
    no_upcoming: "Keine anstehenden Ereignisse.", retired_badge: "im Ruhestand",
    day_j: "Heute", day_one: "Tag", day_other: "Tage", is_today: "Es ist heute!", on_date: "am {date}",
    timeline_title: "Zeitleiste der Feiern", no_months: "Keine Ereignisse in den nächsten {m} Monaten.",
    memorial_title: "In Erinnerung", m_would_have: "wäre am {date} <b>{a}</b> geworden", m_would_have_today: "Wäre heute <b>{a}</b> geworden",
    at_age: "mit {y}", no_memorial: "Kein Gedenktag gefunden.",
  },
  es: {
    "type.birthday": "Cumpleaños", "type.anniversary": "Bodas", "type.memorial": "Memoriales",
    "type.promotion": "Ascensos", "type.special_event": "Eventos", "type.retirement": "Jubilaciones",
    "one.birthday": "Cumpleaños", "one.anniversary": "Aniversario de boda", "one.memorial": "Memorial",
    "one.promotion": "Ascenso", "one.special_event": "Evento especial", "one.retirement": "Jubilación",
    "next.birthday": "Próximo cumpleaños", "next.anniversary": "Próximo aniversario de boda", "next.memorial": "Próximo recuerdo",
    "next.promotion": "Próximo ascenso", "next.special_event": "Próximo evento", "next.retirement": "Próxima jubilación",
    year_one: "{n} año", year_other: "{n} años",
    turns_today: "cumple {y} hoy 🎉", will_turn: "cumplirá {y}", married: "{y} de casados",
    would_have: "habría cumplido {y}", since_death: "nos dejó hace {y}",
    retired_since: "jubilado/a desde hace {y}", retired_since_m: "jubilado desde hace {y}", retired_since_f: "jubilada desde hace {y}",
    retired_year: "jubilado/a este año", retired_year_m: "jubilado este año", retired_year_f: "jubilada este año",
    leaves_in: "se jubila en {y}", leaves_soon: "se jubila en menos de un año", career: "{y} de carrera", medal: "🏅 medalla {m}",
    s_turns_today: "¡{n} cumple {y} hoy!", s_will_turn: "{n} cumplirá {y}", s_married_today: "{n}: ¡{y} de casados hoy!",
    s_married: "{n}: {y} de casados", s_would_have: "{n} habría cumplido {y}",
    s_retired_since: "{n} está jubilado/a desde hace {y}", s_retired: "{n} está jubilado/a",
    s_retired_since_m: "{n} está jubilado desde hace {y}", s_retired_since_f: "{n} está jubilada desde hace {y}",
    s_retired_m: "{n} está jubilado", s_retired_f: "{n} está jubilada",
    s_retires_today: "¡{n} se jubila hoy!", s_retires: "{n} se jubila",
    today: "¡Hoy!", today_plain: "Hoy", tomorrow: "Mañana", in_days: "en {d} días", dminus: "D-{d}",
    notif_on: "Notificaciones activas", list_title: "Recuerdos y Celebraciones", no_events: "No hay eventos.",
    no_upcoming: "No hay eventos próximos.", retired_badge: "jubilado/a", retired_badge_m: "jubilado", retired_badge_f: "jubilada",
    day_j: "Hoy", day_one: "día", day_other: "días", is_today: "¡Es hoy!", on_date: "el {date}",
    timeline_title: "Cronología de celebraciones", no_months: "No hay eventos en los próximos {m} meses.",
    memorial_title: "En memoria", m_would_have: "habría cumplido <b>{y}</b> el {date}", m_would_have_today: "Habría cumplido <b>{y}</b> hoy",
    at_age: "a los {y}", no_memorial: "No se encontró ningún memorial.",
  },
  it: {
    "type.birthday": "Compleanni", "type.anniversary": "Matrimoni", "type.memorial": "Commemorazioni",
    "type.promotion": "Promozioni", "type.special_event": "Eventi", "type.retirement": "Pensioni",
    "one.birthday": "Compleanno", "one.anniversary": "Anniversario di matrimonio", "one.memorial": "Commemorazione",
    "one.promotion": "Promozione", "one.special_event": "Evento speciale", "one.retirement": "Pensione",
    "next.birthday": "Prossimo compleanno", "next.anniversary": "Prossimo anniversario di matrimonio", "next.memorial": "Prossimo ricordo",
    "next.promotion": "Prossima promozione", "next.special_event": "Prossimo evento", "next.retirement": "Prossima pensione",
    year_one: "{n} anno", year_other: "{n} anni",
    turns_today: "compie {y} oggi 🎉", will_turn: "compirà {y}", married: "{y} di matrimonio",
    would_have: "avrebbe compiuto {y}",
    since_death: "scomparso/a da {y}", since_death_m: "scomparso da {y}", since_death_f: "scomparsa da {y}",
    retired_since: "in pensione da {y}", retired_year: "in pensione da quest'anno",
    leaves_in: "pensione tra {y}", leaves_soon: "pensione tra meno di un anno", career: "{y} di carriera", medal: "🏅 medaglia {m}",
    s_turns_today: "{n} compie {y} oggi!", s_will_turn: "{n} compirà {y}", s_married_today: "{n}: {y} di matrimonio oggi!",
    s_married: "{n}: {y} di matrimonio", s_would_have: "{n} avrebbe compiuto {y}",
    s_retired_since: "{n} è in pensione da {y}", s_retired: "{n} è in pensione",
    s_retires_today: "{n} va in pensione oggi!", s_retires: "{n} va in pensione",
    today: "Oggi!", today_plain: "Oggi", tomorrow: "Domani", in_days: "tra {d} giorni", dminus: "G-{d}",
    notif_on: "Notifiche attive", list_title: "Ricordi e Celebrazioni", no_events: "Nessun evento.",
    no_upcoming: "Nessun evento in arrivo.", retired_badge: "in pensione",
    day_j: "Oggi", day_one: "giorno", day_other: "giorni", is_today: "È oggi!", on_date: "il {date}",
    timeline_title: "Cronologia delle celebrazioni", no_months: "Nessun evento nei prossimi {m} mesi.",
    memorial_title: "In memoria", m_would_have: "avrebbe compiuto <b>{y}</b> il {date}", m_would_have_today: "Avrebbe compiuto <b>{y}</b> oggi",
    at_age: "a {y}", no_memorial: "Nessuna commemorazione trovata.",
  },
};

// Éditeurs (fr / en ; repli anglais)
const DC_EDITOR_I18N = {
  fr: {
    title: "Titre", entities: "Capteurs (sélection manuelle)", types: "Types d'événements affichés",
    max_items: "Nombre maximum d'événements", horizon_days: "Horizon", group_by_type: "Regrouper par type",
    compact: "Affichage compact", show_date: "Afficher la date", show_details: "Afficher les détails (âge, noces, catégorie…)",
    hide_today: "Masquer les événements du jour", hide_past: "Masquer les retraites passées", show_icon: "Emoji dans le titre",
    entity: "Événement", show_ring: "Anneau de progression", celebrate: "Animation festive le jour J 🎉",
    months: "Nombre de mois", layout: "Disposition", show_empty_months: "Afficher les mois sans événement",
    sort: "Tri", show_death_date: "Afficher la date de décès", show_age_at_death: "Afficher l'âge au décès",
    show_countdown: "Afficher le compte à rebours", flicker: "Bougie animée (douce)",
    show_category: "Afficher la catégorie d'âge", show_upcoming: "Afficher le prochain anniversaire",
    "entities.memorial": "Capteurs de mémoriaux", "entities.birthday": "Capteurs d'événements (anniversaires)",
    "types.auto": "Types d'événements (choix automatique)",
    h_entities: "Vide = détection automatique de tous les capteurs Souvenirs et Célébrations.",
    h_types: "Aucun type coché = tous les types.", h_unlimited: "0 = illimité", h_horizon: "0 = pas de limite",
    h_entity: "Vide = le prochain événement est choisi automatiquement.", h_title_auto: "Vide = « Prochain anniversaire », « Prochaine retraite »…",
    h_types_auto: "Pour le choix automatique. Aucun type coché = tous.", h_celebrate: "Confettis le jour J (désactivés si « réduire les animations » est actif).",
    h_memorial: "Seuls les capteurs de type mémorial sont affichés. Vide = détection automatique.",
    h_birthday: "Seuls les capteurs de type anniversaire sont pris en compte. Vide = détection automatique de tous les anniversaires.",
    unit_days: "jours", l_frise: "Frise verticale", l_grid: "Grille de mois", s_date: "Date la plus proche", s_name: "Nom",
    "card.informations": "Informations", "card.list": "Liste / Agenda", "card.countdown": "Compte à rebours",
    "card.timeline": "Frise des mois", "card.memorial": "Mémoriaux", brand: "Souvenirs et Célébrations",
    "desc.informations": "Anniversaire du jour, prochain anniversaire, âge et catégorie d'âge 🎂",
    "desc.list": "Tous les événements (anniversaires, mariages, mémoriaux, promotions, événements, retraites), triés, groupés, avec badge J-N 📋",
    "desc.countdown": "Le prochain événement en grand, anneau de progression et confettis le jour J ⏳",
    "desc.timeline": "Frise des 12 prochains mois avec les événements de chaque mois 📅",
    "desc.memorial": "Carte sobre en mémoire des disparus : âge qu'ils auraient eu, date de décès 🕯️",
  },
  en: {
    title: "Title", entities: "Sensors (manual selection)", types: "Event types shown",
    max_items: "Maximum number of events", horizon_days: "Horizon", group_by_type: "Group by type",
    compact: "Compact layout", show_date: "Show the date", show_details: "Show details (age, anniversary, category…)",
    hide_today: "Hide today's events", hide_past: "Hide past retirements", show_icon: "Emoji in the title",
    entity: "Event", show_ring: "Progress ring", celebrate: "Festive animation on the day 🎉",
    months: "Number of months", layout: "Layout", show_empty_months: "Show months without events",
    sort: "Sort", show_death_date: "Show date of death", show_age_at_death: "Show age at death",
    show_countdown: "Show countdown", flicker: "Animated candle (gentle)",
    show_category: "Show age category", show_upcoming: "Show next birthday",
    "entities.memorial": "Memorial sensors", "entities.birthday": "Event sensors (birthdays)",
    "types.auto": "Event types (automatic choice)",
    h_entities: "Empty = automatic detection of all Memories and Celebrations sensors.",
    h_types: "No type checked = all types.", h_unlimited: "0 = unlimited", h_horizon: "0 = no limit",
    h_entity: "Empty = the next event is picked automatically.", h_title_auto: "Empty = “Next birthday”, “Next retirement”…",
    h_types_auto: "For the automatic choice. No type checked = all.", h_celebrate: "Confetti on the day (disabled when “reduce motion” is on).",
    h_memorial: "Only memorial sensors are shown. Empty = automatic detection.",
    h_birthday: "Only birthday sensors are used. Empty = automatic detection of all birthdays.",
    unit_days: "days", l_frise: "Vertical timeline", l_grid: "Month grid", s_date: "Nearest date", s_name: "Name",
    "card.informations": "Information", "card.list": "List / Agenda", "card.countdown": "Countdown",
    "card.timeline": "Month timeline", "card.memorial": "Memorials", brand: "Memories and Celebrations",
    "desc.informations": "Today's birthday, next birthday, age and age category 🎂",
    "desc.list": "All events (birthdays, weddings, memorials, promotions, events, retirements), sorted, grouped, with a countdown badge 📋",
    "desc.countdown": "The next event in big, progress ring and confetti on the day ⏳",
    "desc.timeline": "Timeline of the next 12 months with each month's events 📅",
    "desc.memorial": "A sober card in memory of loved ones: the age they would have reached, date of death 🕯️",
  },
};

let _dcLang = null;
function _langOf(hass) {
  return String(hass?.locale?.language || hass?.language || "").toLowerCase();
}
function _setLang(hass) {
  const l = _langOf(hass);
  if (l) _dcLang = l;
}
function _lang() {
  if (!_dcLang) {
    const ha = document.querySelector("home-assistant");
    _dcLang = _langOf(ha?.hass) || String(navigator.language || "en").toLowerCase();
  }
  return _dcLang;
}
function _pick(table, lang = _lang()) {
  const base = lang.split("-")[0];
  return table[lang] ? lang : table[base] ? base : "en";
}
function _fill(str, vars) {
  return String(str).replace(/\{(\w+)\}/g, (_, k) => (vars && vars[k] !== undefined && vars[k] !== null ? vars[k] : ""));
}
// Texte de carte ; gender = "male" | "female" | autre (neutre)
function _t(key, vars, gender) {
  const L = DC_I18N[_pick(DC_I18N)];
  const suffix = gender === "male" ? "_m" : gender === "female" ? "_f" : "";
  const str = (suffix && L[key + suffix]) || L[key] || (suffix && DC_I18N.en[key + suffix]) || DC_I18N.en[key] || key;
  return _fill(str, vars);
}
function _te(key, vars) {
  const L = DC_EDITOR_I18N[_pick(DC_EDITOR_I18N)];
  return _fill(L[key] ?? DC_EDITOR_I18N.en[key] ?? key, vars);
}
const _years = (n) => _t(Math.abs(n) <= 1 ? "year_one" : "year_other", { n });
// Allemand : datif (« vor 8 Jahren »)
const _yearsDat = (n) => (_pick(DC_I18N) === "de" ? (Math.abs(n) <= 1 ? `${n} Jahr` : `${n} Jahren`) : _years(n));
const _yv = (n) => ({ y: _years(n), yd: _yearsDat(n), a: n });

/* ---------------------------------------------------------------------- */
/* Dates                                                                   */
/* ---------------------------------------------------------------------- */
const DC_MONTHS_FR = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août", "septembre", "octobre", "novembre", "décembre"];
const DC_WEEKDAYS_FR = ["dimanche", "lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi"];

// « 14 mars », « samedi 14 mars », « 1er mai 2027 » (fr) ; Intl pour les autres langues
function _fmtDate(date, { weekday = false, year = false } = {}) {
  if (!(date instanceof Date) || isNaN(date)) return "";
  const lang = _lang();
  if (_pick(DC_I18N) === "fr") {
    const d = date.getDate();
    let s = `${d === 1 ? "1er" : d} ${DC_MONTHS_FR[date.getMonth()]}`;
    if (weekday) s = `${DC_WEEKDAYS_FR[date.getDay()]} ${s}`;
    if (year) s += ` ${date.getFullYear()}`;
    return s;
  }
  const opts = { day: "numeric", month: "long" };
  if (weekday) opts.weekday = "long";
  if (year) opts.year = "numeric";
  try {
    return new Intl.DateTimeFormat(lang, opts).format(date);
  } catch (_e) {
    return date.toDateString();
  }
}
function _monthName(m, y) {
  if (_pick(DC_I18N) === "fr") return DC_MONTHS_FR[m];
  try {
    return new Intl.DateTimeFormat(_lang(), { month: "long" }).format(new Date(y, m, 1));
  } catch (_e) {
    return String(m + 1);
  }
}
const _dayNum = (d) => (_pick(DC_I18N) === "fr" && d === 1 ? "1er" : String(d));

// « 03/05/2014 » → « 3 mai 2014 »
function _fmtFrDate(str) {
  const m = /^(\d{1,2})\/(\d{1,2})\/(\d{4})$/.exec(String(str || "").trim());
  if (!m) return String(str || "");
  return _fmtDate(new Date(Number(m[3]), Number(m[2]) - 1, Number(m[1])), { year: true });
}

function _today() {
  const n = new Date();
  return new Date(n.getFullYear(), n.getMonth(), n.getDate());
}
function _addDays(days) {
  const t = _today();
  return new Date(t.getFullYear(), t.getMonth(), t.getDate() + days);
}

/* ---------------------------------------------------------------------- */
/* Capteurs                                                                */
/* ---------------------------------------------------------------------- */
const DC_TYPES = {
  birthday: { emoji: "🎂", color: "#e91e63" },
  anniversary: { emoji: "💍", color: "#9c27b0" },
  memorial: { emoji: "🕯️", color: "#78909c" },
  promotion: { emoji: "🏆", color: "#ff9800" },
  special_event: { emoji: "⭐", color: "#2196f3" },
  retirement: { emoji: "🏖️", color: "#009688" },
};
const DC_TYPE_ORDER = Object.keys(DC_TYPES);
const _typeOptions = () => DC_TYPE_ORDER.map((t) => ({ value: t, label: `${DC_TYPES[t].emoji} ${_t(`type.${t}`)}` }));

const _num = (v) => {
  if (v === null || v === undefined || v === "") return null;
  const n = Number(v);
  return Number.isFinite(n) ? n : null;
};

// Capteur fourni par l'intégration ? (registre des entités si dispo, sinon attribut event_type)
function _isDcSensor(hass, id) {
  if (!id.startsWith("sensor.")) return false;
  const type = hass.states[id]?.attributes?.event_type;
  if (!DC_TYPES[type]) return false;
  const ent = hass.entities?.[id];
  if (ent && ent.platform) return ent.platform === DC_DOMAIN;
  return true;
}
function _detectAll(hass, type) {
  return Object.keys(hass?.states || {})
    .filter((id) => _isDcSensor(hass, id))
    .filter((id) => !type || hass.states[id].attributes.event_type === type)
    .sort();
}

function _displayName(a, id) {
  if (a.first_name) return String(a.first_name);
  const fn = String(a.friendly_name || "");
  return fn ? fn.split(" - ")[0] : id;
}

function _parseEvent(hass, id) {
  const st = hass?.states?.[id];
  if (!st) return null;
  const a = st.attributes || {};
  const type = a.event_type;
  const days = parseInt(st.state, 10);
  if (!DC_TYPES[type] || !Number.isFinite(days) || days < 0) return null;
  const e = {
    id, type, days,
    date: _addDays(days),
    name: _displayName(a, id),
    full: String(a.friendly_name || "").split(" - ")[0] || _displayName(a, id),
    gender: a.gender || "unspecified",
    years: _num(a.years),
    category: a.age_category || null,
    wedding: a.wedding_type || null,
    deathDate: a.death_date || null,
    sinceDeath: _num(a.years_since_death),
    ageAtDeath: _num(a.age_at_death),
    worked: _num(a.years_worked),
    remaining: _num(a.years_remaining),
    retired: _num(a.years_retired),
    retirementDate: a.retirement_date || null,
    medal: a.work_medal || null,
    notif: a.notifications_enabled === true,
    past: false,
  };
  if (type === "retirement" && e.retired !== null) {
    // Retraite déjà passée (le capteur reste à 0). Jour J seulement si la date de départ est aujourd'hui.
    const rd = /^(\d{1,2})\/(\d{1,2})\/(\d{4})$/.exec(String(e.retirementDate || ""));
    const t = _today();
    const isToday = rd && Number(rd[1]) === t.getDate() && Number(rd[2]) === t.getMonth() + 1 && Number(rd[3]) === t.getFullYear();
    e.past = !isToday;
  }
  return e;
}

const _sortEvents = (a, b) => Number(a.past) - Number(b.past) || a.days - b.days || String(a.name).localeCompare(String(b.name), _lang());

// Détails sans le nom (listes)
function _details(e) {
  const out = [];
  const today = e.days === 0 && !e.past;
  const g = e.gender;
  switch (e.type) {
    case "birthday":
      if (e.years !== null) out.push(_t(today ? "turns_today" : "will_turn", { ..._yv(e.years), n: e.years }, g));
      if (e.category) out.push(e.category);
      break;
    case "anniversary":
      if (e.years !== null) out.push(_t("married", _yv(e.years)));
      if (e.wedding) out.push(e.wedding);
      break;
    case "memorial":
      if (e.years !== null) out.push(_t("would_have", { ..._yv(e.years), n: e.years }, g));
      if (e.sinceDeath !== null) out.push(_t("since_death", _yv(e.sinceDeath), g));
      break;
    case "promotion":
    case "special_event":
      if (e.years !== null && e.years > 0) out.push(_years(e.years));
      break;
    case "retirement":
      if (e.past) out.push(e.retired > 0 ? _t("retired_since", _yv(e.retired), g) : _t("retired_year", {}, g));
      else if (e.remaining !== null && !today) out.push(e.remaining > 0 ? _t("leaves_in", _yv(e.remaining), g) : _t("leaves_soon", {}, g));
      if (e.worked !== null) out.push(_t("career", _yv(e.worked)));
      if (e.medal) out.push(_t("medal", { m: e.medal }));
      break;
  }
  return out;
}

// Phrase avec le nom (carte compte à rebours)
function _sentence(e) {
  const today = e.days === 0 && !e.past;
  const g = e.gender;
  const v = (n) => ({ ..._yv(n), n: e.name });
  switch (e.type) {
    case "birthday":
      return e.years === null ? e.name : _t(today ? "s_turns_today" : "s_will_turn", v(e.years), g);
    case "anniversary":
      return e.years === null ? e.full : _t(today ? "s_married_today" : "s_married", { ..._yv(e.years), n: e.full });
    case "memorial":
      return e.years === null ? e.name : _t("s_would_have", v(e.years), g);
    case "retirement":
      if (e.past) return e.retired > 0 ? _t("s_retired_since", v(e.retired), g) : _t("s_retired", { n: e.name }, g);
      return _t(today ? "s_retires_today" : "s_retires", { n: e.name }, g);
    default:
      return e.years !== null && e.years > 0 ? `${e.name} · ${_years(e.years)}` : e.name;
  }
}

function _extras(e) {
  switch (e.type) {
    case "birthday":
      return e.category ? [e.category] : [];
    case "anniversary":
      return e.wedding ? [e.wedding] : [];
    case "memorial":
      return e.sinceDeath !== null ? [_t("since_death", _yv(e.sinceDeath), e.gender)] : [];
    case "retirement":
      return [e.worked !== null ? _t("career", _yv(e.worked)) : null, e.medal ? _t("medal", { m: e.medal }) : null].filter(Boolean);
    default:
      return [];
  }
}

function _badge(e, { long = false } = {}) {
  if (e.past) return { cls: "b-past", text: "✓" };
  if (e.days === 0) return { cls: "b-today", text: _t("today") };
  if (e.days === 1) return { cls: "b-week", text: _t("tomorrow") };
  const cls = e.days < 7 ? "b-week" : e.days < 30 ? "b-month" : "b-later";
  return { cls, text: _t(long ? "in_days" : "dminus", { d: e.days }) };
}

const _bell = (e) => (e.notif ? ` <span class="bell" title="${_esc(_t("notif_on"))}">🔔</span>` : "");

const DC_BASE_CSS = `
  :host { --dc-today: var(--dc-today-color, #e91e63); --dc-week: var(--warning-color, #ff9800); --dc-month: var(--info-color, #039be5); }
  ha-card { overflow: hidden; }
  .header { font-size: 1.3em; font-weight: 500; padding: 16px 16px 4px; color: var(--ha-card-header-color, var(--primary-text-color)); display: flex; align-items: center; gap: 8px; }
  .muted { color: var(--secondary-text-color); font-style: italic; padding: 8px 16px 16px; }
  .badge { flex: none; font-size: 0.8em; font-weight: 600; padding: 3px 9px; border-radius: 999px; white-space: nowrap;
    background: var(--secondary-background-color, rgba(127,127,127,.15)); color: var(--primary-text-color); }
  .badge.b-today { background: var(--dc-today); color: #fff; }
  .badge.b-week { background: var(--dc-week); color: #fff; }
  .badge.b-month { background: var(--dc-month); color: #fff; }
  .badge.b-past { background: transparent; color: var(--secondary-text-color); border: 1px solid var(--divider-color); }
  [data-entity] { cursor: pointer; }
  [data-entity]:focus-visible { outline: 2px solid var(--primary-color); outline-offset: -2px; }
  .bell { font-size: 0.85em; }
`;

/* ---------------------------------------------------------------------- */
/* Base commune                                                            */
/* ---------------------------------------------------------------------- */
class DateCountdownBaseCard extends HTMLElement {
  constructor() {
    super();
    this._config = {};
    this.attachShadow({ mode: "open" });
    this.shadowRoot.addEventListener("click", (ev) => this._onClick(ev));
    this.shadowRoot.addEventListener("keydown", (ev) => {
      if (ev.key === "Enter" || ev.key === " ") this._onClick(ev);
    });
  }

  static get defaults() {
    return {};
  }

  setConfig(config) {
    if (config && typeof config !== "object") throw new Error("Invalid configuration");
    this._config = { ...this.constructor.defaults, ...(config || {}) };
    this._key = null;
    this._render();
  }

  set hass(hass) {
    const prev = this._hass;
    this._hass = hass;
    _setLang(hass);
    const ids = this._entityIds();
    const key = `${_langOf(hass)}|${ids.join(",")}`;
    if (!prev || key !== this._key || ids.some((id) => prev.states[id] !== hass.states[id]) || !this.shadowRoot.innerHTML) {
      this._key = key;
      this._render();
    }
  }

  get hass() {
    return this._hass;
  }

  _entityIds() {
    if (!this._hass) return [];
    const conf = _asList(this._config.entities).map((e) => (typeof e === "string" ? e : e?.entity)).filter(Boolean);
    return conf.length ? conf : _detectAll(this._hass);
  }

  _typesFilter() {
    const t = _asList(this._config.types).filter((x) => DC_TYPES[x]);
    return t.length ? t : null;
  }

  _events() {
    const types = this._typesFilter();
    return this._entityIds()
      .map((id) => _parseEvent(this._hass, id))
      .filter(Boolean)
      .filter((e) => !types || types.includes(e.type))
      .sort(_sortEvents);
  }

  _onClick(ev) {
    const el = ev.composedPath().find((n) => n instanceof HTMLElement && n.dataset && n.dataset.entity);
    if (!el || this._config.tap_action === "none") return;
    ev.preventDefault();
    this.dispatchEvent(new CustomEvent("hass-more-info", { detail: { entityId: el.dataset.entity }, bubbles: true, composed: true }));
  }

  // title : undefined = titre par défaut traduit ; "" = pas d'en-tête
  _title(defaultKey) {
    const t = this._config.title;
    return t === undefined || t === null ? (defaultKey ? _t(defaultKey) : "") : String(t);
  }

  _header(defaultKey, emoji) {
    const t = this._title(defaultKey);
    if (!t) return "";
    return `<div class="header">${_esc(t)}${emoji && this._config.show_icon !== false ? ` <span aria-hidden="true">${emoji}</span>` : ""}</div>`;
  }

  _render() {
    if (!this.shadowRoot) return;
    if (!this._hass) {
      this.shadowRoot.innerHTML = "";
      return;
    }
    this.shadowRoot.innerHTML = `<style>${DC_BASE_CSS}${this._css()}</style>${this._build()}`;
  }

  _css() {
    return "";
  }

  _build() {
    return "";
  }
}

// Formulaire natif HA : retire les clés internes « _helper » et fournit libellés + aides traduits.
function _form(schema, labels = {}) {
  const helpers = {};
  const clean = (list) =>
    list.map((it) => {
      const { _helper, ...rest } = it;
      if (_helper && it.name) helpers[it.name] = _helper;
      if (rest.schema) rest.schema = clean(rest.schema);
      return rest;
    });
  return {
    schema: clean(schema),
    computeLabel: (s) => (labels[s.name] ? _te(labels[s.name]) : _te(s.name)),
    computeHelper: (s) => (helpers[s.name] ? _te(helpers[s.name]) : undefined),
  };
}
const _entitiesField = (helper = "h_entities") => ({
  name: "entities",
  selector: { entity: { multiple: true, filter: { domain: "sensor", integration: DC_DOMAIN } } },
  _helper: helper,
});
const _typesField = (helper = "h_types") => ({ name: "types", selector: { select: { multiple: true, mode: "list", options: _typeOptions() } }, _helper: helper });
const _grid = (schema) => ({ type: "grid", name: "", flatten: true, schema });
const _bool = (name, helper) => ({ name, selector: { boolean: {} }, ...(helper ? { _helper: helper } : {}) });

/* ---------------------------------------------------------------------- */
/* 0. Carte Informations                                                   */
/* ---------------------------------------------------------------------- */
class DateCountdownInformationsCard extends DateCountdownBaseCard {
  static get defaults() {
    return { show_icon: true, show_category: true, show_upcoming: true };
  }

  static getConfigForm() {
    return _form(
      [
        { name: "title", selector: { text: {} } },
        _entitiesField("h_birthday"),
        _grid([_bool("show_icon"), _bool("show_category"), _bool("show_upcoming")]),
      ],
      { entities: "entities.birthday" }
    );
  }

  static getStubConfig(hass) {
    _setLang(hass);
    const stub = { title: _t("info_title"), show_icon: true, show_category: true, show_upcoming: true };
    const found = _detectAll(hass, "birthday");
    if (found.length) stub.entities = found;
    return stub;
  }

  getCardSize() {
    return 3;
  }

  getGridOptions() {
    return { columns: 6, min_columns: 3, rows: "auto" };
  }

  _entityIds() {
    if (!this._hass) return [];
    const conf = _asList(this._config.entities).map((e) => (typeof e === "string" ? e : e?.entity)).filter(Boolean);
    return conf.length ? conf : _detectAll(this._hass, "birthday");
  }

  _typesFilter() {
    return ["birthday"];
  }

  _catLine(e, future) {
    if (!this._config.show_category || !e.category) return "";
    return `<div class="cat">${_t(future ? "info_cat_future" : "info_cat_now", { c: _esc(e.category) }, e.gender)}</div>`;
  }

  _build() {
    const cfg = this._config;
    const list = this._events();
    const today = list.filter((b) => b.days === 0);
    const next = list.filter((b) => b.days > 0);
    const yrs = (b) => _esc(_years(b.years));
    let body = "";
    if (today.length) {
      body += today
        .map(
          (b) => `<div class="block today">
            <div class="line">${_t("info_today", { n: _esc(b.name) })}</div>
            ${b.years != null ? `<div class="line">${_t("info_celebrates", { n: _esc(b.name), y: yrs(b) })}</div>` : ""}
            ${this._catLine(b, false)}
          </div>`
        )
        .join("");
    } else {
      body += `<div class="block"><div class="line">${_esc(_t("info_none_today"))}</div></div>`;
    }
    if (cfg.show_upcoming && next.length) {
      const d = next[0].days;
      const when = d === 1 ? _t("info_tomorrow") : _t("info_in_days", { d });
      body += `<div class="block"><div class="line">${_t("info_next", { when: _esc(when) })}</div>${next
        .filter((b) => b.days === d)
        .map(
          (b) => `${b.years != null ? `<div class="line">${_t("info_will", { n: _esc(b.name), y: yrs(b) })}</div>` : `<div class="line">${_esc(b.name)}</div>`}
            ${this._catLine(b, true)}`
        )
        .join("")}</div>`;
    } else if (!list.length) {
      body = `<div class="block muted">${_esc(_t("info_no_sensor"))}</div>`;
    }
    const t = this._title("info_title");
    const title = t ? `${_esc(t)}${cfg.show_icon ? " 🎂" : ""}` : cfg.show_icon ? "🎂" : "";
    return `<ha-card>${title ? `<div class="header">${title}</div>` : ""}${body}</ha-card>`;
  }

  _css() {
    return `ha-card { padding: 16px; } .header { padding: 0; margin-bottom: 8px; font-size: 1.4em; } .muted { padding: 0; }
        ha-card { padding: 16px; }
        .header { font-size: 1.4em; font-weight: 500; margin-bottom: 8px; color: var(--ha-card-header-color, var(--primary-text-color)); }
        .block { margin: 8px 0; line-height: 1.5; }
        .block + .block { border-top: 1px solid var(--divider-color); padding-top: 8px; }
        .today .line:first-child { color: var(--primary-color); font-size: 1.1em; }
        .cat { color: var(--secondary-text-color); }
        .muted { color: var(--secondary-text-color); font-style: italic; }
`;
  }
}

/* ---------------------------------------------------------------------- */
/* 1. Carte Liste / Agenda                                                 */
/* ---------------------------------------------------------------------- */
const LIST_TAG = "date-countdown-list-card";

class DateCountdownListCard extends DateCountdownBaseCard {
  static get defaults() {
    return {
      show_icon: true, group_by_type: true, max_items: 0, horizon_days: 0, hide_today: false,
      hide_past: false, compact: false, show_date: true, show_details: true,
    };
  }

  static getConfigForm() {
    return _form([
      { name: "title", selector: { text: {} } },
      _entitiesField(),
      _typesField(),
      _grid([
        { name: "max_items", selector: { number: { min: 0, max: 100, mode: "box" } }, _helper: "h_unlimited" },
        { name: "horizon_days", selector: { number: { min: 0, max: 366, mode: "box", unit_of_measurement: _te("unit_days") } }, _helper: "h_horizon" },
      ]),
      _grid([
        _bool("group_by_type"), _bool("compact"), _bool("show_date"), _bool("show_details"),
        _bool("hide_today"), _bool("hide_past"), _bool("show_icon"),
      ]),
    ]);
  }

  static getStubConfig(hass) {
    _setLang(hass);
    return { title: _t("list_title"), group_by_type: true, max_items: 8 };
  }

  getCardSize() {
    const n = this._lastCount ?? 3;
    return Math.max(2, 1 + Math.ceil(n * (this._config.compact ? 0.6 : 1)));
  }

  getGridOptions() {
    return { columns: 12, min_columns: 4, rows: "auto" };
  }

  _filtered() {
    const c = this._config;
    const horizon = Number(c.horizon_days) || 0;
    let list = this._events()
      .filter((e) => !(c.hide_today && e.days === 0 && !e.past))
      .filter((e) => !(c.hide_past && e.past))
      .filter((e) => !horizon || e.past || e.days <= horizon);
    const max = Number(c.max_items) || 0;
    if (max > 0) list = list.slice(0, max);
    return list;
  }

  _row(e) {
    const c = this._config;
    const b = _badge(e);
    const meta = [];
    if (c.show_date && !e.past) meta.push(_fmtDate(e.date, { weekday: !c.compact }));
    if (c.show_details) meta.push(..._details(e));
    return `<div class="row type-${e.type}${e.days === 0 && !e.past ? " is-today" : ""}" style="--dc-color:${DC_TYPES[e.type].color}"
        data-entity="${_esc(e.id)}" role="button" tabindex="0" aria-label="${_esc(`${_t(`one.${e.type}`)} — ${e.full}`)}">
      <div class="ico" aria-hidden="true">${DC_TYPES[e.type].emoji}</div>
      <div class="txt">
        <div class="name">${_esc(e.full)}${_bell(e)}</div>
        ${meta.length ? `<div class="meta">${meta.map(_esc).join(" · ")}</div>` : ""}
      </div>
      <span class="badge ${b.cls}">${_esc(b.text)}</span>
    </div>`;
  }

  _build() {
    const list = this._filtered();
    this._lastCount = list.length;
    let body;
    if (!list.length) {
      body = `<div class="muted">${_esc(_t("no_events"))}</div>`;
    } else if (this._config.group_by_type) {
      body = DC_TYPE_ORDER.filter((t) => list.some((e) => e.type === t))
        .map((t) => {
          const items = list.filter((e) => e.type === t);
          return `<div class="section"><div class="sec-title" style="--dc-color:${DC_TYPES[t].color}">${DC_TYPES[t].emoji} ${_esc(_t(`type.${t}`))} <span class="count">${items.length}</span></div>${items.map((e) => this._row(e)).join("")}</div>`;
        })
        .join("");
    } else {
      body = `<div class="section">${list.map((e) => this._row(e)).join("")}</div>`;
    }
    return `<ha-card class="${this._config.compact ? "compact" : ""}">${this._header("list_title", "🎉")}<div class="content">${body}</div></ha-card>`;
  }

  _css() {
    return `
      .content { padding: 4px 0 8px; }
      .section + .section { margin-top: 4px; }
      .sec-title { font-size: .8em; font-weight: 600; text-transform: uppercase; letter-spacing: .06em; color: var(--secondary-text-color);
        padding: 10px 16px 4px; display: flex; align-items: center; gap: 6px; }
      .sec-title .count { font-weight: 500; background: var(--secondary-background-color, rgba(127,127,127,.15)); border-radius: 999px; padding: 0 7px; }
      .row { display: flex; align-items: center; gap: 12px; padding: 8px 16px; border-radius: 0; transition: background .15s; }
      .row:hover { background: var(--secondary-background-color, rgba(127,127,127,.08)); }
      .ico { flex: none; width: 38px; height: 38px; border-radius: 50%; display: grid; place-items: center; font-size: 1.25em;
        background: color-mix(in srgb, var(--dc-color) 18%, transparent); box-shadow: inset 0 0 0 2px color-mix(in srgb, var(--dc-color) 45%, transparent); }
      .txt { flex: 1; min-width: 0; }
      .name { font-weight: 500; color: var(--primary-text-color); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
      .meta { font-size: .86em; color: var(--secondary-text-color); margin-top: 1px; }
      .row.is-today .name { color: var(--dc-today); }
      .row.type-memorial .ico { filter: grayscale(.3); }
      .compact .row { padding: 4px 16px; gap: 10px; }
      .compact .ico { width: 28px; height: 28px; font-size: 1em; }
      .compact .meta { white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
    `;
  }
}

/* ---------------------------------------------------------------------- */
/* 2. Carte Compte à rebours / Héros                                       */
/* ---------------------------------------------------------------------- */
const COUNTDOWN_TAG = "date-countdown-countdown-card";
const CONFETTI_COLORS = ["#e91e63", "#ffc107", "#03a9f4", "#8bc34a", "#9c27b0", "#ff5722"];

class DateCountdownCountdownCard extends DateCountdownBaseCard {
  static get defaults() {
    return { show_ring: true, show_date: true, show_details: true, celebrate: true };
  }

  static getConfigForm() {
    return _form(
      [
        { name: "entity", selector: { entity: { filter: { domain: "sensor", integration: DC_DOMAIN } } }, _helper: "h_entity" },
        { name: "title", selector: { text: {} }, _helper: "h_title_auto" },
        _typesField("h_types_auto"),
        _grid([_bool("show_ring"), _bool("show_date"), _bool("show_details"), _bool("celebrate", "h_celebrate")]),
      ],
      { types: "types.auto" }
    );
  }

  static getStubConfig() {
    return { show_ring: true, celebrate: true };
  }

  getCardSize() {
    return 3;
  }

  getGridOptions() {
    return { columns: 6, min_columns: 4, rows: "auto" };
  }

  _entityIds() {
    if (!this._hass) return [];
    if (this._config.entity) return [this._config.entity];
    return super._entityIds();
  }

  _pick() {
    const list = this._events();
    if (this._config.entity) return list[0] || null;
    return list.find((e) => !e.past) || null;
  }

  _progress(e) {
    if (e.type === "retirement") {
      if (e.past || e.days === 0) return 1;
      const w = e.worked ?? 0;
      const r = e.remaining ?? 0;
      return w + r > 0 ? w / (w + r) : 0;
    }
    if (e.days === 0) return 1;
    return Math.min(1, Math.max(0, (365 - e.days) / 365));
  }

  _confetti() {
    let s = "";
    for (let i = 0; i < 22; i++) {
      const x = (i * 37 + 11) % 100;
      const delay = ((i * 0.53) % 4).toFixed(2);
      const dur = (3.2 + ((i * 7) % 10) / 6).toFixed(2);
      const rot = (i * 47) % 360;
      const c = CONFETTI_COLORS[i % CONFETTI_COLORS.length];
      s += `<i style="left:${x}%;--d:${delay}s;--t:${dur}s;--r:${rot}deg;background:${c}${i % 3 === 0 ? ";border-radius:50%" : ""}"></i>`;
    }
    return `<div class="confetti" aria-hidden="true">${s}</div>`;
  }

  _build() {
    const c = this._config;
    const e = this._pick();
    if (!e) {
      const t = this._title();
      return `<ha-card>${t ? `<div class="header">${_esc(t)}</div>` : ""}<div class="muted">${_esc(_t("no_upcoming"))}</div></ha-card>`;
    }
    const T = DC_TYPES[e.type];
    const today = e.days === 0 && !e.past;
    const festive = today && e.type !== "memorial";
    const R = 52;
    const C = 2 * Math.PI * R;
    const p = this._progress(e);
    const label = this._title() || _t(today ? `one.${e.type}` : `next.${e.type}`);
    const sub = [_sentence(e), ...(c.show_details ? _extras(e) : [])];
    const center = e.past
      ? `<div class="big small">✓</div><div class="unit">${_esc(_t("retired_badge", {}, e.gender))}</div>`
      : today
        ? `<div class="big emoji">${festive ? "🎉" : T.emoji}</div><div class="unit">${_esc(_t("day_j"))}</div>`
        : `<div class="big">${e.days}</div><div class="unit">${_esc(_t(e.days === 1 ? "day_one" : "day_other"))}</div>`;
    const ring = c.show_ring
      ? `<svg viewBox="0 0 120 120" class="ring" aria-hidden="true">
          <circle cx="60" cy="60" r="${R}" class="track"/>
          <circle cx="60" cy="60" r="${R}" class="bar" stroke-dasharray="${C.toFixed(2)}" stroke-dashoffset="${(C * (1 - p)).toFixed(2)}"/>
        </svg>`
      : "";
    const dateLine =
      c.show_date && !e.past
        ? `<div class="date">${_esc(today ? _t("is_today") : _t("on_date", { date: _fmtDate(e.date, { weekday: true, year: e.date.getFullYear() !== _today().getFullYear() }) }))}</div>`
        : "";
    return `<ha-card class="${festive ? "festive" : ""} ${e.type === "memorial" ? "sober" : ""}" style="--dc-color:${T.color}">
      ${festive && c.celebrate ? this._confetti() : ""}
      <div class="hero" data-entity="${_esc(e.id)}" role="button" tabindex="0" aria-label="${_esc(`${label} — ${_sentence(e)}`)}">
        <div class="dial ${c.show_ring ? "" : "noring"}">${ring}<div class="center">${center}</div></div>
        <div class="info">
          <div class="label"><span class="emoji-s" aria-hidden="true">${T.emoji}</span> ${_esc(label)}${_bell(e)}</div>
          <div class="who">${_esc(e.full)}</div>
          <div class="sub">${sub.map((s, i) => (i === 0 ? `<b>${_esc(s)}</b>` : _esc(s))).join(" · ")}</div>
          ${dateLine}
        </div>
      </div>
    </ha-card>`;
  }

  _css() {
    return `
      ha-card { position: relative; }
      .hero { display: flex; align-items: center; gap: 18px; padding: 18px; position: relative; z-index: 1; }
      .dial { position: relative; flex: none; width: 116px; height: 116px; }
      .dial.noring { width: 96px; height: 96px; border-radius: 50%; background: color-mix(in srgb, var(--dc-color) 14%, transparent); }
      .ring { width: 100%; height: 100%; transform: rotate(-90deg); }
      .ring circle { fill: none; stroke-width: 9; }
      .ring .track { stroke: var(--divider-color, rgba(127,127,127,.25)); opacity: .6; }
      .ring .bar { stroke: var(--dc-color); stroke-linecap: round; transition: stroke-dashoffset .8s ease; }
      .center { position: absolute; inset: 0; display: flex; flex-direction: column; align-items: center; justify-content: center; }
      .big { font-size: 2.6em; font-weight: 700; line-height: 1; color: var(--primary-text-color); font-variant-numeric: tabular-nums; }
      .big.emoji { font-size: 2.3em; }
      .big.small { font-size: 2em; color: var(--dc-color); }
      .unit { font-size: .8em; color: var(--secondary-text-color); text-transform: uppercase; letter-spacing: .08em; margin-top: 2px; }
      .info { min-width: 0; flex: 1; }
      .label { font-size: .82em; font-weight: 600; text-transform: uppercase; letter-spacing: .06em; color: var(--dc-color); }
      .who { font-size: 1.5em; font-weight: 600; line-height: 1.25; margin: 2px 0 4px; color: var(--primary-text-color); }
      .sub { color: var(--primary-text-color); line-height: 1.4; }
      .sub b { font-weight: 500; }
      .date { margin-top: 6px; font-size: .9em; color: var(--secondary-text-color); }
      .festive { background: linear-gradient(135deg, color-mix(in srgb, var(--dc-color) 16%, var(--ha-card-background, var(--card-background-color, #fff))), var(--ha-card-background, var(--card-background-color, #fff)) 70%); }
      .festive .big.emoji { animation: pop 1.6s ease-in-out infinite; }
      .sober .who { font-weight: 500; }
      @keyframes pop { 0%, 100% { transform: scale(1); } 50% { transform: scale(1.15) rotate(-6deg); } }
      .confetti { position: absolute; inset: 0; pointer-events: none; overflow: hidden; z-index: 0; }
      .confetti i { position: absolute; top: -12px; width: 7px; height: 11px; opacity: .85; border-radius: 1px;
        transform: rotate(var(--r)); animation: fall var(--t) linear var(--d) infinite; }
      @keyframes fall { 0% { transform: translateY(-10px) rotate(var(--r)); opacity: 0; } 10% { opacity: .9; }
        100% { transform: translateY(240px) rotate(calc(var(--r) + 540deg)); opacity: 0; } }
      @media (prefers-reduced-motion: reduce) { .confetti { display: none; } .festive .big.emoji { animation: none; } .ring .bar { transition: none; } }
      @media (max-width: 380px) { .dial { width: 96px; height: 96px; } .big { font-size: 2.1em; } .who { font-size: 1.25em; } }
    `;
  }
}

/* ---------------------------------------------------------------------- */
/* 3. Carte Frise / Calendrier                                             */
/* ---------------------------------------------------------------------- */
const TIMELINE_TAG = "date-countdown-timeline-card";

class DateCountdownTimelineCard extends DateCountdownBaseCard {
  static get defaults() {
    return { show_icon: true, months: 12, layout: "frise", show_empty_months: true, show_details: true };
  }

  static getConfigForm() {
    return _form([
      { name: "title", selector: { text: {} } },
      _entitiesField(),
      _typesField(),
      _grid([
        { name: "months", selector: { number: { min: 1, max: 12, mode: "slider" } } },
        {
          name: "layout",
          selector: { select: { mode: "dropdown", options: [{ value: "frise", label: _te("l_frise") }, { value: "grid", label: _te("l_grid") }] } },
        },
        _bool("show_empty_months"),
        _bool("show_details"),
      ]),
    ]);
  }

  static getStubConfig(hass) {
    _setLang(hass);
    return { title: _t("timeline_title"), months: 12, layout: "frise" };
  }

  getCardSize() {
    return Math.max(3, Math.ceil((this._lastMonths ?? 6) * (this._config.layout === "grid" ? 0.7 : 1.2)));
  }

  getGridOptions() {
    return { columns: 12, min_columns: 4, rows: "auto" };
  }

  _build() {
    const c = this._config;
    const months = Math.min(12, Math.max(1, parseInt(c.months, 10) || 12));
    const t = _today();
    const buckets = [];
    for (let i = 0; i < months; i++) {
      const d = new Date(t.getFullYear(), t.getMonth() + i, 1);
      buckets.push({ y: d.getFullYear(), m: d.getMonth(), items: [], current: i === 0 });
    }
    for (const e of this._events()) {
      if (e.past) continue;
      const idx = (e.date.getFullYear() - t.getFullYear()) * 12 + e.date.getMonth() - t.getMonth();
      if (idx >= 0 && idx < months) buckets[idx].items.push(e);
    }
    const shown = c.show_empty_months ? buckets : buckets.filter((b) => b.items.length);
    this._lastMonths = shown.length;
    const total = buckets.reduce((n, b) => n + b.items.length, 0);
    const chip = (e) => {
      const det = c.show_details ? _details(e).slice(0, 1) : [];
      const b = _badge(e);
      return `<div class="chip${e.days === 0 ? " is-today" : ""}" style="--dc-color:${DC_TYPES[e.type].color}" data-entity="${_esc(e.id)}" role="button" tabindex="0"
          title="${_esc(`${_t(`one.${e.type}`)} — ${e.full} — ${_fmtDate(e.date, { weekday: true })}`)}">
        <span class="day">${_esc(_dayNum(e.date.getDate()))}</span>
        <span class="dot" aria-hidden="true"></span>
        <span class="em" aria-hidden="true">${DC_TYPES[e.type].emoji}</span>
        <span class="nm">${_esc(e.full)}${det.length ? ` <small>${_esc(det[0])}</small>` : ""}</span>
        ${e.days < 30 ? `<span class="badge ${b.cls}">${_esc(b.text)}</span>` : ""}
      </div>`;
    };
    const month = (bk) => `<div class="month${bk.current ? " current" : ""}${bk.items.length ? "" : " empty"}">
        <div class="mlabel"><span class="mdot" aria-hidden="true"></span>${_esc(_monthName(bk.m, bk.y))}${bk.y !== t.getFullYear() ? ` <span class="yr">${bk.y}</span>` : ""}
          ${bk.items.length ? `<span class="count">${bk.items.length}</span>` : ""}</div>
        <div class="items">${bk.items.length ? bk.items.map(chip).join("") : `<div class="none">—</div>`}</div>
      </div>`;
    const legend = DC_TYPE_ORDER.filter((ty) => buckets.some((b) => b.items.some((e) => e.type === ty)))
      .map((ty) => `<span class="lg" style="--dc-color:${DC_TYPES[ty].color}"><span class="dot"></span>${_esc(_t(`type.${ty}`))}</span>`)
      .join("");
    const body = total
      ? `<div class="${c.layout === "grid" ? "grid" : "frise"}">${shown.map(month).join("")}</div>${legend ? `<div class="legend">${legend}</div>` : ""}`
      : `<div class="muted">${_esc(_t("no_months", { m: months }))}</div>`;
    return `<ha-card>${this._header("timeline_title", "📅")}<div class="content">${body}</div></ha-card>`;
  }

  _css() {
    return `
      .content { padding: 8px 16px 14px; }
      .frise { position: relative; padding-left: 18px; }
      .frise::before { content: ""; position: absolute; left: 5px; top: 8px; bottom: 8px; width: 2px; background: var(--divider-color, rgba(127,127,127,.3)); }
      .frise .month { position: relative; padding: 4px 0 8px; }
      .frise .mdot { position: absolute; left: -18px; top: 9px; width: 12px; height: 12px; border-radius: 50%; background: var(--card-background-color, #fff);
        box-shadow: inset 0 0 0 2px var(--secondary-text-color); }
      .frise .month.current .mdot { box-shadow: none; background: var(--primary-color); }
      .frise .month.empty .mlabel { opacity: .55; }
      .mlabel { font-weight: 600; text-transform: capitalize; color: var(--primary-text-color); display: flex; align-items: center; gap: 6px; padding: 4px 0; }
      .month.current .mlabel { color: var(--primary-color); }
      .yr { font-weight: 400; color: var(--secondary-text-color); }
      .count { font-size: .75em; font-weight: 600; background: var(--secondary-background-color, rgba(127,127,127,.15)); border-radius: 999px; padding: 0 7px; color: var(--secondary-text-color); }
      .items { display: flex; flex-direction: column; gap: 4px; }
      .none { color: var(--secondary-text-color); opacity: .5; font-size: .85em; padding-left: 2px; }
      .chip { display: flex; align-items: center; gap: 8px; padding: 5px 10px; border-radius: 10px; min-width: 0;
        background: color-mix(in srgb, var(--dc-color) 10%, transparent); border-left: 3px solid var(--dc-color); }
      .chip:hover { background: color-mix(in srgb, var(--dc-color) 18%, transparent); }
      .chip .day { font-weight: 700; min-width: 2.1em; color: var(--dc-color); font-variant-numeric: tabular-nums; }
      .chip .dot { display: none; }
      .chip .nm { flex: 1; min-width: 0; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; color: var(--primary-text-color); }
      .chip small { color: var(--secondary-text-color); }
      .chip.is-today { box-shadow: 0 0 0 1px var(--dc-today); }
      .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(190px, 1fr)); gap: 10px; }
      .grid .month { border: 1px solid var(--divider-color, rgba(127,127,127,.25)); border-radius: 12px; padding: 6px 10px 10px; }
      .grid .month.current { border-color: var(--primary-color); }
      .grid .mdot { display: none; }
      .grid .month.empty { opacity: .6; }
      .legend { display: flex; flex-wrap: wrap; gap: 6px 14px; margin-top: 10px; font-size: .8em; color: var(--secondary-text-color); }
      .lg { display: inline-flex; align-items: center; gap: 5px; }
      .lg .dot { width: 9px; height: 9px; border-radius: 50%; background: var(--dc-color); }
    `;
  }
}

/* ---------------------------------------------------------------------- */
/* 4. Carte Mémoriaux                                                      */
/* ---------------------------------------------------------------------- */
const MEMORIAL_TAG = "date-countdown-memorial-card";

class DateCountdownMemorialCard extends DateCountdownBaseCard {
  static get defaults() {
    return { show_icon: true, max_items: 0, sort: "date", show_death_date: true, show_age_at_death: true, show_countdown: true, flicker: true };
  }

  static getConfigForm() {
    return _form(
      [
        { name: "title", selector: { text: {} } },
        _entitiesField("h_memorial"),
        _grid([
          { name: "max_items", selector: { number: { min: 0, max: 50, mode: "box" } }, _helper: "h_unlimited" },
          {
            name: "sort",
            selector: { select: { mode: "dropdown", options: [{ value: "date", label: _te("s_date") }, { value: "name", label: _te("s_name") }] } },
          },
          _bool("show_death_date"), _bool("show_age_at_death"), _bool("show_countdown"), _bool("flicker"), _bool("show_icon"),
        ]),
      ],
      { entities: "entities.memorial" }
    );
  }

  static getStubConfig(hass) {
    _setLang(hass);
    return { title: _t("memorial_title") };
  }

  getCardSize() {
    return Math.max(2, 1 + (this._lastCount ?? 2) * 1.2);
  }

  getGridOptions() {
    return { columns: 6, min_columns: 4, rows: "auto" };
  }

  _typesFilter() {
    return ["memorial"];
  }

  _build() {
    const c = this._config;
    let list = this._events();
    if (c.sort === "name") list = list.sort((a, b) => String(a.full).localeCompare(String(b.full), _lang()));
    const max = Number(c.max_items) || 0;
    if (max > 0) list = list.slice(0, max);
    this._lastCount = list.length;
    const row = (e) => {
      const lines = [];
      if (e.years !== null) {
        const v = { y: _esc(_years(e.years)), a: e.years, date: _esc(_fmtDate(e.date)) };
        lines.push(_t(e.days === 0 ? "m_would_have_today" : "m_would_have", v, e.gender));
      }
      const death = [];
      if (e.sinceDeath !== null) death.push(_esc(_t("since_death", _yv(e.sinceDeath), e.gender)));
      if (c.show_death_date && e.deathDate) death.push(`† ${_esc(_fmtFrDate(e.deathDate))}`);
      if (c.show_age_at_death && e.ageAtDeath !== null) death.push(_esc(_t("at_age", _yv(e.ageAtDeath))));
      const b = _badge(e, { long: true });
      return `<div class="row${e.days === 0 ? " is-today" : ""}" data-entity="${_esc(e.id)}" role="button" tabindex="0">
        <div class="candle" aria-hidden="true"><span class="flame"></span><span class="wax"></span></div>
        <div class="txt">
          <div class="name">${_esc(e.full)}${_bell(e)}</div>
          ${lines.map((l) => `<div class="line">${l}</div>`).join("")}
          ${death.length ? `<div class="line death">${death.join(" · ")}</div>` : ""}
        </div>
        ${c.show_countdown ? `<span class="badge soft">${_esc(e.days === 0 ? _t("today_plain") : b.text)}</span>` : ""}
      </div>`;
    };
    const body = list.length ? list.map(row).join("") : `<div class="muted">${_esc(_t("no_memorial"))}</div>`;
    return `<ha-card class="${c.flicker ? "flicker" : ""}">${this._header("memorial_title", "🕯️")}<div class="content">${body}</div></ha-card>`;
  }

  _css() {
    return `
      .header { font-weight: 400; letter-spacing: .02em; }
      .content { padding: 4px 0 10px; }
      .row { display: flex; align-items: center; gap: 14px; padding: 10px 16px; }
      .row + .row { border-top: 1px solid var(--divider-color, rgba(127,127,127,.2)); }
      .row:hover { background: var(--secondary-background-color, rgba(127,127,127,.06)); }
      .candle { flex: none; position: relative; width: 22px; height: 44px; }
      .wax { position: absolute; bottom: 0; left: 5px; width: 12px; height: 26px; border-radius: 3px 3px 2px 2px;
        background: linear-gradient(90deg, #e8e2d6, #fbf8f1 45%, #d9d2c3); }
      .flame { position: absolute; bottom: 26px; left: 6px; width: 10px; height: 16px; border-radius: 50% 50% 50% 50% / 60% 60% 40% 40%;
        background: radial-gradient(ellipse at 50% 70%, #fff6c7 0%, #ffc94d 45%, #ff8a1f 80%, transparent 100%);
        box-shadow: 0 0 10px 3px rgba(255, 180, 60, .35); transform-origin: 50% 100%; }
      .flicker .flame { animation: flick 2.8s ease-in-out infinite; }
      @keyframes flick { 0%, 100% { transform: scale(1) rotate(-1deg); opacity: .95; } 30% { transform: scale(.94, 1.04) rotate(2deg); } 60% { transform: scale(1.03, .96) rotate(-2deg); opacity: .85; } }
      @media (prefers-reduced-motion: reduce) { .flicker .flame { animation: none; } }
      .txt { flex: 1; min-width: 0; }
      .name { font-size: 1.05em; font-weight: 500; color: var(--primary-text-color); }
      .line { font-size: .88em; color: var(--secondary-text-color); line-height: 1.45; }
      .line b { color: var(--primary-text-color); font-weight: 500; }
      .death { font-style: italic; }
      .badge.soft { background: transparent; border: 1px solid var(--divider-color, rgba(127,127,127,.3)); color: var(--secondary-text-color); font-weight: 500; }
      .row.is-today .badge.soft { border-color: var(--secondary-text-color); color: var(--primary-text-color); }
    `;
  }
}

/* ---------------------------------------------------------------------- */
/* Enregistrement                                                          */
/* ---------------------------------------------------------------------- */
const DC_CARDS = [
  { tag: CARD_TAG, cls: DateCountdownInformationsCard, key: "informations" },
  { tag: LIST_TAG, cls: DateCountdownListCard, key: "list" },
  { tag: COUNTDOWN_TAG, cls: DateCountdownCountdownCard, key: "countdown" },
  { tag: TIMELINE_TAG, cls: DateCountdownTimelineCard, key: "timeline" },
  { tag: MEMORIAL_TAG, cls: DateCountdownMemorialCard, key: "memorial" },
];

window.customCards = window.customCards || [];
for (const card of DC_CARDS) {
  if (!customElements.get(card.tag)) customElements.define(card.tag, card.cls);
  if (!window.customCards.some((c) => c.type === card.tag)) {
    window.customCards.push({
      type: card.tag,
      name: `${_te("brand")} — ${_te(`card.${card.key}`)}`,
      description: _te(`desc.${card.key}`),
      preview: true,
      documentationURL: DC_DOC,
    });
  }
}
console.info(`%c SOUVENIRS-ET-CELEBRATIONS-CARDS %c ${CARD_VERSION} `, "color:white;background:#e91e63;font-weight:700", "color:#e91e63");
