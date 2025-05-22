# Foodgram

Адрес проекта: https://yastudy.hopto.org

Цель этого сайта — дать возможность пользователям создавать и хранить рецепты на онлайн-платформе. Кроме того, можно скачать список продуктов, необходимых для приготовления блюда, просмотреть рецепты друзей и добавить любимые рецепты в список избранных.

# API

## 1. Пользователи

### 1.1 Список пользователей
**Эндпоинт:** `GET api/users/`

**Описание:** Получение списка всех пользователей.

**Параметры запроса:**
- `page` (integer): Номер страницы.
- `limit` (integer): Количество объектов на странице.

**Права доступа:** Доступно всем пользователям.

**Возможные ответы:**
- **200 OK**: Список пользователей успешно получен

**Пример успешного ответа:**
```json
{
  "count": 123,
  "next": "http://foodgram.example.org/api/users/?page=4",
  "previous": "http://foodgram.example.org/api/users/?page=2",
  "results": [
    {
      "email": "user@example.com",
      "id": 0,
      "username": "string",
      "first_name": "Вася",
      "last_name": "Иванов",
      "is_subscribed": false,
      "avatar": "http://foodgram.example.org/media/users/image.png"
    }
  ]
}
```

### 1.2 Регистрация пользователя
**Эндпоинт:** `POST api/users/`

**Описание:** Регистрация пользователя.

**Тело запроса:**
- `email` (string <email> <= 254 characters, required): Email пользователя
- `username` (string <= 150 characters ^[\w.@+-]+\z, required): Уникальный юзернейм
- `first_name` (string <= 150 characters, required): Имя
- `last_name` (string <= 150 characters, required): Фамилия
- `password` (string, required): Пароль

**Права доступа:** Доступно всем пользователям.

**Возможные ответы:**
- **201 CREATED**: Пользователь успешно создан
- **400 BAD_REQUEST**: Ошибка валидации в стандартном формате DRF

**Пример запроса:**
```json
{
  "email": "vpupkin@yandex.ru",
  "username": "vasya.pupkin",
  "first_name": "Вася",
  "last_name": "Иванов",
  "password": "Qwerty123"
}
```

**Пример успешного ответа:**
```json
{
  "email": "vpupkin@yandex.ru",
  "id": 0,
  "username": "vasya.pupkin",
  "first_name": "Вася",
  "last_name": "Иванов"
}
```

### 1.3 Профиль пользователя
**Эндпоинт:** `GET api/users/{id}/`

**Описание:** Профиль пользователя.

**Параметры запроса:**
- `id` (string, required): Уникальный id этого пользователя

**Права доступа:** Доступно всем пользователям.

**Возможные ответы:**
- **200 OK**: Список пользователей успешно получен
- **404 NOT_FOUND**: Объект не найден

**Пример успешного ответа:**
```json
{
  "email": "user@example.com",
  "id": 0,
  "username": "string",
  "first_name": "Вася",
  "last_name": "Иванов",
  "is_subscribed": false,
  "avatar": "http://foodgram.example.org/media/users/image.png"
}
```

### 1.4 Текущий пользователь
**Эндпоинт:** `GET api/users/me/`

**Описание:** Текущий пользователь.

**Права доступа:** Доступно только авторизованному пользователю.

**Тело запроса:**
- `username` (avatar, required): Картинка, закодированная в Base64

**Возможные ответы:**
- **200 OK**: Текущий пользователь успешно получен
- **401 UNAUTHORIZED**: Пользователь не авторизован

**Пример успешного ответа:**
```json
{
  "email": "user@example.com",
  "id": 0,
  "username": "string",
  "first_name": "Вася",
  "last_name": "Иванов",
  "is_subscribed": false,
  "avatar": "http://foodgram.example.org/media/users/image.png"
}
```

### 1.5 Добавление аватара
**Эндпоинт:** `PUT api/users/me/avatar`

**Описание:** Добавление аватара.

**Права доступа:** Авторизированый пользователь.

**Возможные ответы:**
- **200 OK**: Аватар успешно добавлен
- **400 BAD_REQUEST**: Ошибка валидации в стандартном формате DRF
- **401 UNAUTHORIZED**: Пользователь не авторизован

**Пример запроса:**
```json
{
  "avatar": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABAgMAAABieywaAAAACVBMVEUAAAD///9fX1/S0ecCAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAACklEQVQImWNoAAAAggCByxOyYQAAAABJRU5ErkJggg=="
}
```

**Пример успешного ответа:**
```json
{
  "avatar": "http://foodgram.example.org/media/users/image.png"
}
```

### 1.5 Удаление аватара
**Эндпоинт:** `DELETE api/users/me/avatar/`

**Описание:** Удаление аватара.

**Права доступа:** Авторизированый пользователь.

**Возможные ответы:**
- **204 NO_CONTENT**: Пользователь успешно удален
- **401 UNAUTHORIZED**: Пользователь не авторизован

### 1.6 Изменение пароля
**Эндпоинт:** `POST api/users/set_password/`

**Описание:** Изменение пароля.

**Тело запроса:**
- `new_password` (string, required): Новый пароль
- `current_password` (string, required): Текущий пароль

**Права доступа:** Авторизированый пользователь.

**Возможные ответы:**
- **204 NO_CONTENT**: Пароль успешно изменен
- **400 BAD_REQUEST**: Ошибка валидации в стандартном формате DRF
- **401 UNAUTHORIZED**: Пользователь не авторизован

**Пример запроса:**
```json
{
  "new_password": "string",
  "current_password": "string"
}
```

### 1.7 Получить токен авторизации
**Эндпоинт:** `GET api/auth/token/login/`

**Описание:** Используется для авторизации по емейлу и паролю, чтобы далее использовать токен при запросах.

**Тело запроса:**
- `password` (string, required): Пароль
- `email` (string, required): Email пользователя

**Права доступа:** Свободный доступ.

**Возможные ответы:**
- **200 OK**: Токен авторизации успешно получен.

**Пример запроса:**
```json
{
  "password": "string",
  "email": "string"
}
```

**Пример успешного ответа:**
```json
{
  "auth_token": "string"
}
```

### 1.8 Удаление токена
**Эндпоинт:** `GET api/auth/token/logout/`

**Описание:** Удаляет токен текущего пользователя.

**Права доступа:** Свободный доступ.

**Возможные ответы:**
- **204 NO_CONTENT**: Токен успешно удален
- **401 UNAUTHORIZED**: Пользователь не авторизован


## 2. Теги

### 2.1 Cписок тегов
**Эндпоинт:** `GET api/tags/`

**Описание:** Получение списка всех тегов.

**Права доступа:** Свободный доступ.

**Возможные ответы:**
- **200 OK**: Список тегов успешно получен.

**Пример успешного ответа:**
```json
[
  {
    "id": 0,
    "name": "Завтрак",
    "slug": "breakfast"
  }
]
```

### 2.2 Получение тега
**Эндпоинт:** `GET api/tags/{id}/`

**Описание:** Получение тега.

**Параметры запроса:**
- `id` (string, required): Уникальный id тега

**Права доступа:** Свободный доступ.

**Возможные ответы:**
- **200 OK**: Тег успешно получен.
- **404 NOT_FOUND**: Объект не найден

**Пример успешного ответа:**
```json
{
  "id": 0,
  "name": "Завтрак",
  "slug": "breakfast"
}
```

## 3. Рецепты

### 3.1 Список рецептов
**Эндпоинт:** `GET api/recipes/`

**Описание:** Получение списка всех рецептов.

**Параметры запроса:**
- `page` (integer): Номер страницы
- `limit` (integer): Количество объектов на странице
- `is_favorited` (integer Enum: 0 1): Показывать только рецепты, находящиеся в списке избранного.
- `is_in_shopping_cart` (integer Enum: 0 1): Показывать только рецепты, находящиеся в списке покупок.
- `author` (integer): Показывать рецепты только автора с указанным id.
- `tags` (Array of strings): Показывать рецепты только с указанными тегами (по slug). Пример: tags=lunch&tags=breakfast

**Права доступа:** Свободный доступ.

**Возможные ответы:**
- **200 OK**: Список рецептов успешно получен.

**Пример успешного ответа:**
```json
{
  "count": 123,
  "next": "http://foodgram.example.org/api/recipes/?page=4",
  "previous": "http://foodgram.example.org/api/recipes/?page=2",
  "results": [
    {
      "id": 0,
      "tags": [
        {
          "id": 0,
          "name": "Завтрак",
          "slug": "breakfast"
        }
      ],
      "author": {
        "email": "user@example.com",
        "id": 0,
        "username": "string",
        "first_name": "Вася",
        "last_name": "Иванов",
        "is_subscribed": false,
        "avatar": "http://foodgram.example.org/media/users/image.png"
      },
      "ingredients": [
        {
          "id": 0,
          "name": "Картофель отварной",
          "measurement_unit": "г",
          "amount": 1
        }
      ],
      "is_favorited": true,
      "is_in_shopping_cart": true,
      "name": "string",
      "image": "http://foodgram.example.org/media/recipes/images/image.png",
      "text": "string",
      "cooking_time": 1
    }
  ]
}
```

### 3.2 Создание рецепта
**Эндпоинт:** `POST api/recipes/`

**Описание:** Создание рецепта.

**Права доступа:** Доступно только авторизованному пользователю.

**Тело запроса:**
- `ingredients` (Array of integers, required): Список ингредиентов
- `tags` (Array of integers, required): Список id тегов
- `image` (string <binary>, required): Картинка, закодированная в Base64
- `name` (string <= 256 characters, required): Название
- `text` (string, required): Описание
- `cooking_time` (integer >= 1, required): Время приготовления (в минутах

**Возможные ответы:**
- **201 CREATED**: Рецепт успешно создан
- **400 BAD_REQUEST**: Ошибка валидации в стандартном формате DRF
- **401 UNAUTHORIZED**: Пользователь не авторизован
- **404 NOT_FOUND**: Объект не найден

**Пример запроса:**
```json
{
  "ingredients": [
    {
      "id": 1123,
      "amount": 10
    }
  ],
  "tags": [
    1,
    2
  ],
  "image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABAgMAAABieywaAAAACVBMVEUAAAD///9fX1/S0ecCAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAACklEQVQImWNoAAAAggCByxOyYQAAAABJRU5ErkJggg==",
  "name": "string",
  "text": "string",
  "cooking_time": 1
}
```

**Пример успешного ответа:**
```json
{
  "id": 0,
  "tags": [
    {
      "id": 0,
      "name": "Завтрак",
      "slug": "breakfast"
    }
  ],
  "author": {
    "email": "user@example.com",
    "id": 0,
    "username": "string",
    "first_name": "Вася",
    "last_name": "Иванов",
    "is_subscribed": false,
    "avatar": "http://foodgram.example.org/media/users/image.png"
  },
  "ingredients": [
    {
      "id": 0,
      "name": "Картофель отварной",
      "measurement_unit": "г",
      "amount": 1
    }
  ],
  "is_favorited": true,
  "is_in_shopping_cart": true,
  "name": "string",
  "image": "http://foodgram.example.org/media/recipes/images/image.png",
  "text": "string",
  "cooking_time": 1
}
```

### 3.3 Получение рецепта
**Эндпоинт:** `GET api/recipes/{id}/`

**Описание:** Получение рецепта.

**Параметры запроса:**
- `id` (string, required): Уникальный id рецепта

**Права доступа:** Доступно всем пользователям.

**Возможные ответы:**
- **200 OK**: Рецепт успешно получен

**Пример успешного ответа:**
```json
{
  "id": 0,
  "tags": [
    {
      "id": 0,
      "name": "Завтрак",
      "slug": "breakfast"
    }
  ],
  "author": {
    "email": "user@example.com",
    "id": 0,
    "username": "string",
    "first_name": "Вася",
    "last_name": "Иванов",
    "is_subscribed": false,
    "avatar": "http://foodgram.example.org/media/users/image.png"
  },
  "ingredients": [
    {
      "id": 0,
      "name": "Картофель отварной",
      "measurement_unit": "г",
      "amount": 1
    }
  ],
  "is_favorited": true,
  "is_in_shopping_cart": true,
  "name": "string",
  "image": "http://foodgram.example.org/media/recipes/images/image.png",
  "text": "string",
  "cooking_time": 1
}
```

### 3.4 Обновление рецепта
**Эндпоинт:** `PATCH api/recipes/{id}/`

**Описание:** Обновление рецепта.

**Параметры запроса:**
- `id` (string, required): Уникальный id рецепта

**Тело запроса:**
- `ingredients` (Array of integers, required): Список ингредиентов
- `tags` (Array of integers, required): Список id тегов
- `image` (string <binary>, required): Картинка, закодированная в Base64
- `name` (string <= 256 characters, required): Название
- `text` (string, required): Описание
- `cooking_time` (integer >= 1, required): Время приготовления (в минутах

**Права доступа:** Доступно только автору данного рецепта.

**Возможные ответы:**
- **200 OK**: Рецепт успешно обновлен
- **400 BAD_REQUEST**: Ошибка валидации в стандартном формате DRF, в том числе с внутренними элементами
- **401 UNAUTHORIZED**: Недостаточно прав
- **403 FORBIDDEN**: Недостаточно прав
- **404 NOT_FOUND**: Объект не найден

**Пример запроса:**
```json
{
  "ingredients": [
    {
      "id": 1123,
      "amount": 10
    }
  ],
  "tags": [
    1,
    2
  ],
  "image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABAgMAAABieywaAAAACVBMVEUAAAD///9fX1/S0ecCAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAACklEQVQImWNoAAAAggCByxOyYQAAAABJRU5ErkJggg==",
  "name": "string",
  "text": "string",
  "cooking_time": 1
}
```

**Пример успешного ответа:**
```json
{
  "id": 0,
  "tags": [
    {
      "id": 0,
      "name": "Завтрак",
      "slug": "breakfast"
    }
  ],
  "author": {
    "email": "user@example.com",
    "id": 0,
    "username": "string",
    "first_name": "Вася",
    "last_name": "Иванов",
    "is_subscribed": false,
    "avatar": "http://foodgram.example.org/media/users/image.png"
  },
  "ingredients": [
    {
      "id": 0,
      "name": "Картофель отварной",
      "measurement_unit": "г",
      "amount": 1
    }
  ],
  "is_favorited": true,
  "is_in_shopping_cart": true,
  "name": "string",
  "image": "http://foodgram.example.org/media/recipes/images/image.png",
  "text": "string",
  "cooking_time": 1
}
```

### 3.5 Удаление рецепта
**Эндпоинт:** `DELETE api/recipes/{id}/`

**Описание:** Удаление рецепта.

**Параметры запроса:**
- `id` (string, required): Уникальный id рецепта
**Права доступа:** Доступно только автору данного рецепта.

**Возможные ответы:**
- **204 NO_CONTENT**: Рецепт успешно удален
- **401 UNAUTHORIZED**: Пользователь не авторизован
- **403 FORBIDDEN**: Недостаточно прав
- **404 NOT_FOUND**: Объект не найден

### 3.2 Получить короткую ссылку на рецепт
**Эндпоинт:** `GET api/recipes/{id}/get-link/`

**Описание:** Получить короткую ссылку на рецепт.

**Параметры запроса:**
- `id` (string, required): Уникальный id рецепта

**Права доступа:** Доступно всем пользователям.

**Возможные ответы:**
- **200 OK**: Ссылка на рецепт
- **404 NOT_FOUND**: Объект не найден

**Пример запроса:**

**Пример успешного ответа:**
```json
{
  "short-link": "https://foodgram.example.org/s/3d0"
}
```

## 4. Список покупок
### 4.1 Скачать список покупок
**Эндпоинт:** `GET api/recipes/download_shopping_cart/`

**Описание:** Скачать файл со списком покупок.

**Права доступа:** Доступно только авторизованному пользователю.

**Возможные ответы:**
- **200 OK**: Список рецептов успешно получен.
- **401 UNAUTHORIZED**: Пользователь не авторизован

### 4.2 Добавить рецепт в список покупок
**Эндпоинт:** `POST api/recipes/{id}/favorite/`

**Описание:** Добавить рецепт в список покупок.

**Параметры запроса:**
- `id` (string, required): Уникальный id рецепта

***Права доступа:** Доступно только авторизованному пользователю.

**Возможные ответы:**
- **201 CREATED**: Рецепт успешно добавлен в список покупок
- **400 BAD_REQUEST**: Ошибка добавления в список покупок (Например, когда рецепт уже есть в списке покупок)
- **401 UNAUTHORIZED**: Пользователь не авторизован
- **404 NOT_FOUND**: Объект не найден

**Пример успешного ответа:**
```json
{
  "id": 0,
  "name": "string",
  "image": "http://foodgram.example.org/media/recipes/images/image.png",
  "cooking_time": 1
}
```

### 4.3 Удалить рецепт из списка покупок
**Эндпоинт:** `DELETE api/recipes/{id}/favorite/`

**Описание:** Удалить рецепт из списка покупок.

**Параметры запроса:**
- `id` (string, required): Уникальный id рецепта

***Права доступа:** Доступно только авторизованному пользователю.

**Возможные ответы:**
- **204 NO_CONTENT**: Рецепт успешно удален из списока покупок
- **400 BAD_REQUEST**: Ошибка удаления из списка покупок (Например, когда рецепта там не было)
- **401 UNAUTHORIZED**: Пользователь не авторизован
- **404 NOT_FOUND**: Объект не найден


## 5. Избранное

### 5.1 Добавить рецепт в избранное
**Эндпоинт:** `POST api/recipes/{id}/favorite/`

**Описание:** Добавить рецепт в избранное.

**Параметры запроса:**
- `id` (string, required): Уникальный id рецепта

***Права доступа:** Доступно только авторизованному пользователю.

**Возможные ответы:**
- **201 CREATED**: Рецепт успешно добавлен в избранное
- **400 BAD_REQUEST**: Ошибка добавления в избранное (Например, когда рецепт уже есть в избранном)
- **401 UNAUTHORIZED**: Пользователь не авторизован
- **404 NOT_FOUND**: Объект не найден

**Пример успешного ответа:**
```json
{
  "id": 0,
  "name": "string",
  "image": "http://foodgram.example.org/media/recipes/images/image.png",
  "cooking_time": 1
}
```

### 5.2 Удалить рецепт из избранного
**Эндпоинт:** `DELETE api/recipes/{id}/shopping_cart/`

**Описание:** Удалить рецепт из избранного.

**Параметры запроса:**
- `id` (string, required): Уникальный id рецепта

***Права доступа:** Доступно только авторизованному пользователю.

**Возможные ответы:**
- **204 NO_CONTENT**: Рецепт успешно удален из списока покупок
- **400 BAD_REQUEST**: Ошибка удаления из избранного (Например, когда рецепта там не было)
- **401 UNAUTHORIZED**: Пользователь не авторизован
- **404 NOT_FOUND**: Объект не найден

## 6. Подписки
### 6.1 Мои подписки
**Эндпоинт:** `POST api/users/subscriptions/`

**Описание:** Возвращает пользователей, на которых подписан текущий пользователь. В выдачу добавляются рецепты.

**Параметры запроса:**
- `page` (integer): Номер страницы
- `limit` (integer): Количество объектов на странице
- `recipes_limit` (integer): Количество объектов внутри поля recipes.

***Права доступа:** Доступно только авторизованному пользователю.

**Возможные ответы:**
- **200 OK**: Список подписок успешно получен
- **401 UNAUTHORIZED**: Пользователь не авторизован

**Пример успешного ответа:**
```json
{
  "count": 123,
  "next": "http://foodgram.example.org/api/users/subscriptions/?page=4",
  "previous": "http://foodgram.example.org/api/users/subscriptions/?page=2",
  "results": [
    {
      "email": "user@example.com",
      "id": 0,
      "username": "string",
      "first_name": "Вася",
      "last_name": "Иванов",
      "is_subscribed": true,
      "recipes": [
        {
          "id": 0,
          "name": "string",
          "image": "http://foodgram.example.org/media/recipes/images/image.png",
          "cooking_time": 1
        }
      ],
      "recipes_count": 0,
      "avatar": "http://foodgram.example.org/media/users/image.png"
    }
  ]
}
```

### 6.2 Подписаться на пользователя
**Эндпоинт:** `POST api/users/{id}/subscribe/`

**Описание:** Подписаться на пользователя.

***Права доступа:** Доступно только авторизованному пользователю.

**Параметры запроса:**
- `id` (string, required): Уникальный id этого пользователя

**Параметры запроса:**
- `recipes_limit` (integer): Количество объектов внутри поля recipes.

**Возможные ответы:**
- **201 CREATED**: Подписка успешно создана
- **400 BAD_REQUEST**: Ошибка подписки (Например, если уже подписан или при подписке на себя самого)
- **401 UNAUTHORIZED**: Пользователь не авторизован
- **404 NOT_FOUND**: Объект не найден

**Пример успешного ответа:**
```json
{
  "email": "user@example.com",
  "id": 0,
  "username": "string",
  "first_name": "Вася",
  "last_name": "Иванов",
  "is_subscribed": true,
  "recipes": [
    {
      "id": 0,
      "name": "string",
      "image": "http://foodgram.example.org/media/recipes/images/image.png",
      "cooking_time": 1
    }
  ],
  "recipes_count": 0,
  "avatar": "http://foodgram.example.org/media/users/image.png"
}
```

### 6.3 Отписаться от пользователя
**Эндпоинт:** `DELETE api/users/{id}/subscribe/`

**Описание:** Отписаться от пользователя.

**Параметры запроса:**
- `id` (string, required): Уникальный id этого пользователя

***Права доступа:** Доступно только авторизованному пользователю.

**Возможные ответы:**
- **204 NO_CONTENT**: Успешная отписка
- **400 BAD_REQUEST**: Ошибка отписки (Например, если не был подписан)
- **401 UNAUTHORIZED**: Пользователь не авторизован
- **404 NOT_FOUND**: Объект не найден

## 7. Ингредиенты

### 7.1 Список ингредиентов
**Эндпоинт:** `GET api/ingredients/`

**Описание:** Список ингредиентов с возможностью поиска по имени.

**Параметры запроса:**
- `name` (string): Поиск по частичному вхождению в начале названия ингредиента

**Права доступа:** Доступно всем пользователям.

**Возможные ответы:**
- **200 OK**: Список ингредиентов успешно получен

**Пример успешного ответа:**
```json
[
  {
    "id": 0,
    "name": "Капуста",
    "measurement_unit": "кг"
  }
]
```

### 7.2 Получение ингредиента
**Эндпоинт:** `POST api/ingredients/{id}/`

**Описание:** Получение ингредиента.

**Параметры запроса:**
- `id` (string, required): Уникальный id ингредиента

**Права доступа:** Доступно всем пользователям.

**Возможные ответы:**
- **200 OK**: Ингредиент успешно получен

**Пример успешного ответа:**
```json
{
  "id": 0,
  "name": "Капуста",
  "measurement_unit": "кг"
}
```

# Контакты 

Email: [Андрей Карахтанов](super.andrew100@yandex.com) 

GitHub: [AndreyKarakhtanov](https://github.com/AndreyKarakhtanov)
