from bottle import route, run, error, template, request
from operator import itemgetter
import vk_api
import getpass


class CountriesVkWrapper:
    def __init__(self, vk_tools, vk):
        self.vk_tools = vk_tools
        self.vk = vk

    @classmethod
    def set_vk_tools(cls, vk_tools):
        cls.vk_tools = vk_tools

    @classmethod
    def set_vk(cls, vk):
        cls.vk = vk

    @classmethod
    def countries(cls):
        """
        Получение списка стран в виде списка словарей
        :return: список словарей со странами
        """
        return cls.vk_tools.get_all('database.getCountries', 1000, {'need_all': 1, 'count': 1000})['items']

    @classmethod
    def country(cls, country_id):
        """
        Получение одной страны в виде словаря
        :param country_id: id страны
        :return: словарь со страной
        """
        return cls.vk.database.getCountriesById(country_ids=country_id)[0]

    @classmethod
    def get_cities(cls, country_id, all):
        """
        Получение списка городов в виде списка словарей
        :param country_id: id страны в которой необходимо узнать города
        :param all: получать ли все города
        :return: список словарей с городами
        """
        return cls.vk_tools.get_all('database.getCities', 1000, {'country_id': country_id, 'need_all': all, 'count': 1000})['items']

    @classmethod
    def get_city(cls, city_id):
        """
        Получение одного города в виде словаря
        :param city_id: id города
        :return: словарь с городом
        """
        return cls.vk.database.getCitiesById(city_ids=city_id)[0]


wrap_vk = CountriesVkWrapper


@error(404)
def err404(error):
    return '''
    <p style="text-align: center;margin-top: 20%;">
    Ooops.. Sorry, nothing here
    <br>ERROR 404</p>
    '''


@route('/')
def countries():
    return template(
        'templates/countries.html', {
            'items': wrap_vk.countries(),  # список стран в виде словарей
            'boo': 1,                               # для обозначения списка стран в универсальном шаблоне
            'title': 'Countries'                    # заголовок страницы
            }
        )


@route('/<country_id:int>')
def cities(country_id):
    """
    sort: "0" сортировать в алфавитном порядке
          "1" сортировать в обратном алфавитном порядке

    (для vk api)
    all_c: "0" показывать не все города страны
           "1" показывать все города страны
    :param country_id: id страны
    :return: заполненый шаблон
    """
    try:
        all_c = request.query['all']
    except KeyError:
        all_c = 0
    try:
        sort = request.query['sort']
    except KeyError:
        sort = 1
    country = wrap_vk.country(country_id)['title']
    cities_list = wrap_vk.get_cities(country_id, all_c)
    if request.query:
        if sort == "1":
            cities_list.sort(key=itemgetter('title'))
            sort = 0
        elif sort == "0":
            cities_list.sort(key=itemgetter('title'), reverse=True)
            sort = 1
    if all_c == '1':
        all_c = 0
    else:
        all_c = 1
    return template(
        'templates/countries.html', {
            'items': cities_list,               # список городов в виде словарей
            'boo': 0,                           # для обозначения списка городов в универсальном шаблоне
            'title': 'Cities in ' + country,    # заголовок страницы
            'sort': sort,                       # для кнопки сортировки
            'all': all_c                        # для кнопки показа всех городов
            }
        )


def auth_handler():
    """ При двухфакторной аутентификации вызывается эта функция.
    """
    key = input("Enter authentication code: ")
    remember_device = True

    return key, remember_device


def main():
    login = input("Login: ")
    password = getpass.getpass("Password: ")

    vk_session = vk_api.VkApi(login, password, auth_handler=auth_handler)

    try:
        vk_session.auth()
    except vk_api.AuthError as error_msg:
        print(error_msg)
        return

    wrap_vk.set_vk_tools(vk_tools=vk_api.VkTools(vk_session))
    wrap_vk.set_vk(vk=vk_session.get_api())

    run()


if __name__ == '__main__':
    main()
