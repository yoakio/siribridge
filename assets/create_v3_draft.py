import plistlib
import os

def generate_old_format():
    # Use a known structure that Shortcuts app can import and upgrade
    shortcut = {
        "WFWorkflowActions": [
            # 1. Receive Input / Magic Link
            {
                "WFWorkflowActionIdentifier": "is.workflow.actions.gettext",
                "WFWorkflowActionParameters": {
                    "WFTextActionText": "Config Receiver Layer"
                }
            },
            # 2. Haptic Feedback
            {
                "WFWorkflowActionIdentifier": "is.workflow.actions.hapticfeedback",
                "WFWorkflowActionParameters": {
                    "WFHapticFeedbackType": "Success"
                }
            },
            # 3. Dictate
            {
                "WFWorkflowActionIdentifier": "is.workflow.actions.dictatetext",
                "WFWorkflowActionParameters": {
                    "WFSpeechLanguage": "zh-CN"
                }
            },
            # 4. Speak
            {
                "WFWorkflowActionIdentifier": "is.workflow.actions.speaktext",
                "WFWorkflowActionParameters": {
                    "WFSpeakTextText": "Jarvis Online"
                }
            }
        ],
        "WFWorkflowClientVersion": "1401.4.48",
        "WFWorkflowIcon": {
            "WFWorkflowIconStartColor": 4283730431,
            "WFWorkflowIconGlyphNumber": 59511
        }
    }
    
    path = "/Users/am/clawd/SiriBridge/assets/Jarvis_V3_Draft.shortcut"
    with open(path, "wb") as f:
        plistlib.dump(shortcut, f)
    return path

if __name__ == "__main__":
    print(generate_old_format())
