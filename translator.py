# -*- coding: utf-8 -*-
import json
import os


class Translator(object):
    class LanguageNotFound(Exception):
        pass

    class StringNotTranslated(Exception):
        pass

    def __init__(self, language='de', base_path='.'):
        self.lang = language
        self.base_path = base_path
        try:
            with open(os.path.join(self.base_path, "strings", "strings_" + str(self.lang)) + '.json', 'r') as f:
                self.strings = json.load(f)
        except FileNotFoundError:
            raise self.LanguageNotFound(
                "Language \"{}\" was not found. The translation is misssing.".format(self.lang))
        except json.JSONDecodeError:
            raise self.LanguageNotFound("The translation file was found but it is not in valid JSON.")

    def __getitem__(self, string):
        if string in self.strings.keys() and type(self.strings[string]) is str:
            return self.strings[string]
        else:
            self.strings[string] = None
            with open(os.path.join(self.base_path, "strings", "strings_" + str(self.lang)) + '.json', 'w') as f:
                json.dump(self.strings, f, indent=2, sort_keys=True)
            raise self.StringNotTranslated(
                "The String \"{}\" was not found.".format(string) +
                " Please translate it. An empty translation was created.")

    def __getattr__(self, string):
        return self[string]

