# Changelog

All notable changes to this project will be documented in this file.

## [0.3.1]

# Bug Fixes

- Fixed `merge` type not being recognised.

## [0.3.0]

### Changes

- **Breaking Change** – removed `track`, `album`, `playlist`, and `multi`
  commands. All three cases are now handled by specifying a `type` field in the
  TOML file.
- **Breaking Change** – changed TOML file format – all cases are now handled by
  a single file type. See documentation for more.
- Added schema validation for TOML files.

## [0.2.0]

### Additions

- Added multi-track type

### Changes

- `start` and `end` track class parameters have moved and now have default None
  values (**potentially breaking change**)

## [0.1.1]

### Additions

- Simple schema validation on required TOML fields
- Humorous cows
- Backoff/Retries on requests that seem to occasionally fail

[0.3.1]: https://github.com/James-Ansley/pytubemusic/compare/v0.3.0...v0.3.1

[0.3.0]: https://github.com/James-Ansley/pytubemusic/compare/v0.2.0...v0.3.0

[0.2.0]: https://github.com/James-Ansley/pytubemusic/compare/v0.1.1...v0.2.0

[0.1.1]: https://github.com/James-Ansley/pytubemusic/compare/v0.0.1-alpha.1...v0.1.1
