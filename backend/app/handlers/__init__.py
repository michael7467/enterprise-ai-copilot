from app.handlers import direct, knowledge_base, placeholders, uploaded_file

HANDLERS = {
    "direct": direct.handle,
    "knowledge_base": knowledge_base.handle,
    "uploaded_file": uploaded_file.handle,
    "vision": placeholders.vision,
}
