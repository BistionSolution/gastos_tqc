odoo.define('gastos_tqc.liquidacion_tree', function (require) {
    "use strict";
    // var DocumentUploadMixin = require('hr_expense.documents.upload.mixin');
    var ListController = require('web.ListController');
    var ListView = require('web.ListView');
    var viewRegistry = require('web.view_registry');
    var core = require('web.core');
    var ListRenderer = require('web.ListRenderer');
    var session = require('web.session');
    var dom = require('web.dom');
    var rpc = require('web.rpc');

    const config = require('web.config');

    const {Component} = owl;
    const {useState} = owl.hooks;

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
            init: function (parent, name, record, options) {
                this._super(parent, name, record, options)
                // console.log('TABLA PRO : ', this.mode)
                // console.log(this.model)
                // console.log(this.res_id)
                // console.log(this.recordData)
                // console.log(this.state)
            },
            events: _.extend({}, ListRenderer.prototype.events, {
                'click .o_context_one': '_context_jefe',
                'click .o_context_two': '_context_contable',
                'click .o_context_three': '_context_pendientes',
            }),
            _render: async function () {
                var self = this;
                this._super(...arguments);
                console.log("user id : ", session.user_id)
                await self._rpc({
                    model: 'tqc.liquidaciones',
                    method: 'get_count_states',
                    args: [{'user_id': session.user_id[0]}]
                    // context: this.context,
                }).then(function (count_state) {
                    self._rpc({
                        model: 'tqc.liquidaciones',
                        method: 'search_employee',
                        // context: this.context,
                    }).then(function (employee) {
                        console.log(employee)
                        if (employee) {
                            self.$el.parent().prev().find('#mydata').remove()
                            self.$el.parent().prev().prepend("<span id='mydata'>" + employee[0] + " - " + employee[1] + "</span>")
                        }
                    });

                    // self.$el.parent().find('.o_expense_container').remove();
                    const elem = QWeb.render('gastos_tqc.dashboard_liquid_tqc', {
                        expenses: count_state,
                        // render_monetary_field: self.render_monetary_field,
                    });

                    // $('.breadcrumb').append('<span>HOLA GA</span>');
                    // console.log("VAMOS A VER ",dom)
                    self.$el.before(elem);
                })
                if (self.state.domain[2]) {
                    self.$el.find('.o_expense_container').children().find(`#${self.state.domain[2][2]}`).addClass('button_black')

                }


            },
            _context_jefe: function (e) {
                var self = this;
                e.preventDefault();
                var $action = $(e.currentTarget);
                this.trigger_up('dashboard_open_action', {
                    action_name: "gastos_tqc.action_view_tree_liquidaciones",
                    action_context: $action.attr('context'),
                });
            },
            _context_contable: function (e) {
                var self = this;
                e.preventDefault();
                var $action = $(e.currentTarget);
                this.trigger_up('dashboard_open_action', {
                    action_name: "gastos_tqc.action_view_contable_liquidaciones",
                    action_context: $action.attr('context'),
                });
            },
            _context_pendientes: function (e) {
                e.preventDefault();
                var $action = $(e.currentTarget);
                this.trigger_up('dashboard_open_action', {
                    action_name: "gastos_tqc.action_view_pendiente_liquidaciones",
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

    var tqcRegistroListRenderer = ListRenderer.extend({
        init: function (parent, name, record, options) {
            this._super(parent, name, record, options)
        },
        _render: async function () {
            var self = this;
            this._super(...arguments);
            self._rpc({
                model: 'tqc.liquidaciones',
                method: 'search_employee',
                // context: this.context,
            }).then(function (employee) {
                console.log(employee)
                if (employee) {
                    self.$el.parent().prev().find('#mydata').remove()
                    self.$el.parent().prev().prepend("<span id='mydata'>" + employee[0] + " - " + employee[1] + "</span>")
                }
            });
            // self._rpc({
            //     model: 'hr.employee',
            //     method: 'search_read',
            //     domain: [['user_id', '=', session.user_id]],
            //     sudo: true,
            //     // context: this.context,
            // }).then(function (employee) {
            //     if (employee.length !== 0) {
            //         self.$el.parent().prev().find('#mydata').remove()
            //         self.$el.parent().prev().prepend("<span id='mydata'>" + employee[0].name + " - " + employee[0].department_id[1] + "</span>")
            //     }
            // });


        }
    });

    var tqcRegisterHeader = ListView.extend({
        config: _.extend({}, ListView.prototype.config, {
            Renderer: tqcRegistroListRenderer
        })
    });

    viewRegistry.add('gastos_tqc_tree_selections', tqcExpensesListViewDashboardHeader);
    viewRegistry.add('gastos_view_name', tqcRegisterHeader);
});
