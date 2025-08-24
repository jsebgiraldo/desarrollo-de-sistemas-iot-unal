# Tareas útiles (VS Code / Docker)

- Build: `docker compose exec esp-idf bash -lc "idf.py set-target esp32 && idf.py build"`
- Clean: `docker compose exec esp-idf bash -lc "idf.py fullclean"`
- Size: `docker compose exec esp-idf bash -lc "idf.py size"`
