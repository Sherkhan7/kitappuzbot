import pickle
from pprint import pp


def read_data():
    filename = 'my_pickle'
    user_data_file = open(f'{filename}_user_data', 'rb')
    conversations_file = open(f'{filename}_conversations', 'rb')

    user_data = pickle.load(user_data_file)
    conversations = pickle.load(conversations_file)

    # for key in user_data:
    #     print(key, '=>', user_data[key])

    # for key in conversations:
    #     print(key, '=>', conversations[key])

    pp(''.ljust(100, '-'))
    pp(user_data)
    pp(''.ljust(100, '-'))
    pp(conversations)
    pp(''.ljust(100, '-'))


read_data()
