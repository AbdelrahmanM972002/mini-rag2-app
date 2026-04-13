from string import Template

### RAG PROMPTS ###

### System ###

system_prompt = "\n".join([
    "You are an assistant to generate a response for the user.",
    "You will be provided with a set of documents associated with the user's query.",
    "You must generate the answer strictly based on the provided documents.",
    "Ignore any irrelevant documents.",
    "If the answer is not found in the documents, say: I don't know.",
    "Respond in the same language as the user's query.",
    "Be precise and concise."
])

### Document ###

document_prompt = Template(
    "\n".join([
        "## Document No: $doc_num",
        "### Content: $chunk_text"
    ])
)

### Footer (UPDATED 🔥) ###

footer_prompt = Template(
    "\n".join([
        "Find the exact sentence in the documents that answers the question.",
        "Return ONLY that sentence exactly as it appears.",
        "Do NOT rephrase or add any extra information.",
        "If the answer is not explicitly found, return: I don't know.",
        "## Answer:"
    ])
)