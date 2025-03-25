def password_check(pswd:str):
    # specialSym = ['$', '@', '#', '%']
    is_true = True

    if len(pswd) < 5:
        is_true = False
    if len(pswd) > 20:
        is_true = False
    # if not any(char.isdigit() for char in pswd):
    #     is_true = False
    # if not any(char.isupper() for char in pswd):
    #     is_true = False
    # if not any(char.islower() for char in pswd):
    #     is_true = False
    # if not any(char in specialSym for char in pswd):
    #     is_true = False
    return is_true
