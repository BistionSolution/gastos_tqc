# -*- coding: utf-8 -*-
{
    'name': "gastos_tqc",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Millenium",
    'website': "https://www.mbcorpsa.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'base_setup', 'hr'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/res_group.xml',
        'security/ir_rules.xml',

        'data/cuenta_gastos_default.xml',

        'report/templates.xml',
        'report/report_sheets.xml',

        'views/liquidaciones.xml',
        'views/registrar_gasto.xml',
        'views/res_config_settings.xml',
        'views/cuenta_contable.xml',
        'views/tipo_documentos.xml',
        'views/tqc_autorizadores.xml',
        'views/hr_employee.xml',
        'views/tqc_impuestos.xml',
        'views/cuenta_gastos_default.xml',
        'views/detalle_liquidaciones.xml',
        'views/historial_liquidaciones.xml',
        'views/sincronizar_tqc.xml',

        'wizard/search_ruc.xml',
        'wizard/search_client.xml',
        'wizard/cuenta_contable.xml',
        'assets.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'qweb': [
        'static/src/xml/liquidacion_header.xml',
        'static/src/xml/select_onemany.xml',
        'static/src/xml/table_depositos.xml',
        'static/src/xml/search_exactus.xml',
        'static/src/xml/cuenta_contable.xml'
    ],
    'application': True,
    # 'assets': {
    #     'web.assets_backend': [
    #         'gastos_tqc/static/src/js/liquidacion_header.js',
    #         'gastos_tqc/static/src/scss/gastos_tqc.scss',
    #     ],
    #     'web.assets_qweb': [
    #         'gastos_tqc/static/src/xml/liquidacion_header.xml',
    #     ],
    # },
}
