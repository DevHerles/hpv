MINSA MPI Client
==================

Instalación
------------

Instalar con PIP:
```
pip install -U git+ssh://git@git.minsa.gob.pe/oidt/mpi-client.git@develop#egg=mpi_client
```

Asegúrese de tener las variables de entorno:
```sh
MPI_API_HOST
MPI_API_TOKEN
```


Uso
-----

Importe el cliente MPI client

```python
from mpi_client.client import MPIClient
```

Tendrá los métodos HTTP por defecto

`GET`, `OPTIONS`, `HEAD`, `POST`, `PUT`, `PATCH`, `DELETE`

```python
mpi_client = MPIClient(token_autorizacion)

mpi_client.get('url', params, **kwargs)
mpi_client.options('url', **kwargs)
mpi_client.head('url', **kwargs)
mpi_client.post('url', data, json, **kwargs)
mpi_client.put('url', data, **kwargs)
mpi_client.patch('url', data, **kwargs)
mpi_client.delete('url', **kwargs)
```
