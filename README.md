# Home Assistant Pi Control Integration

This custom component calls the Pi Control Service to reboot the Pi, read/write `/boot/fullpageos.txt`, and run SSH commands.

## Install

### HACS (recommended)

1. HACS → Integrations → Custom repositories → add this repo URL.
2. Category: **Integration**.
3. Install **Pi Control** and restart Home Assistant.
4. Settings → Devices & Services → Add Integration → **Pi Control**.

### Native (no HACS)

1. Copy `custom_components/picontrol` into your Home Assistant config directory.
2. Restart Home Assistant.

## Configuration

Add to `configuration.yaml`:

```yaml
picontrol:
  host: 192.168.1.50
  port: 8129
  ssl: false
  token: "CHANGE_ME"
```

YAML is optional if you prefer UI setup.

## Services

- `picontrol.reboot`
- `picontrol.get_fullpageos` (writes state `picontrol.fullpageos`)
- `picontrol.set_fullpageos` (field: `content`)
- `picontrol.run_ssh` (fields: `host`, `command`, optional `user`, `port`, `identity_file`)

## Entities

The integration adds a `Pi Control Status` sensor so the device shows up in the UI.
