"""public_datasets app"""

from stac_pydantic import Extensions

from public_datasets.extensions.landsat import LandsatExtension
from stac_fastapi.api.app import StacApi
from stac_fastapi.extensions.core import (
    FieldsExtension,
    QueryExtension,
    SortExtension,
    TransactionExtension,
)
from stac_fastapi.pgstac.config import Settings
from stac_fastapi.pgstac.core import CoreCrudClient
from stac_fastapi.pgstac.db import close_db_connection, connect_to_db
from stac_fastapi.pgstac.transactions import TransactionsClient
from stac_fastapi.pgstac.types.search import PgstacSearch

Extensions.register("landsat", LandsatExtension)


settings = Settings()

api = StacApi(
    settings=settings,
    extensions=[
        TransactionExtension(client=TransactionsClient),
        QueryExtension(),
        SortExtension(),
        FieldsExtension(),
    ],
    client=CoreCrudClient(),
    search_request_model=PgstacSearch,
)
app = api.app


@app.on_event("startup")
async def startup_event():
    """Connect to database on startup."""
    await connect_to_db(app)


@app.on_event("shutdown")
async def shutdown_event():
    """Close database connection."""
    await close_db_connection(app)
