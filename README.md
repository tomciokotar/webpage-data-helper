# Webpage data helper
Usługa umożliwiająca zapisywanie tekstu i linków do obrazków ze stron internetowych do bazy danych. Możliwe jest również zapisanie samych obrazków na dysku serwera. Zapisane dane mogą być później pobrane przez klienta.

- Flask (+ RESTful)
- MongoDB
- Docker

# Uruchamianie
Mogą być potrzebne prawa admina.
```sh
$ docker-compose build
$ docker-compose up
```
Testy:
```sh
$ docker-compose build
$ docker-compose -f docker-compose-test.yml up --abort-on-container-exit web
```
Dostęp do API:
```
http://localhost:5000/
```

# API
Wszystkie wysyłane i odbierane dane są w JSON'ie.

Możliwe statusy dla stron i obrazków: `fetching`, `fetched`, `fetching failed`, `not fetched` (ten ostatni to status, jaki mają obrazki w przypadku polecenia, żeby ich nie ściągać, a ściągnąć wyłącznie tekst ze strony).

Zapisz nową stronę w systemie i w odpowiedzi zwróć `snap_id` dla nowej strony (`fetch_images` jest opcjonalne):
Zapytanie:
```
POST /v1/webpage-snaps
{'url': <url>, 'fetch_images': 'true'}
```
Odpowiedź:
```
{'snap_id': ...}
```

Informacje o stronie (URL, status dot. postępu w ściąganiu, ew. informacja o błędzie):
```
GET /v1/webpage-snaps/<snap_id>/info
```
```
{'url': ..., 'status': ..., 'error': ...}
```

Tekst (w postaci listy tekstów z różnych elementów HTML'owych):
```
GET /v1/webpage-snaps/<snap_id>/text
```
```
['element 1', 'element 2', ...]
```

Lista informacji o obrazkach na stronie:
```
GET /v1/webpage-snaps/<snap_id>/images
```
```
[{'id': ..., 'url': ..., 'status': ..., 'error': ...}, ...]
```

`info`, `test` i `images` w jednym:
```
GET /v1/webpage-snaps/<snap_id>
```
```
{'url': ..., 'status': ..., 'error': ..., 'text_elements': ['elem 1', 'elem 2', ...], 'images': [{info 1}, {info 2}, ...]}
```

Usuwanie strony z bazy (i obrazków, jeśli są), nie zwraca zawartości:
```
DELETE /v1/webpage-snaps/<snap_id>
```

Pobieranie konkretnego obrazka (o ile jest zapisany):
```
GET /v1/webpage-snaps/<snap_id>/images/<image_id>
```

Info na temat obrazka (`id`, `url`, `status`):
```
GET /v1/webpage-snaps/<snap_id>/images/<image_id>/info
```
```
{'id': ..., 'url': ..., 'status': ..., 'error': ...}
```

# Inne
Jedno niedociągnięcie, co do którego uznałem, że nie trzeba go koniecznie poprawiać na potrzeby zadania (jako że głównym kryterium oceny jest API z tego co zrozumiałem), ale może warto o nim wspomnieć: nie wszystkie operacje są atomowe.
Może się np. zdarzyć, że w przypadku błędu podczas usuwania strony obrazki zostaną usunięte z dysku, ale strona jako taka z bazy już nie. Albo, że jakaś strona będzie wiecznie miała status `fetching`.

Poza tym, jeśli nie będzie jasne, dlaczego zrobiłem coś w taki, a nie inny sposób, to z chęcią wyjaśnię :)
