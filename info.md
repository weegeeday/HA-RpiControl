# Pi Control

Use this custom integration to reboot the Pi, read/write `/boot/firmware/fullpageos.txt`, and run SSH commands via the Pi Control Service.

## Install with HACS

1. In HACS, add this repository as a custom repository (Category: Integration).
2. Install **Pi Control**.
3. Restart Home Assistant.

## Configure

```yaml
picontrol:
  host: 192.168.1.50
  port: 8129
  ssl: false
  token: "CHANGE_ME"
```

## Services

- `picontrol.reboot`
- `picontrol.get_fullpageos`
- `picontrol.set_fullpageos`
- `picontrol.run_ssh`
