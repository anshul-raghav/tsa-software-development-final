PANELMAP_SCHEMA = """{
  "panel_id": "string (use provided scan_id)",
  "appliance_type": "string (e.g. microwave, thermostat, washer, vending, oven, unknown)",
  "scan_confidence": "float 0-1",
  "panel_bbox": {"x1": 0.0, "y1": 0.0, "x2": 1.0, "y2": 1.0},
  "orientation": "portrait | landscape",
  "regions": [
    {
      "id": "string (e.g. number_pad, action_column)",
      "label": "string (human-readable name)",
      "bbox": {"x1": "float", "y1": "float", "x2": "float", "y2": "float"},
      "control_ids": ["string array of control ids in this region"],
      "description": "string"
    }
  ],
  "controls": [
    {
      "id": "string (e.g. ctrl_start, ctrl_1)",
      "label": "string (the text on the button)",
      "aliases": ["string array of alternative names"],
      "type": "action | number | mode | setting | dial | toggle | confirm | cancel | display | other",
      "bbox": {"x1": "float 0-1", "y1": "float 0-1", "x2": "float 0-1", "y2": "float 0-1"},
      "region_id": "string | null",
      "is_primary_action": "boolean",
      "confidence": "float 0-1",
      "spoken_description": "string (e.g. 'Start is in the bottom-right corner')"
    }
  ],
  "landmarks": [
    {
      "id": "string",
      "label": "string",
      "bbox": {"x1": "float", "y1": "float", "x2": "float", "y2": "float"},
      "description": "string"
    }
  ],
  "global_description": "string (1-2 sentence description of the overall panel layout)"
}"""


def build_panelmap_prompt(ocr_context: str) -> str:
    return f"""You are a control panel analysis system for the TouchMap accessibility app.

Your job is to analyze an image of a flat control panel and return a STRICT JSON object
describing every control, region, and landmark on the panel.

Determine the appliance type from your visual analysis of the panel image.

OCR SIGNALS (use these as hints, but trust your visual analysis more for layout):
{ocr_context}

REQUIRED OUTPUT SCHEMA:
{PANELMAP_SCHEMA}

CRITICAL RULES:
1. All bounding box coordinates MUST be normalized floats from 0.0 to 1.0, relative to the panel image.
   (0,0) is top-left, (1,1) is bottom-right.
2. Every visible button, number, dial, toggle, or interactive element must be a separate control.
3. Group related controls into regions (e.g., number_pad, action_buttons, settings_row).
4. Assign control types accurately: numbers are "number", Start/Stop are "action", Defrost/Reheat are "mode".
5. Mark primary action buttons (Start, Stop, Cancel) with is_primary_action=true.
6. Include spoken_description for each control describing its spatial position in plain language.
7. Include landmarks for non-interactive visual elements (display screen, dividers, brand logo).
8. The global_description should be 1-2 sentences summarizing the panel layout.

Return ONLY valid JSON matching the schema. No markdown, no explanation, no commentary."""
