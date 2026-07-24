# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.0.1] - 2026-07-24

### Added

- Initial release of the Leave of Absence module.
- Player dashboard to view, submit and revoke LOAs.
- HR dashboard to view all LOAs and proxy-submit on behalf of players.
- Webhook notifications to a Discord channel.
- Automatic Django Group assignment for players on an active LOA (syncs to Discord/TS).
- Daily Celery task to verify and clean up expired LOAs and send a Welcome Back message.
