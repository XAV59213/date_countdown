/*
 * Carte Lovelace « Informations » 🎂 — Souvenirs et Célébrations (date_countdown)
 * Servie et enregistrée automatiquement par l'intégration.
 */
const CARD_TAG = "date-countdown-informations-card";
const CARD_VERSION = "1.2.13";

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

if (!customElements.get(CARD_TAG)) customElements.define(CARD_TAG, DateCountdownInformationsCard);
window.customCards = window.customCards || [];
if (!window.customCards.some((card) => card.type === CARD_TAG)) {
  window.customCards.push({
    type: CARD_TAG,
    name: "Souvenirs et Célébrations — Informations",
    description: "Anniversaire du jour, prochain anniversaire, âge et catégorie d'âge 🎂",
    preview: true,
    documentationURL: "https://github.com/XAV59213/date_countdown#-carte-lovelace",
  });
}
console.info(`%c SOUVENIRS-ET-CELEBRATIONS-CARD %c ${CARD_VERSION} `, "color:white;background:#e91e63;font-weight:700", "color:#e91e63");
