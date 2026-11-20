#!/usr/bin/env python3
"""Vérifie les fichiers de traduction de Souvenirs et Célébrations.

Pour chaque fichier ``translations/*.json`` (et ``strings.json``) :
- le fichier est du JSON valide ;
- il a exactement le même ensemble de clés que ``translations/en.json`` ;
- chaque chaîne contient exactement les mêmes placeholders ``{...}`` que en.json ;
- aucune chaîne n'est vide.

Usage : python3 scripts/check_translations.py  (code de sortie 1 en cas d'erreur)
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent / "custom_components" / "date_countdown"
TRANSLATIONS = ROOT / "translations"
PLACEHOLDER = re.compile(r"\{[^{}]*\}")


def flatten(data: dict, prefix: str = "") -> dict[str, str]:
    out: dict[str, str] = {}
    for key, value in data.items():
        path = f"{prefix}{key}"
        if isinstance(value, dict):
            out.update(flatten(value, path + "."))
        else:
            out[path] = value
    return out


def check() -> list[str]:
    errors: list[str] = []
    reference = flatten(json.loads((TRANSLATIONS / "en.json").read_text(encoding="utf-8")))
    files = sorted(TRANSLATIONS.glob("*.json")) + [ROOT / "strings.json"]
    for path in files:
        name = path.relative_to(ROOT)
        try:
            data = flatten(json.loads(path.read_text(encoding="utf-8")))
        except json.JSONDecodeError as err:
            errors.append(f"{name}: JSON invalide ({err})")
            continue
        missing = sorted(set(reference) - set(data))
        extra = sorted(set(data) - set(reference))
        for key in missing:
            errors.append(f"{name}: clé manquante {key}")
        for key in extra:
            errors.append(f"{name}: clé en trop {key}")
        for key in sorted(set(reference) & set(data)):
            value = data[key]
            if not isinstance(value, str) or not value.strip():
                errors.append(f"{name}: valeur vide ou non textuelle pour {key}")
                continue
            expected = sorted(PLACEHOLDER.findall(reference[key]))
            found = sorted(PLACEHOLDER.findall(value))
            if expected != found:
                errors.append(f"{name}: placeholders {found} au lieu de {expected} pour {key}")
        if not missing and not extra:
            print(f"OK  {name} ({len(data)} chaînes)")
    return errors


def main() -> int:
    errors = check()
    for err in errors:
        print(f"ERREUR  {err}")
    print(f"{'Échec' if errors else 'Succès'} : {len(errors)} erreur(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
