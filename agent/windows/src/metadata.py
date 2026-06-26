# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 CyberProff.no and contributors.
# This file is part of CyberKey.

"""Project identity metadata for CyberKey."""

PROJECT_NAME = "CyberKey"
PROJECT_VERSION = "0.1.0"
PROJECT_ORIGIN = "CyberProff.no"
PROJECT_REPOSITORY = "https://github.com/cyberproff-no/cyberkey"
LICENSE_IDENTIFIER = "GPL-3.0-or-later"


def format_startup_banner() -> str:
    """Return a concise project origin and license banner."""

    return (
        f"{PROJECT_NAME} {PROJECT_VERSION}\n"
        f"Original project: {PROJECT_ORIGIN}\n"
        f"Source: {PROJECT_REPOSITORY}\n"
        f"License: {LICENSE_IDENTIFIER}"
    )
