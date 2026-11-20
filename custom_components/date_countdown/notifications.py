"""Notifications natives (jour J et rappel J-N) pour Souvenirs et Célébrations.

Le calcul du prochain événement réutilise ``DateCountdownSensor.update_for_date``
(même logique que le capteur : état == 0 le jour J), sans dupliquer les règles.
"""

from __future__ import annotations

import asyncio
import logging
from datetime import date, datetime, time, timedelta
from typing import Any, Iterable

from homeassistant.components import persistent_notification
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import CALLBACK_TYPE, HomeAssistant, callback
from homeassistant.helpers.event import async_call_later, async_track_time_change
from homeassistant.helpers.start import async_at_started
from homeassistant.helpers.storage import Store
from homeassistant.util import dt as dt_util

from .const import (
    CONF_NOTIFICATIONS,
    CONF_NOTIFY_ENABLED,
    CONF_NOTIFY_PERSISTENT,
    CONF_NOTIFY_REMINDER_DAYS,
    CONF_NOTIFY_TARGETS,
    CONF_NOTIFY_TIME,
    DEFAULT_NOTIFY_REMINDER_DAYS,
    DEFAULT_NOTIFY_TIME,
    DOMAIN,
    EVENT_TYPES,
    NOTIFY_STORAGE_KEY,
    NOTIFY_STORAGE_VERSION,
    NOTIFY_TITLE,
)
from .sensor import DateCountdownSensor

_LOGGER = logging.getLogger(__name__)

KIND_DAY = "jour_j"
KIND_REMINDER = "rappel"
RETRY_DELAY_SECONDS = 600
STORE_RETENTION_DAYS = 30

DATA_NOTIFIERS = "_notifiers"
DATA_STORE = "_notify_store"

# Services notify qui n'acceptent pas un simple {message, title}
_EXCLUDED_NOTIFY_SERVICES = {"send_message"}

_VOWELS = "aeiouyàâäéèêëîïôöùûüÿæœAEIOUYÀÂÄÉÈÊËÎÏÔÖÙÛÜŸÆŒ"


# ---------------------------------------------------------------------------
# Options
# ---------------------------------------------------------------------------

def get_notification_options(entry: ConfigEntry) -> dict[str, Any]:
    """Retourne les options de notification de l'entrée, complétées par les défauts."""
    raw = dict(entry.options.get(CONF_NOTIFICATIONS) or {})
    targets = raw.get(CONF_NOTIFY_TARGETS) or []
    if isinstance(targets, str):
        targets = [targets]
    try:
        reminder = int(raw.get(CONF_NOTIFY_REMINDER_DAYS, DEFAULT_NOTIFY_REMINDER_DAYS) or 0)
    except (TypeError, ValueError):
        reminder = DEFAULT_NOTIFY_REMINDER_DAYS
    return {
        CONF_NOTIFY_ENABLED: bool(raw.get(CONF_NOTIFY_ENABLED, False)),
        CONF_NOTIFY_TARGETS: [str(t) for t in targets if t],
        CONF_NOTIFY_TIME: normalize_time(raw.get(CONF_NOTIFY_TIME, DEFAULT_NOTIFY_TIME)),
        CONF_NOTIFY_REMINDER_DAYS: max(0, reminder),
        CONF_NOTIFY_PERSISTENT: bool(raw.get(CONF_NOTIFY_PERSISTENT, False)),
    }


def parse_time(value: Any) -> time:
    """Convertit 'HH:MM' ou 'HH:MM:SS' en time (09:00 si invalide)."""
    if isinstance(value, time):
        return value
    parsed = dt_util.parse_time(str(value)) if value else None
    if parsed is None:
        _LOGGER.warning("Horaire de notification invalide '%s', utilisation de 09:00", value)
        parsed = time(9, 0)
    return parsed


def normalize_time(value: Any) -> str:
    """Normalise un horaire au format HH:MM:SS."""
    return parse_time(value).strftime("%H:%M:%S")


def available_notify_targets(hass: HomeAssistant) -> list[str]:
    """Liste les services notify.* disponibles (ex. notify.mobile_app_pixel)."""
    services = hass.services.async_services().get("notify", {})
    return sorted(
        f"notify.{name}" for name in services if name not in _EXCLUDED_NOTIFY_SERVICES
    )


# ---------------------------------------------------------------------------
# Calcul des événements et messages
# ---------------------------------------------------------------------------

def iter_events(entry: ConfigEntry) -> list[dict[str, Any]]:
    """Événements valides de l'entrée."""
    return [
        event
        for event in entry.options.get("events", []) or []
        if isinstance(event, dict) and event.get("type") in EVENT_TYPES and "name" in event
    ]


def _new_sensor(event: dict[str, Any]) -> DateCountdownSensor:
    return DateCountdownSensor(
        event["name"],
        event.get("first_name", ""),
        event["type"],
        event.get("date"),
        event.get("death_date"),
        event.get("start_date"),
        event.get("is_penible", False),
        event.get("career_type", "normale"),
    )


def _compute(event: dict[str, Any], day: date) -> tuple[int | None, dict[str, Any]]:
    """Calcule (jours restants, attributs) pour un événement à une date donnée."""
    sensor = _new_sensor(event)
    sensor.update_for_date(day)
    return sensor.state, sensor.extra_state_attributes


def _ans(n: int) -> str:
    return f"{n} an" if abs(n) == 1 else f"{n} ans"


def _de(name: str) -> str:
    """'de Paul' / 'd’Océane'."""
    return f"d’{name}" if name and name[0] in _VOWELS else f"de {name}"


def _names(event: dict[str, Any]) -> tuple[str, str]:
    """(prénom ou nom, nom complet)."""
    first = (event.get("first_name") or "").strip()
    name = (event.get("name") or "").strip()
    person = first or name
    full = f"{first} {name}".strip() if first and first != name else (name or first)
    return person, full


def build_day_message(event: dict[str, Any], attrs: dict[str, Any]) -> str:
    """Message du jour J, adapté au type d'événement."""
    event_type = event.get("type")
    person, full = _names(event)
    years = attrs.get("years")

    if event_type == "birthday":
        if years is None or years <= 0:
            return f"🎂 Aujourd’hui, c’est l’anniversaire {_de(person)} !"
        msg = f"🎂 Aujourd’hui, {person} a {_ans(years)} !"
        if attrs.get("age_category"):
            msg += f" {attrs['age_category']}"
        return msg

    if event_type == "anniversary":
        if years is None or years <= 0:
            return f"💍 Aujourd’hui, c’est le mariage {_de(full)} !"
        msg = f"💍 Aujourd’hui, {full} fête {_ans(years)} de mariage"
        if attrs.get("wedding_type"):
            return f"{msg} : {attrs['wedding_type']} !"
        return f"{msg} !"

    if event_type == "memorial":
        msg = f"🕯️ Aujourd’hui, {person} aurait eu {_ans(years)}." if years else f"🕯️ Aujourd’hui, nous pensons à {person}."
        since = attrs.get("years_since_death")
        if since:
            msg += f" Disparu(e) depuis {_ans(since)}."
        return f"{msg} Une pensée en sa mémoire."

    if event_type == "promotion":
        if years and years > 0:
            return f"🏆 Aujourd’hui, {full} fête {_ans(years)} de promotion !"
        return f"🏆 Aujourd’hui : promotion {_de(full)} !"

    if event_type == "special_event":
        if years and years > 0:
            return f"⭐ Aujourd’hui : {full} ({_ans(years)}) !"
        return f"⭐ Aujourd’hui : {full} !"

    if event_type == "retirement":
        worked = attrs.get("years_worked")
        msg = f"🏖️ Aujourd’hui, {person} part à la retraite"
        msg += f" après {_ans(worked)} de travail !" if worked else " !"
        if attrs.get("work_medal"):
            msg += f" Médaille du travail : {attrs['work_medal']}."
        return msg

    return f"📅 Aujourd’hui : {full} !"


def build_reminder_message(event: dict[str, Any], attrs: dict[str, Any], days: int) -> str:
    """Message de rappel J-N (ex. « Dans 7 jours : anniversaire d’Océane (25 ans) »)."""
    event_type = event.get("type")
    person, full = _names(event)
    years = attrs.get("years")
    when = "Demain" if days == 1 else f"Dans {days} jours"
    suffix = f" ({_ans(years)})" if years and years > 0 else ""

    if event_type == "birthday":
        body = f"anniversaire {_de(person)}{suffix}"
    elif event_type == "anniversary":
        body = f"anniversaire de mariage {_de(full)}{suffix}"
        if attrs.get("wedding_type"):
            body += f" – {attrs['wedding_type']}"
    elif event_type == "memorial":
        body = f"souvenir {_de(person)}"
        if years:
            body += f", qui aurait eu {_ans(years)}"
    elif event_type == "promotion":
        body = f"anniversaire de la promotion {_de(full)}{suffix}" if suffix else f"promotion {_de(full)}"
    elif event_type == "special_event":
        body = f"{full}{suffix}"
    elif event_type == "retirement":
        body = f"départ à la retraite {_de(person)}"
    else:
        body = full
    return f"⏳ {when} : {body}"


def compute_due_messages(
    event: dict[str, Any], today: date, reminder_days: int = 0
) -> list[tuple[str, str]]:
    """Liste des (type d'envoi, message) à envoyer aujourd'hui pour un événement."""
    state, attrs = _compute(event, today)
    if state is None:
        return []
    due: list[tuple[str, str]] = []

    is_day = state == 0
    if is_day and event.get("type") == "retirement":
        # Le capteur reste à 0 après la retraite : jour J seulement si hier était J-1.
        prev_state, _ = _compute(event, today - timedelta(days=1))
        is_day = prev_state == 1
    if is_day:
        due.append((KIND_DAY, build_day_message(event, attrs)))

    if reminder_days and reminder_days > 0 and state == reminder_days:
        due.append((f"{KIND_REMINDER}_{reminder_days}", build_reminder_message(event, attrs, reminder_days)))
    return due


def build_preview_message(event: dict[str, Any], today: date) -> str:
    """Message représentatif pour le service de test."""
    state, attrs = _compute(event, today)
    if state is None:
        _, full = _names(event)
        return f"📅 {full}"
    if state == 0:
        return build_day_message(event, attrs)
    return build_reminder_message(event, attrs, state)


def event_key(event: dict[str, Any]) -> str:
    """Identifiant stable d'un événement (identique au unique_id du capteur)."""
    return _new_sensor(event).unique_id or event.get("name", "")


# ---------------------------------------------------------------------------
# Anti-doublon persistant
# ---------------------------------------------------------------------------

class NotificationStore:
    """Mémorise les envois (clé entry_id|événement|date|type) dans .storage."""

    def __init__(self, hass: HomeAssistant) -> None:
        self._store: Store = Store(hass, NOTIFY_STORAGE_VERSION, NOTIFY_STORAGE_KEY)
        self._sent: dict[str, str] = {}
        self._loaded = False
        self._lock = asyncio.Lock()

    @staticmethod
    def make_key(entry_id: str, event_id: str, day: date, kind: str) -> str:
        return f"{entry_id}|{event_id}|{day.isoformat()}|{kind}"

    async def async_load(self) -> None:
        async with self._lock:
            if self._loaded:
                return
            data = await self._store.async_load() or {}
            self._sent = dict(data.get("sent", {}))
            self._loaded = True
            self._prune()

    def was_sent(self, key: str) -> bool:
        return key in self._sent

    async def async_mark_sent(self, key: str) -> None:
        self._sent[key] = dt_util.now().isoformat()
        self._prune()
        await self._store.async_save({"sent": self._sent})

    def _prune(self) -> None:
        limit = dt_util.now().date() - timedelta(days=STORE_RETENTION_DAYS)
        for key in list(self._sent):
            parts = key.split("|")
            try:
                day = date.fromisoformat(parts[-2])
            except (IndexError, ValueError):
                continue
            if day < limit:
                self._sent.pop(key, None)


async def async_get_store(hass: HomeAssistant) -> NotificationStore:
    domain_data = hass.data.setdefault(DOMAIN, {})
    store = domain_data.get(DATA_STORE)
    if store is None:
        store = NotificationStore(hass)
        domain_data[DATA_STORE] = store
    await store.async_load()
    return store


# ---------------------------------------------------------------------------
# Gestionnaire par entrée
# ---------------------------------------------------------------------------

class NotificationManager:
    """Planifie et envoie les notifications d'une entrée."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry, store: NotificationStore) -> None:
        self.hass = hass
        self.entry = entry
        self.store = store
        self.options = get_notification_options(entry)
        self._unsubs: list[CALLBACK_TYPE] = []
        self._retry_unsub: CALLBACK_TYPE | None = None
        self._lock = asyncio.Lock()

    @property
    def enabled(self) -> bool:
        return self.options[CONF_NOTIFY_ENABLED]

    async def async_start(self) -> None:
        """Démarre la planification quotidienne (heure locale HA) et le rattrapage."""
        if not self.enabled:
            return
        at = parse_time(self.options[CONF_NOTIFY_TIME])
        self._unsubs.append(
            async_track_time_change(
                self.hass, self._async_handle_time, hour=at.hour, minute=at.minute, second=at.second
            )
        )
        self._unsubs.append(async_at_started(self.hass, self._async_catch_up))
        _LOGGER.debug("Notifications planifiées à %s pour l'entrée %s", at, self.entry.entry_id)

    @callback
    def async_stop(self) -> None:
        """Nettoyage au déchargement."""
        while self._unsubs:
            self._unsubs.pop()()
        if self._retry_unsub:
            self._retry_unsub()
            self._retry_unsub = None

    async def _async_handle_time(self, _now: datetime) -> None:
        await self.async_check_and_send()

    async def _async_catch_up(self, _hass: HomeAssistant) -> None:
        """Rattrapage : HA (re)démarre après l'heure prévue le jour J."""
        at = parse_time(self.options[CONF_NOTIFY_TIME])
        if dt_util.now().time() >= at:
            await self.async_check_and_send()

    async def _async_retry(self, _now: datetime) -> None:
        self._retry_unsub = None
        await self.async_check_and_send(allow_retry=False)

    async def async_check_and_send(self, allow_retry: bool = True) -> int:
        """Envoie les notifications dues aujourd'hui non encore envoyées. Retourne le nombre envoyé."""
        if not self.enabled:
            return 0
        async with self._lock:
            today = dt_util.now().date()
            reminder = self.options[CONF_NOTIFY_REMINDER_DAYS]
            sent = 0
            failed = False
            for event in iter_events(self.entry):
                event_id = event_key(event)
                for kind, message in compute_due_messages(event, today, reminder):
                    key = NotificationStore.make_key(self.entry.entry_id, event_id, today, kind)
                    if self.store.was_sent(key):
                        continue
                    if await self.async_deliver(message, f"{DOMAIN}_{self.entry.entry_id}_{event_id}_{kind}"):
                        await self.store.async_mark_sent(key)
                        sent += 1
                    else:
                        failed = True
            if failed and allow_retry and self._retry_unsub is None:
                _LOGGER.warning(
                    "Aucune notification n'a pu être envoyée pour %s, nouvel essai dans %s min",
                    self.entry.title, RETRY_DELAY_SECONDS // 60,
                )
                self._retry_unsub = async_call_later(self.hass, RETRY_DELAY_SECONDS, self._async_retry)
            return sent

    async def async_send_test(self, event_ids: Iterable[str] | None = None) -> int:
        """Envoie une notification de test (ignore l'anti-doublon et l'activation)."""
        wanted = set(event_ids or [])
        today = dt_util.now().date()
        count = 0
        for event in iter_events(self.entry):
            if wanted and event_key(event) not in wanted:
                continue
            message = f"🧪 Test – {build_preview_message(event, today)}"
            notification_id = f"{DOMAIN}_{self.entry.entry_id}_{event_key(event)}_test"
            if await self.async_deliver(message, notification_id, test=True):
                count += 1
        return count

    async def async_deliver(self, message: str, notification_id: str, test: bool = False) -> bool:
        """Envoie le message à toutes les cibles ; un échec n'empêche pas les autres."""
        targets = list(self.options[CONF_NOTIFY_TARGETS])
        persistent = self.options[CONF_NOTIFY_PERSISTENT] or (test and not targets)
        success = False
        for target in targets:
            domain, _, service = target.partition(".")
            if not service:
                domain, service = "notify", domain
            if domain != "notify":
                _LOGGER.warning("Cible de notification ignorée (pas un service notify) : %s", target)
                continue
            if not self.hass.services.has_service(domain, service):
                _LOGGER.warning("Service de notification introuvable : %s", target)
                continue
            try:
                await self.hass.services.async_call(
                    domain, service, {"message": message, "title": NOTIFY_TITLE}, blocking=True
                )
                success = True
            except Exception as err:  # noqa: BLE001 - une cible ne doit pas bloquer les autres
                _LOGGER.warning("Échec de la notification via %s : %s", target, err)
        if persistent:
            persistent_notification.async_create(
                self.hass, message, title=NOTIFY_TITLE, notification_id=notification_id
            )
            success = True
        if not targets and not persistent:
            _LOGGER.warning("Notifications activées sans cible pour %s", self.entry.title)
        return success
