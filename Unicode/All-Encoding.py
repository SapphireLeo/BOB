# open the file as binary format
f = open("context.enc", "rb")

# declare list of encoding style as Python tuple
_encoding_style = ('ASCII', 'EUC-KR', 'CP949', 'UTF-8', 'UTF-16', 'UTF-32')


# this function return decoded ByteArray with given encoding format.
def byte_string_decode(byte_string, encoding_format):
    try:
        result = byte_string.decode(encoding=encoding_format)

    # if the encoding format doesn't match with the ByteArray, return only None.
    except UnicodeDecodeError:
        return None

    # return decoded ByteArray as string format.
    else:
        return result


# get all binary data from file, and split along '\n'
allLines = f.read().splitlines()

# for each line, start decode.
for lineNum, line in enumerate(allLines):
    # remove all NULL character at start point.
    line = line.lstrip(b'\x00')

    # print line number and bytecode.
    print(f"Line {lineNum}:")
    print('\tbytecode:', end='',)
    # if length of bytecode is too long, present in compressed format.
    if len(line) > 11:
        print(line[:5], '...', line[-5:])
    else:
        print(line)

    # for each encoding format, print decoded result string.
    for encoding in _encoding_style:
        encoding_result = byte_string_decode(line, encoding)
        # print only if the bytecode is decoded successfully.
        if encoding_result is not None:
            print(f'\tencoded by {encoding}:', encoding_result)

