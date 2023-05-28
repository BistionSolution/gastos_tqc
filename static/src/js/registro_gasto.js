odoo.define('gastos_tqc.registro_gasto', function (require) {
"use strict";
    // var DocumentUploadMixin = require('hr_expense.documents.upload.mixin');
    var ListController = require('web.ListController');
    var ListView = require('web.ListView');
    var viewRegistry = require('web.view_registry');
    var core = require('web.core');
    var ListRenderer = require('web.ListRenderer');

    var QWeb = core.qweb;

    var tqcResgistroRender = ListRenderer.extend({
        events:_.extend({}, ListRenderer.prototype.events, {
            'click .o_context_one': '_context_register',
        }),
        _renderView: async function () {
            var self = this;
            await this._super(...arguments);
            const result = await this._rpc({
                model: 'tqc.liquidaciones',
                method: 'get_expense_dashboard',
                context: this.context,
            });

            self.$el.parent().find('.o_expense_container').remove();
            const elem = QWeb.render('gastos_tqc.dashboard_registro_gasto', {
                expenses: result,
                // render_monetary_field: self.render_monetary_field,
            });
            self.$el.prepend(elem);
        },
        _context_register: function (e) {
            console.log("PRIMERO  ESTA")
            e.preventDefault();
            var $action = $(e.currentTarget);
            this.trigger_up('dashboard_open_action', {
                action_name: "gastos_tqc.action_view_filter_gastos",
                action_context: $action.attr('context'),
            });
        }
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

    var tqcRegistroDashboardController = ListController.extend({
        custom_events: _.extend({}, ListController.prototype.custom_events, {
            dashboard_open_action: '_onDashboardOpenAction',
        }),

        /**
         * @private
         * @param {OdooEvent} e
         */
        _onDashboardOpenAction: function (e) {
            return this.do_action(e.data.action_name,
                {additional_context: JSON.parse(e.data.action_context)});
        },
    });


    var tqcExpensesListViewDashboardHeader = ListView.extend({
        config: _.extend({}, ListView.prototype.config, {
            Renderer: tqcResgistroRender,
            Controller: tqcRegistroDashboardController
        })
    });

    viewRegistry.add('registro_tqc_tree_selections', tqcExpensesListViewDashboardHeader);
});
