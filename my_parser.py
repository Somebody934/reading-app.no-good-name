from sudachipy import tokenizer, dictionary


class Parser():
    def __init__(self):
        self.tokenizer = dictionary.Dictionary(dict_type="full").create()
        self.mode = tokenizer.Tokenizer.SplitMode.A

    def parse_text(self, text: str):
        morphs = self.tokenizer.tokenize(text, self.mode)
        return morphs

    def parse_list(self, array: list):
        parsed_array = []
        for item in array:
            parsed_item = self.parse_text(item)
            parsed_array.append(parsed_item)
        return parsed_array


def config():
    to = dictionary.Dictionary(dict_type="full").create()
    mode = tokenizer.Tokenizer.SplitMode.A
    return to, mode


if __name__ == "__main__":
    to, mode = config()
    m = to.tokenize("頭は未だ何だか明瞭しない", mode)

    for word in m:
        print(word.surface())
        print(word.part_of_speech())
        print(word.part_of_speech_id())
        print(word.dictionary_form())
        print(word.normalized_form())
        print(word.reading_form())
        print()
