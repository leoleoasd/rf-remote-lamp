"""Constants for RF Remote Lamp."""

DOMAIN = "rf_remote_lamp"
VERSION = "1.0.0"

# Platforms
PLATFORMS = ["light"]

# Configuration keys
CONF_REMOTE_ENTITY = "remote_entity"
CONF_DEVICE_NAME = "device_name"
CONF_LAMP_NAME = "lamp_name"
CONF_BRIGHTNESS_LEVELS = "brightness_levels"
CONF_CCT_LEVELS = "cct_levels"

# Commands
CMD_TOGGLE = "toggle"
CMD_BRIGHTNESS_UP = "brightness_up"
CMD_BRIGHTNESS_DOWN = "brightness_down"
CMD_CCT_TOGGLE = "cct_toggle"

# Color temperature range (in Kelvin)
# Level 1 = warm (2700K), Level max = cool (6500K)
CCT_MIN_KELVIN = 2700
CCT_MAX_KELVIN = 6500
