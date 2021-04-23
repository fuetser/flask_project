# Проект Социальная сеть "SYB" на Python и Flask
Проект разрабатывался в учебно-познавательных целях.​

В качестве темы проекта была выбрана разработка социальной сети.​

В качестве ориентира мы взяли англоязычную соц.сеть Reddit. Его отличительная черта - сабреддиты, уникальные сообщества. Именно её мы решили реализовать в нашем проекте. Помимо этого должны быть такие базовые для социальных сетей опции как: умная лента - разделение на лучшие посты, набирающие популярность ("горячее"), и посты из групп, на которые подписаны. ​

## Работа с АPI

##### Общий вид запроса:
```
http://syb-blog.herokuapp.com/api/{api_method}?token={token}&offset={offset}&limit={limit}
```
#### Получение токена
Для получения API-токена необходимо иметь аккаунт на сайте. Если он у Вас уже есть, Вы можете получить токен либо на сайте, либо с помощью запроса к API. После получения токен будет действителен 24 часа.
###### Получение токена на сайте:
Для получения токена на сайте перейдите в свой аккаунт, в раздел настройки,  далее - "API-токен" или по ссылке - [Получить токен](http://syb-blog.herokuapp.com/token)
###### Получение токена с помощью запроса к API:
Для получения токена с помощью API необоходимо отправить POST запрос по ссылке **/api/tokens**.
**Поля запроса:**
| Название | Тип поля  | Обязательность |
|:--------:|:---------:|:--------------:|
| username |  string   |        да      |
| password |  string   |        да      |

###### Пример запроса
```python
import requests

requests.post(
    "http://syb-blog.herokuapp.com/api/tokens",
    json={
        "username": "Username",
        "password": "Password123"
    }
)
```
###### Пример ответа
```json
{
    "ok": true,
    "status": 201,
    "token": "token-goes-here"
}
```

###### Пример ответа при неверном запросе
```json
{
    "ok": false,
    "status": 400,
    "detail": "error message goes here"
}
```

### Методы API
При любом запросе к API, кроме создания пользователя и получения токена, нужен токен, который необходимо передавать в качестве query-параметра, так же в запросе могут быть указаны дополнительные параметры **limit** - количество результатов и **offset** - смещение относительно первого результата.

Если запрос не будет содержать ни одного результата, будет возращено сообщение об ошибке:
```json
{
    "ok": false,
    "status": 400,
    "detail": "Wrong offset or limit value"
}
```
#### Users
##### Получение списка всех пользователей
```python
import requests

requests.get(
    "http://syb-blog.herokuapp.com/api/users",
    params={
        "token": "your-token",
        "offset": 1,
        "limit": 5
    }
)
```
##### Получение данных о конретном пользователе
Для получения данных о конкретном пользователе необходимо указать его имя после метода API (**/api/users/Username**)
```python
import requests

requests.get("http://syb-blog.herokuapp.com/api/users/Username", params={"token": "your-token"})
```
#### Создание аккаунта
Для создания аккаунта необходимо отправить POST запрос по адресу **/api/users**
**Поля запроса:**
| Название | Тип поля  | Обязательность |
|:--------:|:---------:|:--------------:|
| username |  string   |        да      |
| password |  string   |        да      |
|   email  |  string   |        да      |

Обратите внимание на то, что поля username и email должны быть уникальными.
```python
import requests

requests.get(
    "http://syb-blog.herokuapp.com/api/users",
    json={
        "username": "Username",
        "password": "Password123",
        "email": "username@mail.com"
        }
)
```
**Пример ответа:**
```json
{
   "ok":true,
   "status":200,
   "users":[
      {
         "comments":[
            {
               "author_id":1,
               "body":"123",
               "id":1,
               "likes":[],
               "post_id":4,
               "timestamp":"Wed, 21 Apr 2021 14:09:51 GMT"
            }
         ],
         "email":"sasha@mail.com",
         "id":1,
         "posts":[
            {
               "author_id":1,
               "body":"hello world!",
               "comments":[],
               "group_id":1,
               "id":2,
               "likes":[],
               "timestamp":"Fri, 16 Apr 2021 16:08:50 GMT",
               "title":"123"
            }
         ],
         "registered":"Fri, 16 Apr 2021 15:49:57 GMT",
         "username":"Sasha"
      }
   ]
}
```
##### Изменение профиля
Для изменения доступны следующие поля:
| Название | Тип поля  | Обязательность |
|:--------:|:---------:|:--------------:|
| username |  string   |       нет      |
| password |  string   |       нет      |
|   email  |  string   |       нет      |

Изменение происходит с помощью PUT запроса, при это должно быть передано хотя бы одно из перечисленных полей
```python
import requests

requests.put(
    "http://syb-blog.herokuapp.com/api/users/Username",
    json={
        "username": "New Username",
        "password": "NewPassword123",
        "email": "new_username@mail.com"
    },
    params={"token": "your-token"}
)
```
##### Удаление аккаунта
Удаление аккаунты выполняется с помощью DELETE запроса
```python
import requests

requests.delete("http://syb-blog.herokuapp.com/api/users/Username", params={"token": "your-token"})
```
#### Posts
Получение всех постов, конкретного поста (по id), удаление поста (по id) происходит аналагично пользователям.
##### Изменение поста
Для изменения доступны следующие поля:
| Название | Тип поля  | Обязательность |
|:--------:|:---------:|:--------------:|
|   title  |  string   |       нет      |
|   body   |  string   |       нет      |

Изменение происходит с помощью PUT запроса, при это должно быть передано хотя бы одно из перечисленных полей, а также Вы должны являться автором поста.
```python
import requests

requests.put(
    "http://syb-blog.herokuapp.com/api/posts/1",
    json={
        "title": "New Title",
        "body": "New post content"
    },
    params={"token": "your-token"}
)
```
#### Groups
Получение всех групп, конкретной группы (по id), удаление группы (по id) происходит аналагично пользователям.
##### Изменение группы
Для изменения доступны следующие поля:
|  Название   | Тип поля  | Обязательность |
|:-----------:|:---------:|:--------------:|
|    name     |  string   |       нет      |
| description |  string   |       нет      |

Изменение происходит с помощью PUT запроса, при это должно быть передано хотя бы одно из перечисленных полей, а также Вы должны являться создателем группы.
```python
import requests

requests.put(
    "http://syb-blog.herokuapp.com/api/posts/1",
    json={
        "name": "New Group Name",
        "description": "New description"
    },
    params={"token": "your-token"}
)
```
