import pickle


def read_data():
    filename = 'my_pickle'
    user_data_file = open(f'{filename}_user_data', 'rb')
    conversations_file = open(f'{filename}_conversations', 'rb')

    user_data_ = pickle.load(user_data_file)
    conversations = pickle.load(conversations_file)

    for key in user_data_:
        print(key, '=>', user_data_[key])

    for key in conversations:
        print(key, '=>', conversations[key])


read_data()
