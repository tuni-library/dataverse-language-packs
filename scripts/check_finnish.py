
#!/usr/bin/env python3

from pathlib import Path
from jproperties import Properties

PAIRS = [
    ("Bundle.properties", "Bundle_fi.properties"),
    ("citation.properties", "citation_fi.properties"),
    ("BuiltInRoles.properties", "BuiltInRoles_fi.properties"),
    ("ValidationMessages.properties", "ValidationMessages_fi.properties"),
    ("License.properties", "License_fi.properties"),
    ("review.properties", "review_fi.properties"),
    ("staticSearchFields.properties", "staticSearchFields_fi.properties"),
]


def load_properties(path):
    properties = Properties()

    with path.open("rb") as source:
        properties.load(source, encoding="utf-8")

    return {
        key: value.data
        for key, value in properties.items()
    }


def main():
    total_missing = 0
    total_obsolete = 0

    for english_file, finnish_file in PAIRS:
        english_path = Path("en_US") / english_file
        finnish_path = Path("fi_FI") / finnish_file

        english = load_properties(english_path)
        finnish = load_properties(finnish_path)

        missing = sorted(set(english) - set(finnish))
        obsolete = sorted(set(finnish) - set(english))

        total_missing += len(missing)
        total_obsolete += len(obsolete)

        print(f"\n{english_file} / {finnish_file}")
        print(f"English keys: {len(english)}")
        print(f"Finnish keys: {len(finnish)}")

        if missing:
            print("\nMissing Finnish translations:")
            for key in missing:
                print(f"  {key}")
                print(f"    English: {english[key]}")

        if obsolete:
            print("\nFinnish keys absent from English:")
            for key in obsolete:
                print(f"  {key}")

    print("\nSUMMARY")
    print(f"Missing Finnish keys: {total_missing}")
    print(f"Finnish-only keys: {total_obsolete}")


if __name__ == "__main__":
    main()

