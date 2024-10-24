# migrations/0004_insert_initial_data.py
from django.db import migrations

def clean_text(text):
    if not text or text == '--' or text == '':
        return None
    return text

class Migration(migrations.Migration):
    dependencies = [
        ('MoxieApp', '0003_create_materialized_view'),
    ]

    operations = [
        migrations.RunSQL(
            # Forward migration
            """
            -- First, insert service categories
            INSERT INTO service_category (name, description) VALUES
            ('Injectables', 'Injectable treatments for cosmetic enhancement'),
            ('Peels', 'Chemical and other peel treatments'),
            ('Fat Dissolving', 'Fat dissolution treatments'),
            ('Sclerotherapy', 'Vein treatment procedures'),
            ('Threads', 'Thread lifting treatments'),
            ('Weightloss', 'Weight management treatments'),
            ('IV Therapy', 'Intravenous therapy treatments'),
            ('Vitamin Injections', 'Vitamin injection treatments'),
            ('Peptide Therapy', 'Peptide-based treatments'),
            ('Ultrasound', 'Ultrasound treatments'),
            ('Facials', 'Facial treatments'),
            ('Other Non Medical', 'Non-medical cosmetic services'),
            ('Consultation', 'Consultation services'),
            ('Follow up', 'Follow-up appointments'),
            ('Other', 'Other services');

            -- Then insert service types
            INSERT INTO service_type (category_id, name, description) VALUES
            -- Injectables
            ((SELECT id FROM service_category WHERE name = 'Injectables'), 'Neuromodulator', 'Botulinum toxin treatments'),
            ((SELECT id FROM service_category WHERE name = 'Injectables'), 'HA Dermal Filler', 'Hyaluronic acid-based fillers'),
            ((SELECT id FROM service_category WHERE name = 'Injectables'), 'Calcium Hydroxyapatite', 'Calcium-based fillers'),
            ((SELECT id FROM service_category WHERE name = 'Injectables'), 'Hyaluronidase', 'Enzyme for filler dissolution'),
            ((SELECT id FROM service_category WHERE name = 'Injectables'), 'Polymethyl methacrylate (PMMA)', 'Permanent filler'),
            ((SELECT id FROM service_category WHERE name = 'Injectables'), 'Poly-L Lactic Acid', 'Collagen stimulator'),

            -- Peels
            ((SELECT id FROM service_category WHERE name = 'Peels'), 'Chemical Peel', 'Chemical exfoliation treatments'),

            -- Fat Dissolving
            ((SELECT id FROM service_category WHERE name = 'Fat Dissolving'), 'Deoxycholic Acid', 'Fat dissolution compound'),

            -- Sclerotherapy
            ((SELECT id FROM service_category WHERE name = 'Sclerotherapy'), 'Sclerotherapy', 'Vein treatment'),

            -- Threads
            ((SELECT id FROM service_category WHERE name = 'Threads'), 'PDO Threads', 'Polydioxanone threads'),
            ((SELECT id FROM service_category WHERE name = 'Threads'), 'Lifting PDO Threads', 'Lifting polydioxanone threads'),
            ((SELECT id FROM service_category WHERE name = 'Threads'), 'Barbed/Cones PDO Threads', 'Barbed polydioxanone threads'),

            -- Weightloss
            ((SELECT id FROM service_category WHERE name = 'Weightloss'), 'GLP-1 Antagonists', 'Weight management medications'),

            -- IV Therapy
            ((SELECT id FROM service_category WHERE name = 'IV Therapy'), 'IV Therapy', 'Intravenous treatments'),

            -- Vitamin Injections
            ((SELECT id FROM service_category WHERE name = 'Vitamin Injections'), 'Vitamin Injections', 'Vitamin supplement injections'),

            -- Peptide Therapy
            ((SELECT id FROM service_category WHERE name = 'Peptide Therapy'), 'Peptide Therapy', 'Peptide-based treatments'),

            -- Facials
            ((SELECT id FROM service_category WHERE name = 'Facials'), 'Hydrafacial', 'Hydrafacial treatments'),
            ((SELECT id FROM service_category WHERE name = 'Facials'), 'SilkPeel', 'SilkPeel treatments'),
            ((SELECT id FROM service_category WHERE name = 'Facials'), 'Diamond Glow', 'Diamond Glow treatments'),
            ((SELECT id FROM service_category WHERE name = 'Facials'), 'Other facial', 'Other facial treatments');

            -- Create a temporary table for service products
            CREATE TEMP TABLE temp_service_products (
                category_name text,
                type_name text,
                product_name text,
                supplier text
            );

            -- Insert service products data
            INSERT INTO temp_service_products VALUES
            -- Neuromodulators
            ('Injectables', 'Neuromodulator', 'Botox', 'Allergan'),
            ('Injectables', 'Neuromodulator', 'Daxxify', 'Revance'),
            ('Injectables', 'Neuromodulator', 'Dysport', 'Galderma'),
            ('Injectables', 'Neuromodulator', 'Jeuveau', 'Evolus'),
            ('Injectables', 'Neuromodulator', 'Xeomin', 'Merz'),

            -- HA Dermal Fillers (Allergan)
            ('Injectables', 'HA Dermal Filler', 'Juvederm Ultra XC', 'Allergan'),
            ('Injectables', 'HA Dermal Filler', 'Juvederm Ultra Plus XC', 'Allergan'),
            ('Injectables', 'HA Dermal Filler', 'Juvederm Volbella', 'Allergan'),
            ('Injectables', 'HA Dermal Filler', 'Juvederm Vollure', 'Allergan'),
            ('Injectables', 'HA Dermal Filler', 'Juvederm Voluma', 'Allergan'),
            ('Injectables', 'HA Dermal Filler', 'Juvederm Volux', 'Allergan'),
            ('Injectables', 'HA Dermal Filler', 'Juvederm Skinvive', 'Allergan'),

            -- HA Dermal Fillers (Galderma)
            ('Injectables', 'HA Dermal Filler', 'Restylane', 'Galderma'),
            ('Injectables', 'HA Dermal Filler', 'Restylane-L', 'Galderma'),
            ('Injectables', 'HA Dermal Filler', 'Restylane Contour', 'Galderma'),
            ('Injectables', 'HA Dermal Filler', 'Restylane Defyne', 'Galderma'),
            ('Injectables', 'HA Dermal Filler', 'Restylane Eyelight', 'Galderma'),
            ('Injectables', 'HA Dermal Filler', 'Restylane Kysse', 'Galderma'),
            ('Injectables', 'HA Dermal Filler', 'Restylane Lyft', 'Galderma'),
            ('Injectables', 'HA Dermal Filler', 'Restylane Silk', 'Galderma'),
            ('Injectables', 'HA Dermal Filler', 'Restylane Refyne', 'Galderma'),

            -- HA Dermal Fillers (Others)
            ('Injectables', 'HA Dermal Filler', 'RHA 2', 'Revance'),
            ('Injectables', 'HA Dermal Filler', 'RHA 3', 'Revance'),
            ('Injectables', 'HA Dermal Filler', 'RHA 4', 'Revance'),
            ('Injectables', 'HA Dermal Filler', 'RHA Redensity', 'Revance'),
            ('Injectables', 'HA Dermal Filler', 'Revanesse Lips', 'Prollenium'),
            ('Injectables', 'HA Dermal Filler', 'Revanesse Versa', 'Prollenium'),
            ('Injectables', 'HA Dermal Filler', 'Belotero Balance', 'Merz'),

            -- Other Injectables
            ('Injectables', 'Calcium Hydroxyapatite', 'Radiesse', 'Merz'),
            ('Injectables', 'Calcium Hydroxyapatite', 'Hyperdilute Radiesse', 'Merz'),
            ('Injectables', 'Hyaluronidase', 'Hylanex', NULL),
            ('Injectables', 'Polymethyl methacrylate (PMMA)', 'Bellafill', 'Suneva'),
            ('Injectables', 'Poly-L Lactic Acid', 'Sculptra', 'Galderma'),

            -- Peels
            ('Peels', 'Chemical Peel', 'PRX', 'WiQo'),
            ('Peels', 'Chemical Peel', 'VI Peel: Classic Precision Plus', 'VI'),
            ('Peels', 'Chemical Peel', 'SkinMedica: Illuminze', 'Allergan'),
            ('Peels', 'Chemical Peel', 'SkinMedica: Rejuvenize', 'Allergan'),
            ('Peels', 'Chemical Peel', 'SkinMedica: Vitalize', 'Allergan'),
            ('Peels', 'Chemical Peel', 'ZO Skin Health: 3 step peel', 'Zo Skin Health'),
            ('Peels', 'Chemical Peel', 'Perfect DermaPeel', 'Bella Medical Products'),
            ('Peels', 'Chemical Peel', 'TCA', NULL),

            -- Weight Loss
            ('Weightloss', 'GLP-1 Antagonists', 'Trizepatide', NULL),
            ('Weightloss', 'GLP-1 Antagonists', 'Phentermine', NULL),
            ('Weightloss', 'GLP-1 Antagonists', 'Liraglutide', NULL),
            ('Weightloss', 'GLP-1 Antagonists', 'Semaglutide', NULL),

            -- IV Therapy
            ('IV Therapy', 'IV Therapy', 'B Vitamins', NULL),
            ('IV Therapy', 'IV Therapy', 'Vitamin C', NULL),
            ('IV Therapy', 'IV Therapy', 'Glutathione', NULL),
            ('IV Therapy', 'IV Therapy', 'NAD', NULL),

            -- Vitamin Injections
            ('Vitamin Injections', 'Vitamin Injections', 'B-12', NULL),
            ('Vitamin Injections', 'Vitamin Injections', 'MIC', NULL),
            ('Vitamin Injections', 'Vitamin Injections', 'Glutathione', NULL),

            -- Peptide Therapy
            ('Peptide Therapy', 'Peptide Therapy', 'Ipamorelin', NULL),
            ('Peptide Therapy', 'Peptide Therapy', 'CJC', NULL),
            ('Peptide Therapy', 'Peptide Therapy', 'BPC 157', NULL),

            -- PDO Threads
            ('Threads', 'PDO Threads', 'Mint', NULL),
            ('Threads', 'PDO Threads', 'Miracu', NULL),
            ('Threads', 'PDO Threads', 'PDO Max', NULL),
            ('Threads', 'PDO Threads', 'V Soft Lift', NULL),
            ('Threads', 'PDO Threads', 'Viola Threads', NULL),
            ('Threads', 'PDO Threads', 'NovaThreads', NULL),
            ('Threads', 'PDO Threads', 'EuroThreads', NULL)
            ;

            -- Create template service entries
            INSERT INTO service (
                name,
                description,
                category_id,
                service_type_id,
                product,
                supplier,
                price,
                duration,
                active
            )
            SELECT 
                tsp.product_name,
                'Template service for ' || tsp.product_name,
                sc.id as category_id,
                st.id as service_type_id,
                tsp.product_name,
                tsp.supplier,
                0.00,  -- Default price
                0,     -- Default duration
                true   -- Active by default
            FROM temp_service_products tsp
            JOIN service_category sc ON sc.name = tsp.category_name
            JOIN service_type st ON st.name = tsp.type_name AND st.category_id = sc.id
            WHERE tsp.product_name IS NOT NULL;

            -- Clean up
            DROP TABLE temp_service_products;
            """,
            # Reverse migration
            """
            DELETE FROM services WHERE true;
            DELETE FROM service_type WHERE true;
            DELETE FROM service_category WHERE true;
            """
        ),
    ]
