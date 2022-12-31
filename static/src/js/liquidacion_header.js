odoo.define('gastos_tqc.liquidacion_tree', function (require) {
    "use strict";
    // var DocumentUploadMixin = require('hr_expense.documents.upload.mixin');
    var ListController = require('web.ListController');
    var ListView = require('web.ListView');
    var viewRegistry = require('web.view_registry');
    var core = require('web.core');
    var ListRenderer = require('web.ListRenderer');
    var session = require('web.session');
    const config = require('web.config');

    var QWeb = core.qweb;

    // var tqcExpensesListController = ListController.extend(DocumentUploadMixin, {
    //     buttons_template: 'ExpensesListView.buttons',
    //     events: _.extend({}, ListController.prototype.events, {
    //         'click .o_button_upload_expense': '_onUpload',
    //         'change .o_expense_documents_upload .o_form_binary_form': '_onAddAttachment',
    //     }),
    //     /**
    //      * @override
    //      */
    //      init: function () {
    //         this._super.apply(this, arguments);
    //         this.isMobile = config.device.isMobileDevice;
    //     },
    // });

    // Expense List Renderer
    var tqcExpenseListRendererHeader = ListRenderer.extend({
            events: _.extend({}, ListRenderer.prototype.events, {
                'click .o_context_one': '_context_jefe',
                'click .o_context_two': '_context_contable',
            }),
            _renderView: async function () {
                var self = this;
                await this._super(...arguments);
                console.log("ENTRO CORECTO ");
                const result = await this._rpc({
                    model: 'tqc.liquidaciones',
                    method: 'get_expense_dashboard',
                    context: this.context,
                });

                self.$el.parent().find('.o_expense_container').remove();
                const elem = QWeb.render('gastos_tqc.dashboard_liquid_tqc', {
                    expenses: result,
                    // render_monetary_field: self.render_monetary_field,
                });
                self.$el.prepend(elem);
            },
            _context_jefe: function (e) {
                e.preventDefault();
                var $action = $(e.currentTarget);
                this.trigger_up('dashboard_open_action', {
                    action_name: "gastos_tqc.action_view_tree_liquidaciones",
                    action_context: $action.attr('context'),
                });
            },
            _context_contable: function (e) {
                e.preventDefault();
                var $action = $(e.currentTarget);
                this.trigger_up('dashboard_open_action', {
                    action_name: "gastos_tqc.action_view_contable_liquidaciones",
                    action_context: $action.attr('context'),
                });
            },
            // render_monetary_field: function (value, currency_id) {
            //     value = value.toFixed(2);
            //     var currency = session.get_currency(currency_id);
            //     if (currency) {
            //         if (currency.position === "after") {
            //             value += currency.symbol;
            //         } else {
            //             value = currency.symbol + value;
            //         }
            //     }
            //     return value;
            // }
        }
    );

    var tqcGastosDashboardController = ListController.extend({
        custom_events: _.extend({}, ListController.prototype.custom_events, {
            dashboard_open_action: '_onDashboardOpenAction',
        }),

        /**
         * @private
         * @param {OdooEvent} e
         */
        _onDashboardOpenAction: function (e) {
            console.log("ESEGUNDO ESTA")
            console.log("esta es : ", e.data.action_name)
            return this.do_action(e.data.action_name,
                {additional_context: JSON.parse(e.data.action_context)});
        },
    });


    var tqcExpensesListViewDashboardHeader = ListView.extend({
        config: _.extend({}, ListView.prototype.config, {
            Renderer: tqcExpenseListRendererHeader,
            Controller: tqcGastosDashboardController
        })
    });

    viewRegistry.add('gastos_tqc_tree_selections', tqcExpensesListViewDashboardHeader);
});
