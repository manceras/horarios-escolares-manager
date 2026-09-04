# horarios-escolares-manager

Generador de horarios de código abierto para colegios de primaria.

Montar el horario de un colegio a mano le cuesta días de trabajo a jefatura de
estudios, y aun así acaba con un profesor dando clase en dos aulas a la vez.
Este proyecto modela el colegio —profesorado, grupos, asignaturas, espacios y
carga lectiva semanal— y genera un horario sin conflictos con un motor de
restricciones, para después revisarlo, ajustarlo e imprimirlo.

[Read this in English](README.md)

## Estado

**Base inicial, todavía no apto para producción.** Lo que ya funciona:

- [x] Modelo de dominio, migraciones y datos de ejemplo de un colegio español
- [x] Motor de restricciones (OR-Tools CP-SAT) con las restricciones duras de abajo, con tests
- [x] Validador independiente de horarios (`find_conflicts`) para ediciones manuales
- [x] Autenticación JWT con roles `admin` / `head_of_studies` / `teacher`
- [x] API para profesorado, grupos, asignaturas, espacios, franjas,
      disponibilidad y carga lectiva, con las reglas de negocio en los servicios
- [x] Endpoints para lanzar el solver, guardar y publicar un horario, y validar
      las ediciones manuales contra las restricciones duras
- [x] Informe de carga que avisa de que el horario es imposible antes de resolver
- [x] Pantalla de profesorado, con las piezas compartidas de tabla, diálogo y
      formulario que reutilizarán el resto de pantallas
- [x] Pantallas para todas las entidades: profesorado, disponibilidad, grupos,
      asignaturas, aulas, franjas y carga lectiva, con informe de viabilidad
- [x] Rejilla semanal: lanzar el solver, ver conflictos, mover y bloquear
      sesiones con el servidor validando cada cambio, y publicar el horario
- [x] Vistas imprimibles y exportación CSV por profesor, grupo y aula
- [ ] Pantalla de gestión de usuarios (hoy se crean con `make create-user`)
- [ ] Más de un curso escolar a la vez

## Restricciones que entiende el motor

Duras — un horario que incumpla una de ellas se rechaza:

- un profesor, un grupo y un aula están como mucho en un sitio por franja
- nadie da clase en una franja en la que no está disponible (jornada parcial, otras tareas)
- las asignaturas que necesitan un espacio concreto (gimnasio, aula de música, informática) lo tienen
- cada entrada de carga lectiva recibe exactamente sus sesiones semanales
- no se programa nada durante el recreo
- ningún profesor supera su máximo de sesiones semanales

Blandas — se minimizan, no se garantizan:

- evitar dos sesiones de la misma asignatura para el mismo grupo el mismo día

El modelo completo está en [`docs/domain-model.md`](docs/domain-model.md).

## Arranque rápido

Requisitos: Python 3.12+ con [uv](https://docs.astral.sh/uv/), Node 22+ con
pnpm, y Docker si quieres el despliegue en contenedores.

```sh
git clone https://github.com/manceras/horarios-escolares-manager.git
cd horarios-escolares-manager
make setup
cp backend/.env.example backend/.env
make migrate
make seed          # datos de desarrollo: admin@example.org / changeme
make dev           # API en :8000, web en :5173
```

Documentación interactiva de la API: <http://localhost:8000/docs>.

## Despliegue

```sh
cp .env.example .env      # pon un SECRET_KEY real
docker compose up -d --build
```

La web se sirve en el puerto 8080 y hace de proxy de `/api` hacia el contenedor
de la API. La base de datos SQLite vive en el volumen `api-data`: haz copia.

### Crear la primera cuenta

No hay registro público: el personal de un colegio no se da de alta solo, y
`make seed` son datos de desarrollo que nunca deben cargarse en un colegio real.
Crea el primer administrador desde la línea de comandos, que pide la contraseña
para que no quede en el historial del shell:

```sh
make create-user                                               # en local
docker compose exec api uv run python scripts/create_user.py   # desplegado
```

Las cuentas siguientes se crean igual.

## Contribuir

Se agradecen las contribuciones, sobre todo de quien hace horarios de verdad.
Empieza por [CONTRIBUTING.md](CONTRIBUTING.md) y por
[`docs/vertical-slice.md`](docs/vertical-slice.md).

Todo el código, los comentarios, la documentación y los mensajes de commit se
escriben en inglés. El texto que ve el usuario está en español y vive solo en
`frontend/src/locales/es.json`.

## Licencia

[MIT](LICENSE) © Antonio Mancera Gamez
