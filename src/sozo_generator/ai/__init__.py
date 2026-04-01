"""AI layer — LLM-powered chat, intent parsing, and document composition.

SAFETY RULE: The AI layer NEVER generates clinical content, PMIDs, or
treatment recommendations. It only interprets user intent and routes
to the verified generation pipeline.
"""
