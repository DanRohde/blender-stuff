import bpy
if bpy.app.version >= (4, 3, 0):
    PRIORITY_ICONS = {
        "low" : "NODE_SOCKET_FLOAT",
        "normal" : "NODE_SOCKET_COLLECTION",
        "high" : "NODE_SOCKET_MATRIX",
    }
else:
    PRIORITY_ICONS = {
        "low": "SEQUENCE_COLOR_05",
        "normal": "SEQUENCE_COLOR_04",
        "high": "SEQUENCE_COLOR_01",
    }
PRIORITIES = [("high", "High", "High Priority", PRIORITY_ICONS["high"],2),
              ("normal", "Normal", "Normal Priority", PRIORITY_ICONS["normal"],1),
              ("low", "Low", "Low Priority", PRIORITY_ICONS["low"],0)]