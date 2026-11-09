
#!/usr/bin/env python3
"""Synchronize IQSS English properties and apply local overrides."""

from pathlib import Path
import re
import shutil
import sys

SOURCE = Path(sys.argv[1])
TARGET = Path("en_US")
OVERRIDES = Path("local-overrides/en_US")

# Basic Java properties key=value or key:value format.
ENTRY = re.compile(
    r"^(\s*([A-Za-z0-9_./-]+)\s*[=:]\s*)(.*?)(\r?\n?)$"
)


def parse_overrides(path):
    entries = {}

    for number, line in enumerate(
        path.read_text(encoding="utf-8").splitlines(), 1
    ):
        stripped = line.strip()

        if not stripped or stripped.startswith(("#", "!")):
            continue

        match = ENTRY.fullmatch(line)

        if not match or line.rstrip().endswith("\\"):
            raise ValueError(
                f"Unsupported override at {path}:{number}"
            )

        key = match.group(2)
        value = match.group(3)

        if key in entries:
            raise ValueError(f"Duplicate override: {key}")

        entries[key] = value

    return entries


def apply_overrides(target_file, overrides):
    content = target_file.read_text(encoding="utf-8")
    lines = content.splitlines(keepends=True)

    found = set()
    output = []

    for line in lines:
        match = ENTRY.fullmatch(line)

        if match and match.group(2) in overrides:
            key = match.group(2)

            if key in found:
                raise ValueError(f"Duplicate source key: {key}")

            found.add(key)

            output.append(
                match.group(1)
                + overrides[key]
                + match.group(4)
            )
        else:
            output.append(line)

    missing = set(overrides) - found

    if missing:
        raise ValueError(
            f"Override keys missing from {target_file}: "
            f"{sorted(missing)}"
        )

    target_file.write_text(
        "".join(output), encoding="utf-8"
    )


def main():
    if not SOURCE.is_dir():
        raise ValueError(f"Source directory missing: {SOURCE}")

    files = sorted(SOURCE.glob("*.properties"))

    if not files:
        raise ValueError("No English properties files found")

    TARGET.mkdir(exist_ok=True)

    # Copy English properties from the selected IQSS release.
    for source_file in files:
        shutil.copy2(source_file, TARGET / source_file.name)

    # Apply customizations after copying official resources.
    for override_file in sorted(OVERRIDES.glob("*.properties")):
        target_file = TARGET / override_file.name

        if not target_file.exists():
            raise ValueError(
                f"No IQSS source file for {override_file.name}"
            )

        overrides = parse_overrides(override_file)
        apply_overrides(target_file, overrides)

    for required in ("Bundle.properties", "citation.properties"):
        if not (TARGET / required).is_file():
            raise ValueError(f"Missing required file: {required}")

    print(
        f"Synchronized {len(files)} IQSS English properties files"
    )


if __name__ == "__main__":
    main()

