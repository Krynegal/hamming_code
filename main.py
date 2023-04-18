from fastcrc import crc16
from random import randint

WORD_LENGTH = 99


def encoding(text):
    d, c = {'': ''.zfill(8)}, 1
    for i in range(len(text)):
        if text[i] not in d:
            d[text[i]], c = str(bin(c)[2:]).zfill(8), c + 1
    return d


def get_bin_source_text(text, dictionary):
    return "".join([dictionary[i] for i in text])


def codewords(b_text):
    s = WORD_LENGTH - 7
    return [b_text[i:i + s].zfill(s) for i in range(0, len(b_text), s)]


def process(word):
    for j in range(7):
        start = 2 ** j - 1 + 1
        stop = 2 * 2 ** j - 1
        line_sum = 0
        while start <= (len(str(word))):
            arr = [int(i) for i in word[start:stop]]
            line_sum += sum(arr)
            start = stop + 2 ** j
            stop = start + 2 ** j
        word = f'{word[:2 ** j - 1]}{line_sum % 2}{word[2 ** j:]}'
    return word


def hamming_code(words):
    hamming_code = []
    for i in range(len(words)):
        hamming_code.append(words[i])
        for j in range(7):
            hamming_code[i] = hamming_code[i][:2 ** j - 1] + str(0) + hamming_code[i][2 ** j - 1:]
        hamming_code[i] = process(hamming_code[i])
    return hamming_code


def err_sent_detection(mistakes):
    mistakes_checker = []
    for i in range(len(mistakes)):
        mistakes_checker.append(mistakes[i])
        mistakes_checker[i] = process(mistakes_checker[i])
    numb_sent = []
    for i in range(len(mistakes_checker)):
        for j in range(len(mistakes_checker[i])):
            if mistakes_checker[i][j] != mistakes[i][j]:
                numb_sent.append(i)
                break
    return numb_sent


def mistakes_detection(numb_sent, mistakes):
    mistakes_checker = []
    mis = []
    for i in range(len(numb_sent)):
        mistakes_checker.append(mistakes[numb_sent[i]])
        mis.append([])
        for j in range(7):
            start = 2 ** j - 1
            stop = 2 * 2 ** j - 1
            line_sum = 0
            while start < (len(str(mistakes_checker[i]))):
                arr = [int(i) for i in mistakes_checker[i][start:stop]]
                line_sum += sum(arr)
                start = stop + 2 ** j
                stop = start + 2 ** j
            mis[i].append(line_sum % 2)
    results = []
    for i in range(len(mis)):
        result = 0
        for j in reversed(range(7)):
            result += mis[i][j] * 2 ** j
        results.append(result - 1)
    return results


def mistakes_fixing(mist_pos, numb_sent, mistakes):
    words = mistakes.copy()
    for i in range(len(mist_pos)):
        try:
            ns, mp = numb_sent[i], mist_pos[i]
            words[ns] = f'{words[ns][:mp]}{abs(int(words[ns][mp]) - 1)}{words[ns][mp + 1:]}'
        except:
            continue
    return words


def decoding(words):
    decoder = []
    for i in range(len(words)):
        decoder.append(words[i])
        for j in reversed(range(7)):
            decoder[i] = decoder[i][:2 ** j - 1] + decoder[i][2 ** j:]
    return decoder


def get_key(d, value):
    try:
        for k, v in d.items():
            if v == value:
                return k
    except TypeError:
        print(d[0])
        return d[0]


def bin2words(dec_words):
    full_bin = ''
    for i in range(len(dec_words)):
        full_bin += dec_words[i]
    final_text = ''
    for j in range(0, len(full_bin) - 7, 8):
        try:
            final_text += get_key(word_dict, full_bin[j:j + 8])
        except TypeError:
            final_text += ''
    return final_text


if __name__ == "__main__":
    with open('file.txt') as f:
        source_text = f.read()
    print(len(source_text))

    word_dict = encoding(source_text)
    b_text = get_bin_source_text(source_text, word_dict)
    code_words = codewords(b_text)
    print(code_words)

    checksum1 = [crc16.arc(f'{word}'.encode()) for word in code_words]

    hamming_words = hamming_code(code_words)
    word_length = len(hamming_words[0])
    word_number = len(hamming_words)
    print(f'Длина слова с учетом контрольных бит: {word_length}')
    print(f'Количество слов: {word_number}')

    random_numbers = [randint(0, len(hamming_words[i]) - 1) for i in range(word_number)]
    random_words = []
    for i in range(20):
        cond = randint(1, 3)
        random_words.extend([randint(0, word_number-1)]*cond)

    error_stat = {}
    for word_num in random_words:
        if word_num not in error_stat:
            error_stat[word_num] = 1
        else:
            error_stat[word_num] += 1
    print(error_stat)

    mistakes_0 = hamming_words.copy()
    mistakes_1 = hamming_words.copy()
    for i in range(word_number):
        m1, rn = mistakes_1[i], random_numbers[i]
        mistakes_1[i] = f'{m1[:rn]}{abs(int(m1[rn]) - 1)}{m1[rn + 1:]}'
    mistakes_few = hamming_words.copy()
    for i in range(len(random_words)):
        rs, rn = random_words[i], random_numbers[i]
        mistakes_few[rs] = f'{mistakes_few[rs][:rn]}{abs(int(mistakes_few[rs][rn]) - 1)}{mistakes_few[rs][rn + 1:]}'

    for a in [mistakes_0, mistakes_1, mistakes_few]:
        numb_sent = err_sent_detection(a)
        mist_pos = mistakes_detection(numb_sent, a)
        words = mistakes_fixing(mist_pos, numb_sent, a)
        dec_words = decoding(words)
        checksum = [crc16.arc(f'{i}'.encode()) for i in dec_words]
        print(checksum1 == checksum)
        text = bin2words(dec_words)
        print(f'text: {text}')


    numb_sent_few = err_sent_detection(mistakes_few)
    mist_pos_few = mistakes_detection(numb_sent_few, mistakes_few)
    words_few = mistakes_fixing(mist_pos_few, numb_sent_few, mistakes_few)
    dec_words_few = decoding(words_few)
    checksum2 = [crc16.arc(f'{i}'.encode()) for i in dec_words_few]
    numb_sent_few = sorted(list(set(random_words)))
    for i in numb_sent_few:
        print(f'слово с номером {i} исправлено: {checksum1[i] == checksum2[i]}')

    print(f'исходный текст: {source_text}')
