import plistlib
import os

def create_shortcut():
    # Basic shortcut structure
    shortcut = {
        "WFWorkflowActions": [
            {
                "WFWorkflowActionIdentifier": "is.workflow.actions.gettext",
                "WFWorkflowActionParameters": {
                    "WFTextActionText": "SiriBridge v3 Pro v2026.02.05"
                }
            },
            {
                "WFWorkflowActionIdentifier": "is.workflow.actions.hapticfeedback",
                "WFWorkflowActionParameters": {
                    "WFHapticFeedbackType": "Success"
                }
            }
        ],
        "WFWorkflowClientVersion": "1401.4.48",
        "WFWorkflowIcon": {
            "WFWorkflowIconStartColor": 4283730431,
            "WFWorkflowIconGlyphNumber": 59511
        },
        "WFWorkflowTypes": ["NCWidget", "Watch"]
    }
    
    with open("/Users/am/clawd/SiriBridge/assets/v3_factory_test.plist", "wb") as f:
        plistlib.dump(shortcut, f)

if __name__ == "__main__":
    create_shortcut()
