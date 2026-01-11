# RF Remote Lamp

A Home Assistant custom integration for controlling RF lamps through remote entities.

## Features

- Control RF lamps that only have a toggle command
- Tracks assumed state (persisted across restarts)
- Integrates with any Home Assistant remote entity
- Simple UI configuration

## Configuration

1. Go to **Settings** → **Devices & Services**
2. Click **+ Add Integration**
3. Search for "RF Remote Lamp"
4. Fill in:
   - **Lamp Name**: Display name for your lamp
   - **Remote Entity**: Your remote entity (e.g., `remote.living_room`)
   - **Device Name**: Device name as configured in your remote
