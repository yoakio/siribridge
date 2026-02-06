import plistlib
import os
import uuid

def generate_v3_pro():
    # Identifiers for common actions
    # Note: These are simplified for the demo
    actions = [
        # 1. Haptic Feedback (Success)
        {
            "WFWorkflowActionIdentifier": "is.workflow.actions.hapticfeedback",
            "WFWorkflowActionParameters": {
                "WFHapticFeedbackType": "Success"
            }
        },
        # 2. Dictate Text
        {
            "WFWorkflowActionIdentifier": "is.workflow.actions.dictatetext",
            "WFWorkflowActionParameters": {
                "WFSpeechLanguage": "zh-CN"
            }
        },
        # 3. Get Contents of URL (POST)
        {
            "WFWorkflowActionIdentifier": "is.workflow.actions.downloadurl",
            "WFWorkflowActionParameters": {
                "WFHTTPMethod": "POST",
                "WFURL": "https://siri-proxy.qybc.workers.dev/ask",
                "WFJSONValues": {
                    "Value": {
                        "WFSerializationType": "WFDictionaryPropertyValue",
                        "WFDictionaryFieldValueItems": [
                            {
                                "WFItemType": 0,
                                "WFKey": "text",
                                "WFValue": {"Value": {"Type": "ActionOutput", "OutputName": "Dictated Text"}, "WFSerializationType": "WFTextTokenString"}
                            }
                        ]
                    }
                }
            }
        },
        # 4. Speak Text
        {
            "WFWorkflowActionIdentifier": "is.workflow.actions.speaktext",
            "WFWorkflowActionParameters": {
                "WFSpeakTextText": {"Value": {"Type": "ActionOutput", "OutputName": "Contents of URL"}, "WFSerializationType": "WFTextTokenString"}
            }
        }
    ]

    shortcut = {
        "WFWorkflowActions": actions,
        "WFWorkflowClientVersion": "1401.4.48",
        "WFWorkflowIcon": {
            "WFWorkflowIconStartColor": 4283730431,
            "WFWorkflowIconGlyphNumber": 59511
        },
        "WFWorkflowInputContentItemClasses": [
            "WFAppStoreAppContentItem",
            "WFArticleContentItem",
            "WFContactContentItem",
            "WFDateContentItem",
            "WFEmailAddressContentItem",
            "WFFaceTimeContentItem",
            "WFGenericFileContentItem",
            "WFImageContentItem",
            "WFiTunesProductContentItem",
            "WFLocationContentItem",
            "WFMapsLinkContentItem",
            "WFParkingContentItem",
            "WFPhoneNumberContentItem",
            "WFRichTextContentItem",
            "WFSafariWebPageContentItem",
            "WFURLContentItem"
        ],
        "WFWorkflowMinimumCompatibilityVersion": 900,
        "WFWorkflowTypes": ["NCWidget", "Watch"]
    }

    output_path = "/Users/am/clawd/SiriBridge/assets/问贾维斯_V3_Pro_Unsigned.shortcut"
    with open(output_path, "wb") as f:
        plistlib.dump(shortcut, f)
    
    print(output_path)

if __name__ == "__main__":
    generate_v3_pro()
