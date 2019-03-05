def get_key(api):
    apidict = {"edamam":[1,2], "spotify":[4,5], "openweathermap":[7], "eventbrite":[9]}
    try:
        linenums = apidict[api]
        f = open("keys.txt")
        keys = []
        for i, line in enumerate(f):
             if i in linenums:
                 keys.append(line.rstrip())
        return keys
    except Exception as e:
        print "****API KEY NOT FOUND******"
        return ""
