# RF Remote Lamp

[![GitHub Release][releases-shield]][releases]
[![GitHub Activity][commits-shield]][commits]
[![License][license-shield]](LICENSE)

[![hacs][hacsbadge]][hacs]
[![Project Maintenance][maintenance-shield]][user_profile]

A Home Assistant custom integration for controlling RF lamps through remote entities (like Broadlink).

## Features

- Control RF lamps that only have a toggle command
- Tracks assumed state (persisted across restarts)
- Integrates with any Home Assistant remote entity
- Simple UI configuration

## How it works

RF remotes are typically one-way communication devices - they send commands but don't receive feedback. This integration:

1. Maintains an "assumed state" for each lamp
2. Only sends toggle commands when the state actually needs to change
3. Persists the assumed state across Home Assistant restarts

## Installation

### HACS (Recommended)

1. Open HACS in Home Assistant
2. Click on "Integrations"
3. Click the three dots in the top right corner and select "Custom repositories"
4. Add `https://github.com/leoleoasd/rf-remote-lamp` with category "Integration"
5. Click "Install"
6. Restart Home Assistant

### Manual Installation

1. Copy the `custom_components/rf_remote_lamp` directory to your Home Assistant's `custom_components` directory
2. Restart Home Assistant

## Configuration

1. Go to **Settings** → **Devices & Services**
2. Click **+ Add Integration**
3. Search for "RF Remote Lamp"
4. Fill in the configuration:
   - **Lamp Name**: The display name for your lamp (e.g., "Living Room Lamp")
   - **Remote Entity**: Select your remote entity (e.g., `remote.living_room`)
   - **Device Name**: The device name as configured in your remote (e.g., "living room lamp")

## Example

If you previously had a template light like this:

```yaml
template:
  - light:
      - name: Living Room Lamp
        unique_id: living_room_lamp_light
        state: "{{ is_state('input_boolean.input_boolean_living_room_light_state', 'on') }}"
        turn_on:
          - condition: state
            entity_id: input_boolean.input_boolean_living_room_light_state
            state: "off"
          - service: input_boolean.turn_on
            target:
              entity_id: input_boolean.input_boolean_living_room_light_state
          - service: remote.send_command
            target:
              entity_id: remote.living_room
            data:
              device: "living room lamp"
              command: "toggle"
        turn_off:
          - condition: state
            entity_id: input_boolean.input_boolean_living_room_light_state
            state: "on"
          - service: input_boolean.turn_off
            target:
              entity_id: input_boolean.input_boolean_living_room_light_state
          - service: remote.send_command
            target:
              entity_id: remote.living_room
            data:
              device: "living room lamp"
              command: "toggle"
```

You can replace it with this integration by configuring:

- **Lamp Name**: `Living Room Lamp`
- **Remote Entity**: `remote.living_room`
- **Device Name**: `living room lamp`

## Contributions are welcome!

If you want to contribute to this please read the [Contribution guidelines](CONTRIBUTING.md)

---

[commits-shield]: https://img.shields.io/github/commit-activity/y/leoleoasd/rf-remote-lamp.svg?style=for-the-badge
[commits]: https://github.com/leoleoasd/rf-remote-lamp/commits/main
[hacs]: https://hacs.xyz
[hacsbadge]: https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge
[license-shield]: https://img.shields.io/github/license/leoleoasd/rf-remote-lamp.svg?style=for-the-badge
[maintenance-shield]: https://img.shields.io/badge/maintainer-%40leoleoasd-blue.svg?style=for-the-badge
[releases-shield]: https://img.shields.io/github/release/leoleoasd/rf-remote-lamp.svg?style=for-the-badge
[releases]: https://github.com/leoleoasd/rf-remote-lamp/releases
[user_profile]: https://github.com/leoleoasd
