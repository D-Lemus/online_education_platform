import pydgraph

# Ajusta el host/puerto si tu profe lo puso diferente
DGRAPH_ALPHA = "localhost:9080"

def get_dgraph_client() -> pydgraph.DgraphClient:
    """
    Devuelve un cliente de Dgraph listo para usar.
    Se usa en los routers para hacer queries y mutaciones.
    """
    stub = pydgraph.DgraphClientStub(DGRAPH_ALPHA)
    client = pydgraph.DgraphClient(stub)
    return client


def init_dgraph_schema():
    """
    Define el esquema mínimo que vamos a usar para inscripciones:
      - user_id: email del usuario
      - course_id: id del curso (el mismo que usas en Mongo)
      - enrolled_in: relación User -> Course
    """
    client = get_dgraph_client()

    schema = """
    user_id: string @index(exact) .
    course_id: string @index(exact) .
    full_name: string .
    role: string .

    enrolled_in: [uid] @reverse .


    type User {
        user_id
        full_name
        role
        enrolled_in
    }

    type Course {
        course_id
        enrolled_in
    }
    """

    op = pydgraph.Operation(schema=schema)
    client.alter(op)