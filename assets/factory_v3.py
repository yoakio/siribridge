import plistlib
import uuid

def generate_v3_pro():
    # Helper to create UUIDs for variables
    def get_uuid():
        return str(uuid.uuid4()).upper()

    input_uuid = get_uuid()
    url_result_uuid = get_uuid()
    config_file_uuid = get_uuid()
    key_uuid = get_uuid()
    url_uuid = get_uuid()
    dictate_uuid = get_uuid()
    reply_uuid = get_uuid()
    continue_uuid = get_uuid()

    actions = [
        # --- PHASE 1: MAGIC LINK RECEIVER ---
        {
            "WFWorkflowActionIdentifier": "is.workflow.actions.gettext",
            "WFWorkflowActionParameters": {
                "WFTextActionText": {"Value": {"Type": "ExtensionInput"}, "WFSerializationType": "WFTextTokenString"},
                "UUID": input_uuid
            }
        },
        {
            "WFWorkflowActionIdentifier": "is.workflow.actions.conditional",
            "WFWorkflowActionParameters": {
                "WFControlFlowMode": 0,
                "WFCondition": 4, # Has Any Value
                "WFVariable": {"Value": {"OutputUUID": input_uuid, "Type": "ActionOutput"}, "WFSerializationType": "WFTextTokenString"}
            }
        },
        {
            "WFWorkflowActionIdentifier": "is.workflow.actions.base64encode",
            "WFWorkflowActionParameters": {
                "WFBase64LineBreakMode": "None",
                "WFBase64EncodeMode": "Decode",
                "WFInput": {"Value": {"OutputUUID": input_uuid, "Type": "ActionOutput"}, "WFSerializationType": "WFTextTokenString"}
            }
        },
        {
            "WFWorkflowActionIdentifier": "is.workflow.actions.documentpicker.save",
            "WFWorkflowActionParameters": {
                "WFFileDestinationPath": "RickAI/config.json",
                "WFAskWhereToSave": False,
                "WFSaveFileOverwrite": True
            }
        },
        {
            "WFWorkflowActionIdentifier": "is.workflow.actions.notification",
            "WFWorkflowActionParameters": {
                "WFNotificationActionBody": "✅ 贾维斯配置同步成功！"
            }
        },
        {
            "WFWorkflowActionIdentifier": "is.workflow.actions.exit",
            "WFWorkflowActionParameters": {}
        },
        {
            "WFWorkflowActionIdentifier": "is.workflow.actions.conditional",
            "WFWorkflowActionParameters": {
                "WFControlFlowMode": 1 # Otherwise
            }
        },
        # --- PHASE 2: LOAD CONFIG ---
        {
            "WFWorkflowActionIdentifier": "is.workflow.actions.file",
            "WFWorkflowActionParameters": {
                "WFFile": {
                    "fileLocation": {
                        "relativeSubpath": "RickAI/config.json",
                        "WFFileLocationType": "iCloud"
                    }
                },
                "UUID": config_file_uuid
            }
        },
        {
            "WFWorkflowActionIdentifier": "is.workflow.actions.getvalueforkey",
            "WFWorkflowActionParameters": {
                "WFDictionaryKey": "url",
                "WFInput": {"Value": {"OutputUUID": config_file_uuid, "Type": "ActionOutput"}, "WFSerializationType": "WFTextTokenString"},
                "UUID": url_uuid
            }
        },
        {
            "WFWorkflowActionIdentifier": "is.workflow.actions.getvalueforkey",
            "WFWorkflowActionParameters": {
                "WFDictionaryKey": "key",
                "WFInput": {"Value": {"OutputUUID": config_file_uuid, "Type": "ActionOutput"}, "WFSerializationType": "WFTextTokenString"},
                "UUID": key_uuid
            }
        },
        # --- PHASE 3: CORE INTERACTION ---
        {
            "WFWorkflowActionIdentifier": "is.workflow.actions.hapticfeedback",
            "WFWorkflowActionParameters": {
                "WFHapticFeedbackType": "Selection"
            }
        },
        {
            "WFWorkflowActionIdentifier": "is.workflow.actions.dictatetext",
            "WFWorkflowActionParameters": {
                "WFSpeechLanguage": "zh-CN",
                "WFDictateTextStopListening": "After Short Pause",
                "UUID": dictate_uuid
            }
        },
        {
            "WFWorkflowActionIdentifier": "is.workflow.actions.downloadurl",
            "WFWorkflowActionParameters": {
                "WFHTTPMethod": "POST",
                "WFURL": {"Value": {"OutputUUID": url_uuid, "Type": "ActionOutput"}, "WFSerializationType": "WFTextTokenString"},
                "WFHTTPHeaders": {
                    "Value": {
                        "WFDictionaryFieldValueItems": [
                            {
                                "WFItemType": 0,
                                "WFKey": "Authorization",
                                "WFValue": {"Value": {"attachmentsByRange": {"{7, 1}": {"OutputUUID": key_uuid, "Type": "ActionOutput"}}, "string": "Bearer "}, "WFSerializationType": "WFTextTokenString"}
                            }
                        ]
                    }
                },
                "WFHTTPBodyType": "JSON",
                "WFJSONValues": {
                    "Value": {
                        "WFDictionaryFieldValueItems": [
                            {
                                "WFItemType": 0,
                                "WFKey": "text",
                                "WFValue": {"Value": {"OutputUUID": dictate_uuid, "Type": "ActionOutput"}, "WFSerializationType": "WFTextTokenString"}
                            }
                        ]
                    }
                },
                "UUID": url_result_uuid
            }
        },
        # --- PHASE 4: FEEDBACK & LOOP ---
        {
            "WFWorkflowActionIdentifier": "is.workflow.actions.getvalueforkey",
            "WFWorkflowActionParameters": {
                "WFDictionaryKey": "reply",
                "WFInput": {"Value": {"OutputUUID": url_result_uuid, "Type": "ActionOutput"}, "WFSerializationType": "WFTextTokenString"},
                "UUID": reply_uuid
            }
        },
        {
            "WFWorkflowActionIdentifier": "is.workflow.actions.getvalueforkey",
            "WFWorkflowActionParameters": {
                "WFDictionaryKey": "continue",
                "WFInput": {"Value": {"OutputUUID": url_result_uuid, "Type": "ActionOutput"}, "WFSerializationType": "WFTextTokenString"},
                "UUID": continue_uuid
            }
        },
        {
            "WFWorkflowActionIdentifier": "is.workflow.actions.hapticfeedback",
            "WFWorkflowActionParameters": {
                "WFHapticFeedbackType": "Success"
            }
        },
        {
            "WFWorkflowActionIdentifier": "is.workflow.actions.speaktext",
            "WFWorkflowActionParameters": {
                "WFSpeakTextText": {"Value": {"OutputUUID": reply_uuid, "Type": "ActionOutput"}, "WFSerializationType": "WFTextTokenString"},
                "WFSpeakTextWait": True
            }
        },
        {
            "WFWorkflowActionIdentifier": "is.workflow.actions.conditional",
            "WFWorkflowActionParameters": {
                "WFControlFlowMode": 0,
                "WFCondition": 4, # Is True / Has Value
                "WFVariable": {"Value": {"OutputUUID": continue_uuid, "Type": "ActionOutput"}, "WFSerializationType": "WFTextTokenString"}
            }
        },
        {
            "WFWorkflowActionIdentifier": "is.workflow.actions.runworkflow",
            "WFWorkflowActionParameters": {
                "WFWorkflowName": "问贾维斯"
            }
        },
        {
            "WFWorkflowActionIdentifier": "is.workflow.actions.conditional",
            "WFWorkflowActionParameters": {
                "WFControlFlowMode": 2 # End If
            }
        },
        {
            "WFWorkflowActionIdentifier": "is.workflow.actions.conditional",
            "WFWorkflowActionParameters": {
                "WFControlFlowMode": 2 # End If
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
        "WFWorkflowInputContentItemClasses": ["WFTextContentItem", "WFURLContentItem"],
        "WFWorkflowMinimumCompatibilityVersion": 900,
        "WFWorkflowTypes": ["NCWidget", "Watch", "ActionExtension"]
    }

    path = "/tmp/Jarvis_v3_Pro.shortcut"
    with open(path, "wb") as f:
        plistlib.dump(shortcut, f)
    print(path)

if __name__ == "__main__":
    generate_v3_pro()
