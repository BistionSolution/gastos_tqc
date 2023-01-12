# -*- coding: utf-8 -*-
{
    'name': "gastos_tqc",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/ir_rules.xml',
        'security/res_group.xml',

        'views/liquidaciones.xml',
        'views/templates.xml',
        'views/cuenta_contable.xml',
        'views/tipo_liquidaciones.xml',
        'views/tipo_documentos.xml',
        'views/registrar_gasto.xml',
        'assets.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'qweb': [
        'static/src/xml/liquidacion_header.xml',
        'static/src/xml/select_onemany.xml',
        'static/src/xml/table_depositos.xml'
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
