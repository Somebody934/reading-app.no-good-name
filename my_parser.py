from sudachipy import tokenizer, dictionary


class Parser:
    def __init__(self):
        self.tokenizer = dictionary.Dictionary(dict_type="full").create()
        self.mode = tokenizer.Tokenizer.SplitMode.C
        self.dict = self.add_known()
    def parse_text(self, text: str):
        morphs = self.tokenizer.tokenize(text, self.mode)
        return morphs

    def parse_list(self, array: list):
        parsed_array = []
        for item in array:
            parsed_item = self.parse_text(item)
            parsed_array.append(parsed_item)
            dict = self.format_data(parsed_item)
            self.dict = {**dict, **self.dict}
        return parsed_array

    def format_data(self, morphs: list, known="not-known"):
        dict = {}
        for morph in morphs:
            dict[morph.dictionary_form()] = {
                "original": morph.dictionary_form(),
                "style": morph.part_of_speech()[1],
                "type": morph.part_of_speech()[0],
                "reading": self.tokenizer.tokenize(morph.dictionary_form(), self.mode)[0].reading_form(),
                "known": known,
            }
        return dict

    def add_known(self):
        with open("static/data/known_words.txt","r", encoding="utf-8") as file:
            text = file.read().replace("\n", " ")
            parsed_text = self.parse_text(text)
            dict = self.format_data(parsed_text, known="known")
        return dict


def config():
    to = dictionary.Dictionary(dict_type="full").create()
    mode = tokenizer.Tokenizer.SplitMode.A
    return to, mode


if __name__ == "__main__":
    to, mode = config()
    prs = Parser()
    prs.add_known()
    text = "頭は未だ何だか明瞭しない"
    text_list =[text]
    m = to.tokenize(text, mode)
    # print(prs.format_data(m))
    # for word in m:
    #     print(word.surface())
    #     print(word.part_of_speech())
    #     print(word.part_of_speech_id())
    #     print(word.dictionary_form())
    #     print(word.normalized_form())
    #     print(word.reading_form())
    #     print()
    print(prs.parse_text(text))
    print(prs.parse_list(text_list)[0])
    print()
