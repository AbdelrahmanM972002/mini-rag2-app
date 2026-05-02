import os
import importlib


class TemplateParser:

    def __init__(self, language: str = None, default_language='en'):
        self.current_path = os.path.dirname(os.path.abspath(__file__))
        self.default_language = default_language
        self.language = None
        self.set_language(language)

    def set_language(self, language: str):
        target_lang = language if language else self.default_language

        language_path = os.path.join(self.current_path, "locales", target_lang)

        if os.path.exists(language_path):
            self.language = target_lang
        else:
            self.language = self.default_language

    def get(self, group: str, key: str, vars: dict = None):
        if vars is None:
            vars = {}

        if not group or not key:
            return None

        try:
            # ✅ import correct module way
            module_path = f"stores.llm.templates.locales.{self.language}.{group}"
            module = importlib.import_module(module_path)

            template_obj = getattr(module, key, None)

            if template_obj is None:
                return None

            return template_obj.safe_substitute(vars)

        except Exception as e:
            print(f"DEBUG: Template Error -> {e}")
            return None