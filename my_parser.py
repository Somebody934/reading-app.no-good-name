from sudachipy import tokenizer, dictionary

from cloud_storage import upload_file, read_file


class Parser:
    def __init__(self):
        self.tokenizer = dictionary.Dictionary(dict_type="full").create()
        self.mode = tokenizer.Tokenizer.SplitMode.C
        self.dict = {}

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

    def parse_known(self, user_id, data=None, known="known"):
        if data is None:
            path = "data/known.txt"
            data = read_file(user_id=user_id, path=path).get("known")
            if data is None:
                return {}
        text = data.replace("\n", " ")
        parsed_text = self.parse_text(text)
        dict = self.format_data(parsed_text, known=known)
        return dict

    def add_known(self, user_id, data=None, known="known"):
        self.dict = {**self.dict, **self.parse_known(user_id, data, known)}
        file = "\n".join([key for (key, value) in self.dict.items() if value["known"] == "known"])
        path = "data/known.txt"
        upload_file(user_id=user_id, text=file, path=path)


def config():
    to = dictionary.Dictionary(dict_type="full").create()
    mode = tokenizer.Tokenizer.SplitMode.A
    return to, mode


if __name__ == "__main__":
    to, mode = config()
    prs = Parser()
    text = "頭は未だ何だか明瞭しない"
    text_list = [text]
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
