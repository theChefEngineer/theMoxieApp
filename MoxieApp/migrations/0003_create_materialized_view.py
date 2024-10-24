# MoxieApp/migrations/0004_create_mv_daily_revenue.py

from django.db import migrations

class Migration(migrations.Migration):
    dependencies = [
        ('MoxieApp', '0002_create_views'),  # Update this to match your latest migration
    ]

    operations = [
        migrations.RunSQL(
            """
            CREATE MATERIALIZED VIEW mv_daily_revenue AS
            SELECT 
                DATE(a.created_at) AS date,
                m.id AS medspa_id,
                m.name AS medspa_name,
                COUNT(DISTINCT a.id) AS total_appointments,
                SUM(a.total_price) AS daily_revenue,
                array_agg(DISTINCT s.category_id) AS service_categories_used
            FROM appointment a
            JOIN medspa m ON m.id = a.medspa_id
            JOIN appointment_service as_j ON as_j.appointment_id = a.id
            JOIN service s ON s.id = as_j.service_id
            WHERE a.status = 'completed'
            GROUP BY DATE(a.created_at), m.id, m.name
            WITH DATA;

            CREATE UNIQUE INDEX ON mv_daily_revenue (date, medspa_id);

            CREATE OR REPLACE FUNCTION refresh_daily_revenue()
            RETURNS trigger AS $$
            BEGIN
                REFRESH MATERIALIZED VIEW CONCURRENTLY mv_daily_revenue;
                RETURN NULL;
            END;
            $$ LANGUAGE plpgsql;

            CREATE TRIGGER refresh_daily_revenue_trigger
                AFTER INSERT OR UPDATE OR DELETE ON appointment
                FOR EACH STATEMENT
                EXECUTE FUNCTION refresh_daily_revenue();
            """
        ),
    ]
