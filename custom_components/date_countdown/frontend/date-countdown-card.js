/*
 * Carte Lovelace « Informations » 🎂 — Souvenirs et Célébrations (date_countdown)
 * Servie et enregistrée automatiquement par l'intégration.
 */
const CARD_TAG = "date-countdown-informations-card";
const CARD_VERSION = "1.2.18";

const _asList = (v) => (Array.isArray(v) ? v : v ? [v] : []);
const _esc = (s) =>
  String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c]);

const _isBirthday = (st) => st && st.attributes && st.attributes.event_type === "birthday";

// Capteurs date_countdown : attribut event_type présent et état numérique.
function _detect(hass, onlyBirthdays = true) {
  return Object.keys(hass?.states || {})
    .filter((id) => id.startsWith("sensor."))
    .filter((id) => {
      const st = hass.states[id];
      const type = st.attributes?.event_type;
      if (!type) return false;
      return onlyBirthdays ? type === "birthday" : true;
    })
    .sort();
}

// Accord neutre « un(e) », comme dans le rendu attendu (catégories mixtes).
function _article(_category) {
  return "un(e)";
}

const _days = (n) => (n === 1 ? "demain" : `dans ${n} jours`);

class DateCountdownInformationsCard extends HTMLElement {
  constructor() {
    super();
    this._config = {};
    this.attachShadow({ mode: "open" });
  }

  static getConfigForm() {
    return {
      schema: [
        { name: "title", selector: { text: {} } },
        { name: "entities", selector: { entity: { multiple: true, filter: { domain: "sensor", integration: "date_countdown" } } } },
        {
          type: "grid",
          name: "",
          flatten: true,
          schema: [
            { name: "show_icon", default: true, selector: { boolean: {} } },
            { name: "show_category", default: true, selector: { boolean: {} } },
            { name: "show_upcoming", default: true, selector: { boolean: {} } },
          ],
        },
      ],
      computeLabel: (s) =>
        ({
          title: "Titre",
          entities: "Capteurs d'événements (anniversaires)",
          show_icon: "Afficher l'emoji 🎂",
          show_category: "Afficher la catégorie d'âge",
          show_upcoming: "Afficher le prochain anniversaire",
        })[s.name],
      computeHelper: (s) =>
        s.name === "entities"
          ? "Seuls les capteurs de type anniversaire sont pris en compte. Vide = détection automatique de tous les anniversaires."
          : undefined,
    };
  }

  static getStubConfig(hass) {
    const stub = { title: "Informations", show_icon: true, show_category: true, show_upcoming: true };
    const found = _detect(hass);
    if (found.length) stub.entities = found;
    return stub;
  }

  setConfig(config) {
    this._config = { title: "Informations", show_icon: true, show_category: true, show_upcoming: true, ...(config || {}) };
    this._render();
  }

  set hass(hass) {
    const prev = this._hass;
    this._hass = hass;
    const ids = this._entityIds();
    if (!prev || ids.some((id) => prev.states[id] !== hass.states[id]) || !this.shadowRoot.innerHTML) this._render();
  }

  getCardSize() {
    return 3;
  }

  getGridOptions() {
    return { columns: 6, min_columns: 3, rows: "auto" };
  }

  _entityIds() {
    const conf = _asList(this._config.entities).map((e) => (typeof e === "string" ? e : e?.entity)).filter(Boolean);
    return conf.length ? conf : _detect(this._hass);
  }

  _birthdays() {
    const hass = this._hass;
    if (!hass) return [];
    return this._entityIds()
      .map((id) => hass.states[id])
      .filter(_isBirthday)
      .map((st) => ({
        id: st.entity_id,
        days: parseInt(st.state, 10),
        name: st.attributes.first_name || st.attributes.friendly_name || st.entity_id,
        years: st.attributes.years,
        category: st.attributes.age_category,
      }))
      .filter((b) => Number.isFinite(b.days) && b.days >= 0)
      .sort((a, b) => a.days - b.days || String(a.name).localeCompare(b.name));
  }

  _categoryLine(b, future) {
    if (!this._config.show_category || !b.category) return "";
    const verb = future ? "et sera" : "et devient";
    return `<div class="cat">${verb} ${_article(b.category)} <b>${_esc(b.category)}</b> !</div>`;
  }

  _render() {
    if (!this.shadowRoot) return;
    const cfg = this._config;
    const list = this._birthdays();
    const today = list.filter((b) => b.days === 0);
    const next = list.filter((b) => b.days > 0);
    let body = "";

    if (today.length) {
      body += today
        .map(
          (b) => `<div class="block today">
            <div class="line">🎉 Aujourd'hui, c'est l'anniversaire de <b>${_esc(b.name)}</b> !</div>
            ${b.years != null ? `<div class="line">${_esc(b.name)} fête ses <b>${_esc(b.years)} ans</b></div>` : ""}
            ${this._categoryLine(b, false)}
          </div>`
        )
        .join("");
    } else {
      body += `<div class="block"><div class="line">Aujourd'hui, pas d'anniversaire.</div></div>`;
    }

    if (cfg.show_upcoming && next.length) {
      const d = next[0].days;
      const group = next.filter((b) => b.days === d);
      body += `<div class="block"><div class="line">Le prochain anniversaire est <b>${_days(d)}</b></div>${group
        .map(
          (b) => `${b.years != null ? `<div class="line">${_esc(b.name)} aura <b>${_esc(b.years)} ans</b></div>` : `<div class="line">${_esc(b.name)}</div>`}
            ${this._categoryLine(b, true)}`
        )
        .join("")}</div>`;
    } else if (!list.length) {
      body = `<div class="block muted">Aucun capteur d'anniversaire trouvé. Choisis des capteurs dans l'éditeur de la carte.</div>`;
    }

    const title = cfg.title ? `${_esc(cfg.title)}${cfg.show_icon ? " 🎂" : ""}` : cfg.show_icon ? "🎂" : "";
    this.shadowRoot.innerHTML = `
      <style>
        ha-card { padding: 16px; }
        .header { font-size: 1.4em; font-weight: 500; margin-bottom: 8px; color: var(--ha-card-header-color, var(--primary-text-color)); }
        .block { margin: 8px 0; line-height: 1.5; }
        .block + .block { border-top: 1px solid var(--divider-color); padding-top: 8px; }
        .today .line:first-child { color: var(--primary-color); font-size: 1.1em; }
        .cat { color: var(--secondary-text-color); }
        .muted { color: var(--secondary-text-color); font-style: italic; }
      </style>
      <ha-card>
        ${title ? `<div class="header">${title}</div>` : ""}
        ${body}
      </ha-card>`;
  }
}


/* ======================================================================
 * Cartes supplémentaires : Liste / Agenda, Compte à rebours, Frise, Mémoriaux
 * Vanilla JS + shadow DOM, aucune dépendance externe.
 * ==================================================================== */

const DC_DOMAIN = "date_countdown";
const DC_DOC = "https://github.com/XAV59213/date_countdown#-cartes-lovelace";

const DC_TYPES = {
  birthday: { label: "Anniversaires", one: "Anniversaire", next: "Prochain anniversaire", emoji: "🎂", color: "#e91e63" },
  anniversary: { label: "Mariages", one: "Anniversaire de mariage", next: "Prochain anniversaire de mariage", emoji: "💍", color: "#9c27b0" },
  memorial: { label: "Mémoriaux", one: "Mémorial", next: "Prochain souvenir", emoji: "🕯️", color: "#78909c" },
  promotion: { label: "Promotions", one: "Promotion", next: "Prochaine promotion", emoji: "🏆", color: "#ff9800" },
  special_event: { label: "Événements", one: "Événement spécial", next: "Prochain événement", emoji: "⭐", color: "#2196f3" },
  retirement: { label: "Retraites", one: "Retraite", next: "Prochaine retraite", emoji: "🏖️", color: "#009688" },
};
const DC_TYPE_ORDER = Object.keys(DC_TYPES);
const DC_TYPE_OPTIONS = DC_TYPE_ORDER.map((t) => ({ value: t, label: `${DC_TYPES[t].emoji} ${DC_TYPES[t].label}` }));

const DC_MONTHS = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août", "septembre", "octobre", "novembre", "décembre"];
const DC_MONTHS_SHORT = ["janv.", "févr.", "mars", "avr.", "mai", "juin", "juil.", "août", "sept.", "oct.", "nov.", "déc."];
const DC_WEEKDAYS = ["dimanche", "lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi"];

const _num = (v) => {
  if (v === null || v === undefined || v === "") return null;
  const n = Number(v);
  return Number.isFinite(n) ? n : null;
};
const _ans = (n) => `${n} ${Math.abs(n) <= 1 ? "an" : "ans"}`;
const _dayNum = (d) => (d === 1 ? "1er" : String(d));

// « 14 mars », « samedi 14 mars », « 14 mars 2027 »
function _fmtDate(date, { weekday = false, year = false } = {}) {
  if (!(date instanceof Date) || isNaN(date)) return "";
  let s = `${_dayNum(date.getDate())} ${DC_MONTHS[date.getMonth()]}`;
  if (weekday) s = `${DC_WEEKDAYS[date.getDay()]} ${s}`;
  if (year) s += ` ${date.getFullYear()}`;
  return s;
}

// « 03/05/2014 » → « 3 mai 2014 »
function _fmtFrDate(str) {
  const m = /^(\d{1,2})\/(\d{1,2})\/(\d{4})$/.exec(String(str || "").trim());
  if (!m) return String(str || "");
  const d = new Date(Number(m[3]), Number(m[2]) - 1, Number(m[1]));
  return _fmtDate(d, { year: true });
}

function _today() {
  const n = new Date();
  return new Date(n.getFullYear(), n.getMonth(), n.getDate());
}

function _addDays(days) {
  const t = _today();
  return new Date(t.getFullYear(), t.getMonth(), t.getDate() + days);
}

// Capteur fourni par l'intégration ? (registre des entités si dispo, sinon attribut event_type)
function _isDcSensor(hass, id) {
  if (!id.startsWith("sensor.")) return false;
  const st = hass.states[id];
  const type = st?.attributes?.event_type;
  if (!DC_TYPES[type]) return false;
  const ent = hass.entities?.[id];
  if (ent && ent.platform) return ent.platform === DC_DOMAIN;
  return true;
}

function _detectAll(hass) {
  return Object.keys(hass?.states || {}).filter((id) => _isDcSensor(hass, id)).sort();
}

function _displayName(a, id) {
  if (a.first_name) return String(a.first_name);
  const fn = String(a.friendly_name || "");
  if (fn) return fn.split(" - ")[0];
  return id;
}

function _parseEvent(hass, id) {
  const st = hass?.states?.[id];
  if (!st) return null;
  const a = st.attributes || {};
  const type = a.event_type;
  const days = parseInt(st.state, 10);
  if (!DC_TYPES[type] || !Number.isFinite(days) || days < 0) return null;
  const e = {
    id,
    type,
    days,
    date: _addDays(days),
    name: _displayName(a, id),
    full: String(a.friendly_name || "").split(" - ")[0] || _displayName(a, id),
    years: _num(a.years),
    category: a.age_category || null,
    wedding: a.wedding_type || null,
    eventDate: a.event_date || null,
    deathDate: a.death_date || null,
    ageIfAlive: _num(a.age_if_alive),
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

const _sortEvents = (a, b) => Number(a.past) - Number(b.past) || a.days - b.days || String(a.name).localeCompare(String(b.name), "fr");

// Détails sans le nom (pour les listes)
function _details(e) {
  const out = [];
  const today = e.days === 0 && !e.past;
  switch (e.type) {
    case "birthday":
      if (e.years !== null) out.push(today ? `fête ses ${_ans(e.years)} 🎉` : `aura ${_ans(e.years)}`);
      if (e.category) out.push(e.category);
      break;
    case "anniversary":
      if (e.years !== null) out.push(`${_ans(e.years)} de mariage`);
      if (e.wedding) out.push(e.wedding);
      break;
    case "memorial":
      if (e.years !== null) out.push(`aurait eu ${_ans(e.years)}`);
      if (e.sinceDeath !== null) out.push(`disparu(e) depuis ${_ans(e.sinceDeath)}`);
      break;
    case "promotion":
    case "special_event":
      if (e.years !== null && e.years > 0) out.push(`${_ans(e.years)}`);
      break;
    case "retirement":
      if (e.past) {
        out.push(e.retired > 0 ? `retraité(e) depuis ${_ans(e.retired)}` : "retraité(e) cette année");
      } else if (e.remaining !== null && !today) {
        out.push(e.remaining > 0 ? `départ dans ${_ans(e.remaining)}` : "départ dans moins d'un an");
      }
      if (e.worked !== null) out.push(`${_ans(e.worked)} de carrière`);
      if (e.medal) out.push(`🏅 médaille ${e.medal}`);
      break;
  }
  return out;
}

// Phrase avec le nom (carte compte à rebours)
function _sentence(e) {
  const today = e.days === 0 && !e.past;
  const n = e.name;
  switch (e.type) {
    case "birthday":
      return e.years === null ? n : today ? `${n} fête ses ${_ans(e.years)} !` : `${n} aura ${_ans(e.years)}`;
    case "anniversary":
      return e.years === null ? e.full : today ? `${e.full} : ${_ans(e.years)} de mariage aujourd'hui !` : `${e.full} : ${_ans(e.years)} de mariage`;
    case "memorial":
      return e.years === null ? n : `${n} aurait eu ${_ans(e.years)}`;
    case "retirement":
      if (e.past) return e.retired > 0 ? `${n} est retraité(e) depuis ${_ans(e.retired)}` : `${n} est retraité(e)`;
      return today ? `${n} part à la retraite aujourd'hui !` : `${n} part à la retraite`;
    default:
      return e.years !== null && e.years > 0 ? `${n} · ${_ans(e.years)}` : n;
  }
}

function _extras(e) {
  switch (e.type) {
    case "birthday":
      return e.category ? [e.category] : [];
    case "anniversary":
      return e.wedding ? [e.wedding] : [];
    case "memorial":
      return e.sinceDeath !== null ? [`disparu(e) depuis ${_ans(e.sinceDeath)}`] : [];
    case "retirement":
      return [e.worked !== null ? `${_ans(e.worked)} de carrière` : null, e.medal ? `🏅 médaille ${e.medal}` : null].filter(Boolean);
    default:
      return [];
  }
}

function _badge(e, { long = false } = {}) {
  if (e.past) return { cls: "b-past", text: "✓" };
  if (e.days === 0) return { cls: "b-today", text: "Aujourd'hui !" };
  if (e.days === 1) return { cls: "b-week", text: "Demain" };
  const cls = e.days < 7 ? "b-week" : e.days < 30 ? "b-month" : "b-later";
  return { cls, text: long ? `dans ${e.days} jours` : `J-${e.days}` };
}

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
    if (config && typeof config !== "object") throw new Error("Configuration invalide");
    this._config = { ...this.constructor.defaults, ...(config || {}) };
    this._key = null;
    this._render();
  }

  set hass(hass) {
    const prev = this._hass;
    this._hass = hass;
    const ids = this._entityIds();
    const key = ids.join(",");
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

  _header(defaultEmoji) {
    const t = this._config.title;
    if (!t) return "";
    return `<div class="header">${_esc(t)}${defaultEmoji && this._config.show_icon !== false ? ` <span aria-hidden="true">${defaultEmoji}</span>` : ""}</div>`;
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

const _entitiesField = (helper) => ({
  name: "entities",
  selector: { entity: { multiple: true, filter: { domain: "sensor", integration: DC_DOMAIN } } },
  _helper: helper,
});
const _typesField = () => ({ name: "types", selector: { select: { multiple: true, mode: "list", options: DC_TYPE_OPTIONS } } });
// Construit le formulaire natif HA : retire les clés internes « _helper » et fournit libellés + aides FR.
function _form(schema, labels) {
  const helpers = {};
  const clean = (list) =>
    list.map((it) => {
      const { _helper, ...rest } = it;
      if (_helper && it.name) helpers[it.name] = _helper;
      if (rest.schema) rest.schema = clean(rest.schema);
      return rest;
    });
  const cleaned = clean(schema);
  return { schema: cleaned, computeLabel: (s) => labels[s.name], computeHelper: (s) => helpers[s.name] };
}

/* ---------------------------------------------------------------------- */
/* 1. Carte Liste / Agenda                                                 */
/* ---------------------------------------------------------------------- */
const LIST_TAG = "date-countdown-list-card";

class DateCountdownListCard extends DateCountdownBaseCard {
  static get defaults() {
    return {
      title: "Souvenirs et Célébrations",
      show_icon: true,
      group_by_type: true,
      max_items: 0,
      horizon_days: 0,
      hide_today: false,
      hide_past: false,
      compact: false,
      show_date: true,
      show_details: true,
    };
  }

  static getConfigForm() {
    const schema = [
      { name: "title", selector: { text: {} } },
      _entitiesField("Vide = détection automatique de tous les capteurs Souvenirs et Célébrations."),
      { ..._typesField(), _helper: "Aucun type coché = tous les types." },
      {
        type: "grid",
        name: "",
        flatten: true,
        schema: [
          { name: "max_items", selector: { number: { min: 0, max: 100, mode: "box" } }, _helper: "0 = illimité" },
          { name: "horizon_days", selector: { number: { min: 0, max: 366, mode: "box", unit_of_measurement: "jours" } }, _helper: "0 = pas de limite" },
        ],
      },
      {
        type: "grid",
        name: "",
        flatten: true,
        schema: [
          { name: "group_by_type", selector: { boolean: {} } },
          { name: "compact", selector: { boolean: {} } },
          { name: "show_date", selector: { boolean: {} } },
          { name: "show_details", selector: { boolean: {} } },
          { name: "hide_today", selector: { boolean: {} } },
          { name: "hide_past", selector: { boolean: {} } },
          { name: "show_icon", selector: { boolean: {} } },
        ],
      },
    ];
    return _form(schema, {
        title: "Titre",
        entities: "Capteurs (sélection manuelle)",
        types: "Types d'événements affichés",
        max_items: "Nombre maximum d'événements",
        horizon_days: "Horizon",
        group_by_type: "Regrouper par type",
        compact: "Affichage compact",
        show_date: "Afficher la date",
        show_details: "Afficher les détails (âge, noces, catégorie…)",
        hide_today: "Masquer les événements du jour",
        hide_past: "Masquer les retraites passées",
        show_icon: "Emoji dans le titre",
      });
  }

  static getStubConfig() {
    return { title: "Souvenirs et Célébrations", group_by_type: true, max_items: 8 };
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
    const title = e.full;
    return `<div class="row type-${e.type}${e.days === 0 && !e.past ? " is-today" : ""}" style="--dc-color:${DC_TYPES[e.type].color}"
        data-entity="${_esc(e.id)}" role="button" tabindex="0" aria-label="${_esc(`${DC_TYPES[e.type].one} — ${title}`)}">
      <div class="ico" aria-hidden="true">${DC_TYPES[e.type].emoji}</div>
      <div class="txt">
        <div class="name">${_esc(title)}${e.notif ? ` <span class="bell" title="Notifications actives">🔔</span>` : ""}</div>
        ${meta.length ? `<div class="meta">${meta.map(_esc).join(" · ")}</div>` : ""}
      </div>
      <span class="badge ${b.cls}">${_esc(b.text)}</span>
    </div>`;
  }

  _build() {
    const c = this._config;
    const list = this._filtered();
    this._lastCount = list.length;
    let body;
    if (!list.length) {
      body = `<div class="muted">Aucun événement à afficher.</div>`;
    } else if (c.group_by_type) {
      body = DC_TYPE_ORDER.filter((t) => list.some((e) => e.type === t))
        .map((t) => {
          const items = list.filter((e) => e.type === t);
          return `<div class="section"><div class="sec-title" style="--dc-color:${DC_TYPES[t].color}">${DC_TYPES[t].emoji} ${_esc(DC_TYPES[t].label)} <span class="count">${items.length}</span></div>${items.map((e) => this._row(e)).join("")}</div>`;
        })
        .join("");
    } else {
      body = `<div class="section">${list.map((e) => this._row(e)).join("")}</div>`;
    }
    return `<ha-card class="${c.compact ? "compact" : ""}">${this._header("🎉")}<div class="content">${body}</div></ha-card>`;
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
    const schema = [
      {
        name: "entity",
        selector: { entity: { filter: { domain: "sensor", integration: DC_DOMAIN } } },
        _helper: "Vide = le prochain événement est choisi automatiquement.",
      },
      { name: "title", selector: { text: {} }, _helper: "Vide = « Prochain anniversaire », « Prochaine retraite »…" },
      { ..._typesField(), _helper: "Pour le choix automatique. Aucun type coché = tous." },
      {
        type: "grid",
        name: "",
        flatten: true,
        schema: [
          { name: "show_ring", selector: { boolean: {} } },
          { name: "show_date", selector: { boolean: {} } },
          { name: "show_details", selector: { boolean: {} } },
          { name: "celebrate", selector: { boolean: {} }, _helper: "Confettis le jour J (désactivés si « réduire les animations » est actif)." },
        ],
      },
    ];
    return _form(schema, {
        entity: "Événement",
        title: "Titre",
        types: "Types d'événements (choix automatique)",
        show_ring: "Anneau de progression",
        show_date: "Afficher la date",
        show_details: "Afficher les détails",
        celebrate: "Animation festive le jour J 🎉",
      });
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
      return `<ha-card>${c.title ? `<div class="header">${_esc(c.title)}</div>` : ""}<div class="muted">Aucun événement à venir.</div></ha-card>`;
    }
    const T = DC_TYPES[e.type];
    const today = e.days === 0 && !e.past;
    const festive = today && e.type !== "memorial";
    const R = 52;
    const C = 2 * Math.PI * R;
    const p = this._progress(e);
    const label = c.title || (today ? T.one : T.next);
    const extras = c.show_details ? _extras(e) : [];
    const sub = [_sentence(e), ...extras];
    const center = e.past
      ? `<div class="big small">✓</div><div class="unit">retraité(e)</div>`
      : today
        ? `<div class="big emoji">${festive ? "🎉" : T.emoji}</div><div class="unit">Jour J</div>`
        : `<div class="big">${e.days}</div><div class="unit">${e.days === 1 ? "jour" : "jours"}</div>`;
    const ring = c.show_ring
      ? `<svg viewBox="0 0 120 120" class="ring" aria-hidden="true">
          <circle cx="60" cy="60" r="${R}" class="track"/>
          <circle cx="60" cy="60" r="${R}" class="bar" stroke-dasharray="${C.toFixed(2)}" stroke-dashoffset="${(C * (1 - p)).toFixed(2)}"/>
        </svg>`
      : "";
    const dateLine = c.show_date && !e.past ? `<div class="date">${today ? "C'est aujourd'hui !" : `le ${_fmtDate(e.date, { weekday: true, year: e.date.getFullYear() !== _today().getFullYear() })}`}</div>` : "";
    return `<ha-card class="${festive ? "festive" : ""} ${e.type === "memorial" ? "sober" : ""}" style="--dc-color:${T.color}">
      ${festive && c.celebrate ? this._confetti() : ""}
      <div class="hero" data-entity="${_esc(e.id)}" role="button" tabindex="0" aria-label="${_esc(`${label} — ${_sentence(e)}`)}">
        <div class="dial ${c.show_ring ? "" : "noring"}">${ring}<div class="center">${center}</div></div>
        <div class="info">
          <div class="label"><span class="emoji-s" aria-hidden="true">${T.emoji}</span> ${_esc(label)}${e.notif ? ` <span class="bell" title="Notifications actives">🔔</span>` : ""}</div>
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
    return { title: "Frise des célébrations", show_icon: true, months: 12, layout: "frise", show_empty_months: true, show_details: true };
  }

  static getConfigForm() {
    const schema = [
      { name: "title", selector: { text: {} } },
      _entitiesField("Vide = détection automatique de tous les capteurs Souvenirs et Célébrations."),
      { ..._typesField(), _helper: "Aucun type coché = tous les types." },
      {
        type: "grid",
        name: "",
        flatten: true,
        schema: [
          { name: "months", selector: { number: { min: 1, max: 12, mode: "slider" } } },
          {
            name: "layout",
            selector: { select: { mode: "dropdown", options: [{ value: "frise", label: "Frise verticale" }, { value: "grid", label: "Grille de mois" }] } },
          },
          { name: "show_empty_months", selector: { boolean: {} } },
          { name: "show_details", selector: { boolean: {} } },
        ],
      },
    ];
    return _form(schema, {
        title: "Titre",
        entities: "Capteurs (sélection manuelle)",
        types: "Types d'événements affichés",
        months: "Nombre de mois",
        layout: "Disposition",
        show_empty_months: "Afficher les mois sans événement",
        show_details: "Afficher les détails",
      });
  }

  static getStubConfig() {
    return { title: "Frise des célébrations", months: 12, layout: "frise" };
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
          title="${_esc(`${DC_TYPES[e.type].one} — ${e.full} — ${_fmtDate(e.date, { weekday: true })}`)}">
        <span class="day">${_esc(_dayNum(e.date.getDate()))}</span>
        <span class="dot" aria-hidden="true"></span>
        <span class="em" aria-hidden="true">${DC_TYPES[e.type].emoji}</span>
        <span class="nm">${_esc(e.full)}${det.length ? ` <small>${_esc(det[0])}</small>` : ""}</span>
        ${e.days < 30 ? `<span class="badge ${b.cls}">${_esc(b.text)}</span>` : ""}
      </div>`;
    };
    const month = (bk) => `<div class="month${bk.current ? " current" : ""}${bk.items.length ? "" : " empty"}">
        <div class="mlabel"><span class="mdot" aria-hidden="true"></span>${_esc(DC_MONTHS[bk.m])}${bk.y !== t.getFullYear() ? ` <span class="yr">${bk.y}</span>` : ""}
          ${bk.items.length ? `<span class="count">${bk.items.length}</span>` : ""}</div>
        <div class="items">${bk.items.length ? bk.items.map(chip).join("") : `<div class="none">—</div>`}</div>
      </div>`;
    const legend = DC_TYPE_ORDER.filter((ty) => buckets.some((b) => b.items.some((e) => e.type === ty)))
      .map((ty) => `<span class="lg" style="--dc-color:${DC_TYPES[ty].color}"><span class="dot"></span>${_esc(DC_TYPES[ty].label)}</span>`)
      .join("");
    const body = total
      ? `<div class="${c.layout === "grid" ? "grid" : "frise"}">${shown.map(month).join("")}</div>${legend ? `<div class="legend">${legend}</div>` : ""}`
      : `<div class="muted">Aucun événement sur les ${months} prochains mois.</div>`;
    return `<ha-card>${this._header("📅")}<div class="content">${body}</div></ha-card>`;
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
    return { title: "En mémoire", show_icon: true, max_items: 0, sort: "date", show_death_date: true, show_age_at_death: true, show_countdown: true, flicker: true };
  }

  static getConfigForm() {
    const schema = [
      { name: "title", selector: { text: {} } },
      _entitiesField("Seuls les capteurs de type mémorial sont affichés. Vide = détection automatique."),
      {
        type: "grid",
        name: "",
        flatten: true,
        schema: [
          { name: "max_items", selector: { number: { min: 0, max: 50, mode: "box" } }, _helper: "0 = illimité" },
          {
            name: "sort",
            selector: { select: { mode: "dropdown", options: [{ value: "date", label: "Date la plus proche" }, { value: "name", label: "Nom" }] } },
          },
          { name: "show_death_date", selector: { boolean: {} } },
          { name: "show_age_at_death", selector: { boolean: {} } },
          { name: "show_countdown", selector: { boolean: {} } },
          { name: "flicker", selector: { boolean: {} } },
          { name: "show_icon", selector: { boolean: {} } },
        ],
      },
    ];
    return _form(schema, {
        title: "Titre",
        entities: "Capteurs de mémoriaux",
        max_items: "Nombre maximum",
        sort: "Tri",
        show_death_date: "Afficher la date de décès",
        show_age_at_death: "Afficher l'âge au décès",
        show_countdown: "Afficher le compte à rebours",
        flicker: "Bougie animée (douce)",
        show_icon: "Bougie dans le titre",
      });
  }

  static getStubConfig() {
    return { title: "En mémoire" };
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
    if (c.sort === "name") list = list.sort((a, b) => String(a.full).localeCompare(String(b.full), "fr"));
    const max = Number(c.max_items) || 0;
    if (max > 0) list = list.slice(0, max);
    this._lastCount = list.length;
    const row = (e) => {
      const lines = [];
      if (e.years !== null) lines.push(`${e.days === 0 ? "Aurait eu" : "aurait eu"} <b>${_esc(_ans(e.years))}</b> ${e.days === 0 ? "aujourd'hui" : `le ${_esc(_fmtDate(e.date))}`}`);
      const death = [];
      if (e.sinceDeath !== null) death.push(`disparu(e) depuis ${_esc(_ans(e.sinceDeath))}`);
      if (c.show_death_date && e.deathDate) death.push(`† ${_esc(_fmtFrDate(e.deathDate))}`);
      if (c.show_age_at_death && e.ageAtDeath !== null) death.push(`à ${_esc(_ans(e.ageAtDeath))}`);
      const b = _badge(e, { long: true });
      return `<div class="row${e.days === 0 ? " is-today" : ""}" data-entity="${_esc(e.id)}" role="button" tabindex="0">
        <div class="candle" aria-hidden="true"><span class="flame"></span><span class="wax"></span></div>
        <div class="txt">
          <div class="name">${_esc(e.full)}${e.notif ? ` <span class="bell" title="Notifications actives">🔔</span>` : ""}</div>
          ${lines.map((l) => `<div class="line">${l}</div>`).join("")}
          ${death.length ? `<div class="line death">${death.join(" · ")}</div>` : ""}
        </div>
        ${c.show_countdown ? `<span class="badge soft">${e.days === 0 ? "Aujourd'hui" : _esc(b.text)}</span>` : ""}
      </div>`;
    };
    const body = list.length ? list.map(row).join("") : `<div class="muted">Aucun mémorial trouvé.</div>`;
    return `<ha-card class="${c.flicker ? "flicker" : ""}">${this._header("🕯️")}<div class="content">${body}</div></ha-card>`;
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
  {
    tag: CARD_TAG,
    cls: DateCountdownInformationsCard,
    name: "Souvenirs et Célébrations — Informations",
    description: "Anniversaire du jour, prochain anniversaire, âge et catégorie d'âge 🎂",
  },
  {
    tag: LIST_TAG,
    cls: DateCountdownListCard,
    name: "Souvenirs et Célébrations — Liste / Agenda",
    description: "Tous les événements (anniversaires, mariages, mémoriaux, promotions, événements, retraites), triés, groupés, avec badge J-N 📋",
  },
  {
    tag: COUNTDOWN_TAG,
    cls: DateCountdownCountdownCard,
    name: "Souvenirs et Célébrations — Compte à rebours",
    description: "Le prochain événement en grand, anneau de progression et confettis le jour J ⏳",
  },
  {
    tag: TIMELINE_TAG,
    cls: DateCountdownTimelineCard,
    name: "Souvenirs et Célébrations — Frise des mois",
    description: "Frise des 12 prochains mois avec les événements de chaque mois 📅",
  },
  {
    tag: MEMORIAL_TAG,
    cls: DateCountdownMemorialCard,
    name: "Souvenirs et Célébrations — Mémoriaux",
    description: "Carte sobre en mémoire des disparus : âge qu'ils auraient eu, date de décès 🕯️",
  },
];

window.customCards = window.customCards || [];
for (const card of DC_CARDS) {
  if (!customElements.get(card.tag)) customElements.define(card.tag, card.cls);
  if (!window.customCards.some((c) => c.type === card.tag)) {
    window.customCards.push({ type: card.tag, name: card.name, description: card.description, preview: true, documentationURL: DC_DOC });
  }
}
console.info(`%c SOUVENIRS-ET-CELEBRATIONS-CARDS %c ${CARD_VERSION} `, "color:white;background:#e91e63;font-weight:700", "color:#e91e63");
