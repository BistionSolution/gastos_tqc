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
    'depends': ['base', 'web', 'base_setup', 'hr'],

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
        'views/hr_department.xml',
        'views/tqc_impuestos.xml',
        'views/cuenta_gastos_default.xml',
        'views/detalle_liquidaciones.xml',
        'views/historial_liquidaciones.xml',
        'views/sincronizar_tqc.xml',

        'wizard/search_ruc.xml',
        'wizard/search_client.xml',
        'wizard/cuenta_contable.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'application': True,
    'assets': {
        'web.assets_backend': [

            # # 'gastos_tqc/static/src/views/*.js',
            # # 'gastos_tqc/static/src/**/*.xml',
            # # 'gastos_tqc/static/src/js/liquidacion_header.js',
            # # 'gastos_tqc/static/src/js/registro_gasto.js',
            # 'gastos_tqc/static/src/scss/gastos_tqc.scss',
            # 'gastos_tqc/static/src/scss/table_liqui.scss',
            # 'gastos_tqc/static/src/scss/modal_style.scss',
            #
            # # split view
            # 'gastos_tqc/static/src/views/split_view/side_form_view.scss',
            #
            # # 'gastos_tqc/static/src/views/split_view/x2many_field.xml',
            #
            # 'gastos_tqc/static/src/views/split_view/side_form_status_indicator.xml',
            # 'gastos_tqc/static/src/views/split_view/side_form_control_panel.xml',
            # 'gastos_tqc/static/src/views/split_view/side_form_controller.xml',
            # 'gastos_tqc/static/src/views/split_view/side_form_view_container.xml',
            #
            # # 'gastos_tqc/static/src/views/split_view/list_controller.xml',
            # 'gastos_tqc/static/src/views/split_view/list_renderer.xml',
            #
            # # views header flujo
            # 'gastos_tqc/static/src/views/header_flujo.xml',
            # 'gastos_tqc/static/src/views/hide_icon_delete.xml',
            # 'gastos_tqc/static/src/views/one2many_selectable.xml',
            #
            # # views js
            # 'gastos_tqc/static/src/views/header_flujo.js',
            # 'gastos_tqc/static/src/views/header_registry.js',
            # 'gastos_tqc/static/src/views/hide_icon_delete.js',
            # 'gastos_tqc/static/src/views/one2many_selectable.js',
            #
            # # INTERACT
            # 'gastos_tqc/static/src/lib/interact.min.js',
            #
            # 'gastos_tqc/static/src/views/split_view/hooks.js',
            #
            # 'gastos_tqc/static/src/views/split_view/with_search.js',
            #
            # 'gastos_tqc/static/src/views/split_view/form_view.js',
            # 'gastos_tqc/static/src/views/split_view/side_form_status_indicator.js',
            # 'gastos_tqc/static/src/views/split_view/side_form_control_panel.js',
            # 'gastos_tqc/static/src/views/split_view/side_form_controller.js',
            # 'gastos_tqc/static/src/views/split_view/side_form_view_container.js',
            #
            # 'gastos_tqc/static/src/views/split_view/list_arch_parser.js',
            # # 'gastos_tqc/static/src/views/split_view/list_controller.js',
            # 'gastos_tqc/static/src/views/split_view/list_renderer.js',
            #
            # # 'gastos_tqc/static/src/js/modal_search.js',
            # # 'gastos_tqc/static/src/js/clicked_field.js',
            # 'gastos_tqc/static/src/js/wiget_text.js',
            # # 'gastos_tqc/static/src/js/render_search_ruc.js',
            # # 'gastos_tqc/static/src/js/render_search_client.js',
            # # 'gastos_tqc/static/src/js/get_cuenta_contable.js',
            #
            # # 'gastos_tqc/static/src/js/list_renderer.js',
            # # 'gastos_tqc/static/src/js/web_client.js',
        ],
        # 'web.assets_qweb': [
        #     'gastos_tqc/static/src/xml/liquidacion_header.xml',
        # ],
    },
}
