# Webpage data helper
Usługa umożliwiająca zapisywanie zawartości stron internetowych (snapów) do bazy danych i opcjonalnie obrazków z tych stron. Użytkownik może później te dane pobrać.

# Uruchamianie
Mogą być potrzebne prawa admina.
```sh
$ docker-compose build
$ docker-compose up
```
Testy:
```sh
$ docker-compose -f docker-compose-test.yml up --abort-on-container-exit web
```
Dostęp do API:
```
http://localhost:5000/
```

# API
Zapisz nową stronę (`fetch_images` opcjonalnie), w odpowiedzi `snap_id` dla nowej strony:
`POST /v1/webpage-snaps`
`{'url': <url>, 'fetch_images': 'true'}`

Informacje o stronie (`url`, `status`, ew. `error`):
`GET /v1/webpage-snaps/<snap_id>/info`

Tekst (w postaci listy tekstów z różnych elementów HTML'owych):
`GET /v1/webpage-snaps/<snap_id>/text`

Lista opisów obrazków na stronie (`id`, `url`, `status`):
`GET /v1/webpage-snaps/<snap_id>/images`

`info`, `test` i `images` w jednym:
`GET /v1/webpage-snaps/<snap_id>`

Usuwanie strony z bazy (i obrazków, jeśli są), nie zwraca zawartości:
`DELETE /v1/webpage-snaps/<snap_id>`

Pobieranie konkretnego obrazka (o ile jest zapisany):
`GET /v1/webpage-snaps/<snap_id>/images/<image_id>`

Info na temat obrazka (`id`, `url`, `status`):
`GET /v1/webpage-snaps/<snap_id>/images/<image_id>/info`

Możliwe statusy dla stron i obrazków: `fetching`, `fetched`, `fetching failed`, `not fetched` (jeśli było polecenie, żeby nie ściągać obrazków, tylko sam kod strony).

# Inne
Jedno niedociągnięcie, co do którego uznałem, że nie trzeba go koniecznie poprawiać na potrzeby zadania (jako że głównym kryterium oceny jest API z tego, co zrozumiałem), ale może warto o nim wspomnieć: nie wszystkie operacje są atomowe.
Może się np. zdarzyć, że w przypadku błędu podczas usuwania strony obrazki zostaną usunięte z dysku, ale strona jako taka z bazy już nie. Albo, że jakaś strona będzie wiecznie miała status `fetching`.

Poza tym, jeśli nie będzie jasne, dlaczego zrobiłem coś w taki, a nie inny sposób, to z chęcią wyjaśnię :)