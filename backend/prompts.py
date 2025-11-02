# backend/prompts.py

def get_base_instruction():
    """Get base instruction for the Argusa AI Challenge bot."""
    # Focus solely on answering questions based on the provided context from GreenHorizon documents.
    # Emphasize extracting specific details like names, roles, file locations, etc., when relevant.
    return """You are an AI assistant designed to answer questions based on the GreenHorizon company documents provided in the 'Context' section below.
            Your answers should be accurate, concise, and directly derived from the information contained within the context.
            When asked to list items (e.g., projects, people, files), provide a clear, structured list based on the context.
            When asked about specific individuals, roles, or file locations, extract and state them clearly if present in the context.
            If the context does not contain sufficient information to answer the question, state so clearly.
            Do not fabricate information or rely on prior knowledge outside the provided context.
            Format your answer appropriately (e.g., use line breaks for lists)."""


def get_language_instruction(language):
    """Get language-specific instruction (if needed, though context is likely English)."""
    # For now, assume context and answers are in English.
    # This could be adapted if multilingual documents/questions are introduced.
    if language == 'en':
        return "Please provide your answer in English based on the context."
    # Add other languages if required later
    # elif language == 'de':
    #    return "Bitte beantworten Sie die Frage auf Deutsch basierend auf dem Kontext."
    else:
        # Default to English if language is unknown or not specified
        return "Please provide your answer in English based on the context."
