from django.db import DatabaseError, connection
from django.db.migrations.executor import MigrationExecutor
from django.http import JsonResponse


def readiness(_request):
    try:
        connection.ensure_connection()
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
        executor = MigrationExecutor(connection)
        pending = executor.migration_plan(executor.loader.graph.leaf_nodes())
        if pending:
            return JsonResponse(
                {"status": "not_ready", "checks": {"database": "ok", "migrations": "pending"}},
                status=503,
            )
    except (DatabaseError, OSError):
        return JsonResponse(
            {"status": "not_ready", "checks": {"database": "unavailable"}},
            status=503,
        )
    except Exception:
        # Do not expose database URLs, migration details, or driver errors in health responses.
        return JsonResponse(
            {"status": "not_ready", "checks": {"database": "unavailable"}},
            status=503,
        )
    return JsonResponse({"status": "ready", "checks": {"database": "ok", "migrations": "applied"}})
