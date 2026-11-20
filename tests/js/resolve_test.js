// Test node des cartes : entités secondaires → capteur principal, sans doublons ; éditeurs.
const fs = require("fs");
const vm = require("vm");
const assert = require("assert");

const file = process.argv[2];
const code = fs.readFileSync(file, "utf8");
class FakeElement {
  attachShadow() { this.shadowRoot = { innerHTML: "", addEventListener() {}, querySelector: () => null, querySelectorAll: () => [] }; return this.shadowRoot; }
  dispatchEvent() {}
  addEventListener() {}
}
const ctx = {
  console: { info() {}, log: console.log, warn() {} },
  HTMLElement: FakeElement,
  customElements: { get: () => undefined, define() {} },
  window: {},
  navigator: { language: "fr" },
  document: { querySelector: () => null },
  Intl, Date, Math, Number, String, Object, Array, JSON, Set, Map, RegExp, Error, CustomEvent: class {},
  requestAnimationFrame: () => 0, setTimeout, clearTimeout,
};
vm.createContext(ctx);
vm.runInContext(code + "\n;globalThis.__dc = { _resolveIds, _resolveMain, _entitySelector, DateCountdownListCard, DateCountdownCountdownCard, DateCountdownMemorialCard, DateCountdownInformationsCard };", ctx);
const dc = ctx.__dc;

const main = (type, extra = {}) => ({ state: "54", attributes: { event_type: type, friendly_name: "X", ...extra } });
const hass = {
  language: "fr",
  locale: { language: "fr" },
  states: {
    "sensor.anais": main("birthday", { event_date: "15/06/2001", years: 25 }),
    "sensor.anais_jours_restants": { state: "54", attributes: { unit_of_measurement: "d" } },
    "binary_sensor.anais_aujourd_hui_jour_j": { state: "off", attributes: {} },
    "sensor.jeanne": main("memorial", { event_date: "01/03/1946", death_date: "10/10/2020" }),
    "sensor.jeanne_date_de_deces": { state: "2020-10-10", attributes: { device_class: "date" } },
    "sensor.autre": { state: "1", attributes: {} },
  },
  entities: {
    "sensor.anais": { entity_id: "sensor.anais", device_id: "dev_a", platform: "date_countdown" },
    "sensor.anais_jours_restants": { entity_id: "sensor.anais_jours_restants", device_id: "dev_a", platform: "date_countdown" },
    "binary_sensor.anais_aujourd_hui_jour_j": { entity_id: "binary_sensor.anais_aujourd_hui_jour_j", device_id: "dev_a", platform: "date_countdown" },
    "sensor.jeanne": { entity_id: "sensor.jeanne", device_id: "dev_j", platform: "date_countdown" },
    "sensor.jeanne_date_de_deces": { entity_id: "sensor.jeanne_date_de_deces", device_id: "dev_j", platform: "date_countdown" },
    "sensor.autre": { entity_id: "sensor.autre", device_id: "dev_x", platform: "demo" },
  },
};

// Résolution
assert.strictEqual(dc._resolveMain(hass, "sensor.anais_jours_restants"), "sensor.anais");
assert.strictEqual(dc._resolveMain(hass, "binary_sensor.anais_aujourd_hui_jour_j"), "sensor.anais");
assert.strictEqual(dc._resolveMain(hass, "sensor.anais"), "sensor.anais");
assert.strictEqual(dc._resolveMain(hass, "sensor.autre"), "sensor.autre");
assert.strictEqual(dc._resolveMain({ states: hass.states }, "sensor.anais_jours_restants"), "sensor.anais_jours_restants");
assert.deepStrictEqual(
  [...dc._resolveIds(hass, ["sensor.anais_jours_restants", "sensor.anais", "binary_sensor.anais_aujourd_hui_jour_j", "sensor.jeanne_date_de_deces"])],
  ["sensor.anais", "sensor.jeanne"]
);

// Cartes : liste sans doublons, compte à rebours sur une entité secondaire
const list = new dc.DateCountdownListCard();
list.setConfig({ entities: ["sensor.anais_jours_restants", "binary_sensor.anais_aujourd_hui_jour_j", "sensor.anais", "sensor.jeanne_date_de_deces"] });
list._hass = hass;
assert.deepStrictEqual([...list._entityIds()], ["sensor.anais", "sensor.jeanne"]);
const cd = new dc.DateCountdownCountdownCard();
cd.setConfig({ entity: "binary_sensor.anais_aujourd_hui_jour_j" });
cd._hass = hass;
assert.deepStrictEqual([...cd._entityIds()], ["sensor.anais"]);
const info = new dc.DateCountdownInformationsCard();
info.setConfig({ entities: ["sensor.anais_jours_restants"] });
info._hass = hass;
assert.deepStrictEqual([...info._entityIds()], ["sensor.anais"]);
// Sans configuration : détection automatique des seuls capteurs principaux
const auto = new dc.DateCountdownListCard();
auto.setConfig({});
auto._hass = hass;
assert.deepStrictEqual([...auto._entityIds()], ["sensor.anais", "sensor.jeanne"]);

// Éditeurs : sans hass connu, filtre intégration ; avec hass, seulement les capteurs principaux du type
let sel = dc._entitySelector("birthday", true);
assert.strictEqual(sel.entity.include_entities, undefined);
assert.strictEqual(sel.entity.filter.integration, "date_countdown");
list.hass = hass; // mémorise hass (set hass → _setLang)
sel = dc._entitySelector("birthday", true);
assert.deepStrictEqual([...sel.entity.include_entities], ["sensor.anais"]);
assert.strictEqual(sel.entity.multiple, true);
sel = dc._entitySelector(undefined, false);
assert.deepStrictEqual([...sel.entity.include_entities], ["sensor.anais", "sensor.jeanne"]);
const memForm = dc.DateCountdownMemorialCard.getConfigForm();
const entField = memForm.schema.find((s) => s.name === "entities");
assert.deepStrictEqual([...entField.selector.entity.include_entities], ["sensor.jeanne"]);
console.log("OK");
