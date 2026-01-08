#!/usr/bin/env python3
"""
Analyze simulation HTML to extract game master events and check for variable update triggers.
"""
import re
import sys
from pathlib import Path

def extract_events_from_html(html_path: str):
    """Extract game master events from HTML file."""
    with open(html_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find all game master events
    # Pattern: Step X City Council Moderator --- Event: **text**
    pattern = r'Step (\d+) City Council Moderator --- Event: \*\*(.*?)\*\*'
    matches = re.findall(pattern, content, re.DOTALL)

    events = []
    for step, event_text in matches:
        # Clean up the text
        event_text = event_text.replace('<br />', ' ').strip()
        events.append({
            'step': int(step),
            'text': event_text
        })

    return events

def check_for_variable_triggers(events: list):
    """Check if events contain grounded variable update triggers."""
    variable_keywords = {
        'median_monthly_rent': ['rent', 'housing cost', 'lease', 'landlord'],
        'low_income_displacement_rate': ['displaced', 'forced out', 'evicted', 'left', 'moved away'],
        'small_business_survival_rate': ['business closed', 'shop shut', 'store closed', 'went out of business'],
        'community_cohesion_index': ['community', 'neighbor', 'cohesion', 'togetherness'],
        'property_tax_base': ['property value', 'tax base', 'assessment', 'property worth'],
        'new_housing_units_permitted': ['approved', 'permitted', 'development approved', 'zoning'],
        'affordable_housing_units': ['affordable housing', 'low-income housing', 'subsidy'],
        'housing_affordability_index': ['affordable', 'rent burden', 'cost burden'],
        'rent_control_active': ['rent control', 'rent stabilization', 'cap rent'],
        'inclusionary_zoning_active': ['inclusionary zoning', 'affordable requirement', 'mandatory affordable'],
        'neighborhood_character': ['neighborhood character', 'gentrify', 'upscale', 'working class']
    }

    results = []
    for event in events:
        triggers_found = []
        for var_name, keywords in variable_keywords.items():
            for keyword in keywords:
                if keyword.lower() in event['text'].lower():
                    triggers_found.append(f"{var_name} (keyword: '{keyword}')")

        if triggers_found:
            results.append({
                'step': event['step'],
                'event': event['text'][:200] + '...' if len(event['text']) > 200 else event['text'],
                'triggers': triggers_found
            })

    return results

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python analyze_simulation.py <html_file>")
        sys.exit(1)

    html_path = sys.argv[1]
    print(f"Analyzing: {html_path}\n")

    events = extract_events_from_html(html_path)
    print(f"Found {len(events)} game master events\n")

    if not events:
        print("No events found!")
        sys.exit(0)

    print("All Events:")
    print("=" * 80)
    for event in events:
        print(f"\nStep {event['step']}:")
        print(f"  {event['text'][:300]}")

    print("\n\n")
    print("Variable Update Triggers Detected:")
    print("=" * 80)

    triggers = check_for_variable_triggers(events)
    if not triggers:
        print("No potential variable update triggers found in events.")
        print("\nThis explains why grounded variables aren't changing - the events don't")
        print("contain explicit enough language to trigger the LLM to update variables.")
    else:
        for result in triggers:
            print(f"\nStep {result['step']}:")
            print(f"  Event: {result['event'][:100]}...")
            print(f"  Potential triggers:")
            for trigger in result['triggers']:
                print(f"    - {trigger}")
