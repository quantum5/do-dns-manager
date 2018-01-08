def load_htpasswd(file):
    database = {}

    with open(file, encoding='utf-8') as file:
        for line in file:
            line = line.strip()
            if not line or line.startswith('#'):
                continue

            username, password = line.split(':', 1)
            database[username] = password

    return database
