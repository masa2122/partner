import os
import deepl
from dotenv import load_dotenv

class Deepl():
    def __init__(self) -> None:
        self.lang_dict = {
            'je' : ['JA', 'EN-US'],
            'je2' : ['JA', 'EN-GB'],
            'ej' : ['EN','JA'],
            'j' : ['JA'],
        }
        load_dotenv('./.env')
        DEEPL_API_KEY = os.environ['DEEPL_API_KEY']
        self.translator = deepl.Translator(DEEPL_API_KEY)

    def transform(self,lang, text):
        la = self.lang_dict[lang]

        if len(la) == 1:
            result = self.translator.translate_text(text, target_lang=la[0])
        else:
            result = self.translator.translate_text(text, source_lang=la[0], target_lang=la[1])

        return result
