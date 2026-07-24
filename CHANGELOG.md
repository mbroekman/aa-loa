# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.0.6] - 2026-07-24

### Fixed

- Completely purged all remaining Bootstrap CSS variables from dark mode overrides that were causing white backgrounds on panel headings in themes like Darkly.

## [0.0.5] - 2026-07-24

### Fixed

- Replaced CSS variables with hardcoded hex colors to prevent themes from resolving fallbacks to white.
- Greatly increased CSS specificity for `.panel-title` classes to enforce colors over Alliance Auth base themes.

## [0.0.4] - 2026-07-24

### Fixed

- Added a cache-buster to the CSS stylesheet link to force browsers to load the new styling changes correctly on deployment.

## [0.0.3] - 2026-07-24

### Added

- Major UI overhaul of the HR Dashboard and Player Dashboard with modern Bootstrap 5 aesthetic.
- Introduced modern metric cards to filter active, upcoming, and processed Leave of Absences.
- Added comprehensive dark mode support compatible with legacy Alliance Auth themes (night, slate, darkly, cyborg).
- Added robust date validation (client-side and server-side) preventing manual text entry in date pickers.

### Fixed

- Fixed GitHub Actions workflows by updating deprecated action versions (checkout@v4, setup-python@v5).
- Fixed pre-commit stylelint configuration to allow empty input.

## [0.0.2] - 2026-07-24

### Added

- Added robust test suite with 100% backend test coverage using `tox` and Django `TestCase`.
- Integrated GitHub Actions workflows (`automated-checks.yml`, `release.yml`, `potential-duplicates.yml`) for automated CI/CD and PyPI Trusted Publishing.
- Added standard Alliance Auth pre-commit configuration (`flake8`, `black`, `isort`) for unified code formatting.

## [0.0.1] - 2026-07-24

### Added

- Initial release of the Leave of Absence module.
- Player dashboard to view, submit and revoke LOAs.
- HR dashboard to view all LOAs and proxy-submit on behalf of players.
- Webhook notifications to a Discord channel.
- Automatic Django Group assignment for players on an active LOA (syncs to Discord/TS).
- Daily Celery task to verify and clean up expired LOAs and send a Welcome Back message.
