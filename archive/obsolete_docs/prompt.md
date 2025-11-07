Analyze the following sentence and extract components based ONLY on the provided specialized Organizational Process/Quality Model. Adhere strictly to the entity types, naming rules, and final JSON structure provided below.

**I think our sales predictions are unreliable because everyone in the sales team hates to document their calls in the CRM.**

## Specialized Model Constraints:

1.  Entity Types (Only these five are valid):
    * Output: The final product (e.g., 'Customer Record').
    * Output Quality: A measurable quality of one specific Output (e.g., 'Data Quality').
    * Persona: An archetype representing a group of people (e.g., 'Sales Rep').
    * Process Step: A procedure a Persona follows to create an Output in a Tool (e.g., 'Record Lead Info Step').
    * Tool: A system or framework that the Persona uses (e.g., 'CRM System').

2.  Naming and Ambiguity Rules (Strictly Enforced):
    * Full Naming: The Output Quality entity name MUST include the name of the related Persona (e.g., "Sales Team Persona-Induced Data Quality of Unnamed Output").
    * Ambiguity Flagging: If an entity (like 'Output' or 'Process') is implied but not explicitly named, use the flag "Unnamed" in its name (e.g., "Unnamed Output in CRM", "Documentation Step of an Unnamed Process").
    * No Enrichment: Do not include any descriptions or unmentioned attributes in the entity names.

3.  Relationship Rules (Strictly Enforced and Updated):
    * Mandatory Fields: Both relationship_quality and relationship_description are mandatory for every captured relationship.
    * Quality Capture: Use the relationship_quality field for the overall assessment/sentiment:
        * If a quality/sentiment is explicitly mentioned (eg., "bad," "good," "hates," "slow"), use that specific word.
        * If no quality is mentioned, use the exact string "n/a".
    * Description Capture: Use the relationship_description field to capture the specific linking phrase or context used in the sentence (e.g., "document their calls," "are unreliable," "in the CRM").

## Task Output Format (Strict JSON):
Generate a single JSON object with two top-level arrays: entities and relationships.

```json
{
  "entities": [
    {"type": "[Type]", "name": "[Specific Name]"},
    // ... all extracted entities
  ],
  "relationships": [
    {
      "source_entity_name": "[Name]", 
      "target_entity_name": "[Name]", 
      "relationship_quality": "[explicit word or n/a]", 
      "relationship_description": "[Specific linking phrase/context]"
    }
    // ... all extracted relationships
  ]
}
```