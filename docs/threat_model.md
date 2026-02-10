# Threat Model

## Attacker Goals
- extract system prompt / hidden rules
- force unsafe instructions
- bypass refusals via roleplay, authority, encoding, or multi-turn escalation
- inject malicious instructions via external content (HTML/PDF/email)
- induce hallucinated sources to create false authority

## Defender Goals
- maintain instruction hierarchy
- refuse unsafe requests cleanly
- avoid hallucination and false citations
- maintain schema and formatting constraints
