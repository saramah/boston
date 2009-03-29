def build_dictionary(path, kv):
    """
    build_dictionary(path, kv)
        -path is path to dictionary we want to parse
        -kv is whether or not the dictionary is key-value pairs

    note: this doesn't cover the case when you have both variable
    length keys and values, only variable length values for kv pairs,
    and variable length keys with no values
    """
    build = {}
    with open(path) as infile:
        for line in infile:
            val = True
            if kv is False:
                key = line.strip().title()
            else:
                line = line.split()
                key = line[0].strip().capitalize()
                if len(line) > 1:
                    val = " ".join(line[1:]).strip()
            if key not in build:
                build[key] = val
    return build
