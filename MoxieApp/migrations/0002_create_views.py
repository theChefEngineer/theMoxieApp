from django.db import migrations

class Migration(migrations.Migration):
    dependencies = [
        ('MoxieApp', '0001_initial'),
    ]

    operations = [
        migrations.RunSQL(
            # SQL for creating views
            """
            -- View for Medspa statistics
            CREATE OR REPLACE VIEW v_medspa_statistics AS
            SELECT 
                m.id AS medspa_id,
                m.name AS medspa_name,
                COUNT(DISTINCT s.id) AS total_services,
                COUNT(DISTINCT a.id) AS total_appointments,
                COUNT(DISTINCT CASE WHEN a.status = 'completed' THEN a.id END) AS completed_appointments,
                COALESCE(SUM(CASE WHEN a.status = 'completed' THEN a.total_price END), 0) AS total_revenue
            FROM medspa m
            LEFT JOIN appointment a ON a.medspa_id = m.id
            LEFT JOIN appointment_service as_j ON as_j.appointment_id = a.id
            LEFT JOIN service s ON s.id = as_j.service_id
            GROUP BY m.id, m.name;

            -- View for service utilization
            CREATE OR REPLACE VIEW v_service_utilization AS
            SELECT 
                s.id AS service_id,
                s.name AS service_name,
                m.id AS medspa_id,
                m.name AS medspa_name,
                COUNT(DISTINCT as_j.appointment_id) AS total_bookings,
                COUNT(DISTINCT CASE WHEN a.status = 'completed' THEN a.id END) AS completed_bookings,
                COALESCE(AVG(CASE WHEN a.status = 'completed' THEN a.total_price END), 0) AS avg_revenue_per_booking
            FROM service s
            JOIN appointment_service as_j ON as_j.service_id = s.id
            JOIN appointment a ON a.id = as_j.appointment_id
            JOIN medspa m ON m.id = a.medspa_id
            GROUP BY s.id, s.name, m.id, m.name;
            """
        ),
    ]
