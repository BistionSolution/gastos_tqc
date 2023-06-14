odoo.define('gastos_tqc.go_selectable', function (require) {
    "use strict";
    var utils = require('web.utils');
    var core = require('web.core');
    var _t = core._t;
    var rpc = require('web.rpc');
    var field_registry = require('web.field_registry');
    var ListRenderer = require('web.ListRenderer');
    var FieldOne2Many = require('web.relational_fields').FieldOne2Many;
    var fields = require('web.relational_fields');

    ListRenderer.include({
        init: function (parent, state, params) {
            this._super.apply(this, arguments);
        }, events: _.extend({}, ListRenderer.prototype.events, {
            'click tbody .search_ruc': '_onClickRuc',
            'click tbody .search_client': '_onClickClient'
        }),
        _updateSelection: function () {
            const previousSelection = JSON.stringify(this.selection);
            this.selection = [];
            var self = this;
            var $inputs = this.$('tbody .o_list_record_selector input:visible:not(:disabled)');
            var allChecked = $inputs.length > 0;
            $inputs.each(function (index, input) {
                if (input.checked) {
                    self.selection.push($(input).closest('tr').data('id'));
                } else {
                    allChecked = false;
                }
            });
            if (this.selection.length > 0) {
                $('.button_delete_order_lines').show()
                $('.button_select_order_lines').show()
            } else {
                $('.button_delete_order_lines').hide()
                $('.button_select_order_lines').hide()
            }
            this.$('thead .o_list_record_selector input').prop('checked', allChecked);
            if (JSON.stringify(this.selection) !== previousSelection) {
                this.trigger_up('selection_changed', {allChecked, selection: this.selection});
            }
            // this.trigger_up('selection_changed', {selection: this.selection});
            this._updateFooter();
        },
        _renderRows: function () {
            var $rows = this.state.data.map(this._renderRow.bind(this));
            // permite quitar por estado de la solicitud para poder quitar el editar
            if (this.__parentedParent.model === 'tqc.liquidaciones') {
                // if (this.addCreateLine && this.__parentedParent.recordData.habilitado_state !== ['proceso','corregir']) {
                let stado = ['proceso', 'corregir'];
                if (this.addCreateLine && stado.indexOf(this.__parentedParent.recordData.habilitado_state) === -1) {
                    var $tr = $('<tr>');
                    var colspan = this._getNumberOfCols();

                    if (this.handleField) {
                        colspan = colspan - 1;
                        $tr.append('<td>');
                    }

                    var $td = $('<td>')
                        .attr('colspan', colspan)
                        .addClass('o_field_x2many_list_row_add');
                    $tr.append($td);
                    $rows.push($tr);

                    if (this.addCreateLine) {
                        _.each(this.creates, function (create, index) {
                            var $a = $('<a href="#" role="button">')
                                .attr('data-context', create.context)
                                .text(create.string);
                            if (index > 0) {
                                $a.addClass('ml16');
                            }
                            $td.append($a);
                        });
                    }
                }
            } else {
                if (this.addCreateLine) {
                    var $tr = $('<tr>');
                    var colspan = this._getNumberOfCols();

                    if (this.handleField) {
                        colspan = colspan - 1;
                        $tr.append('<td>');
                    }

                    var $td = $('<td>')
                        .attr('colspan', colspan)
                        .addClass('o_field_x2many_list_row_add');
                    $tr.append($td);
                    $rows.push($tr);

                    if (this.addCreateLine) {
                        _.each(this.creates, function (create, index) {
                            var $a = $('<a href="#" role="button">')
                                .attr('data-context', create.context)
                                .text(create.string);
                            if (index > 0) {
                                $a.addClass('ml16');
                            }
                            $td.append($a);
                        });
                    }
                }
            }
            return $rows;
        },
        // _onCellClick: function (event) {
        //     // this._super(...arguments);
        //     console.log("GOES")
        //     // The special_click property explicitely allow events to bubble all
        //     // the way up to bootstrap's level rather than being stopped earlier.
        //     var $td = $(event.currentTarget);
        //     var $tr = $td.parent();
        //
        //     // detecta si existe el widget one2many selecteable
        //     if ($tr.find('.o_list_record_selector').length > 0) {
        //         var rowIndex = $tr.prop('rowIndex') - 2;
        //     } else {
        //         var rowIndex = $tr.prop('rowIndex') - 1;
        //     }
        //     // var rowIndex = $tr.prop('rowIndex') - 1;
        //
        //     if (!this._isRecordEditable($tr.data('id')) || $(event.target).prop('special_click')) {
        //         return;
        //     }
        //     var fieldIndex = Math.max($tr.find('.o_field_cell').index($td), 0);
        //
        //     console.log("td: ", $td)
        //
        //     if ($tr.find('.o_list_record_selector').length > 0) {
        //         this._selectCell(rowIndex, fieldIndex, {event: event});
        //
        //     } else {
        //         this._selectCell(rowIndex, fieldIndex, {event: event}).then(function () {
        //             // add button with custom code bistion
        //             if ($td.hasClass('consult_ruc')) {
        //                 $td.addClass('overnone');
        //                 $td.append($('<button>', {
        //                     'class': 'search_ruc fa fa-search', 'name': 'search',
        //                 }))
        //
        //             } else {
        //                 if ($td.hasClass('consult_client')) {
        //                     $td.addClass('overnone');
        //                     $td.append($('<button>', {
        //                         'class': 'search_client fa fa-search', 'name': 'search',
        //                     }))
        //                 } else {
        //                     $('.search_ruc').remove()
        //                     $('.search_client').remove()
        //                 }
        //             }
        //         });
        //     }
        //
        // },
        _selectCell: function (rowIndex, fieldIndex, options) {
            var selectCell = this._super.apply(this, arguments);
            if (options && options.event?.currentTarget) {
                var $td = $(options.event.currentTarget)
                return selectCell.then(function () {
                    console.log("se", this)
                    if ($td.hasClass('consult_ruc')) {
                        $('.search_ruc').remove()
                        $td.addClass('overnone');
                        // var newButton = '<button class="search_ruc fa fa-search" name="search">new button</button>'
                        $td.append($('<button>', {
                            'class': 'search_ruc fa fa-search', 'name': 'search',
                        }))
                        $('.search_client').remove()
                        // $(options.event.target).append($('<button>', {
                        //     'class': 'search_ruc fa fa-search', 'name': 'search',
                        // }))
                    } else {
                        if ($td.hasClass('consult_client')) {
                            $('.search_client').remove()
                            $td.addClass('overnone');
                            $td.append($('<button>', {
                                'class': 'search_client fa fa-search', 'name': 'search',
                            }))
                            $('.search_ruc').remove()
                        } else {
                            $('.search_ruc').remove()
                            $('.search_client').remove()
                        }
                    }
                })
            }

            return selectCell
        },
        _onClickRuc: function (event) {
            var changes = {}

            var self = this;
            // changes['glosa_entrega'] = "GAAAAAAAA";
            // this.trigger_up('field_changed', {
            //     dataPointID: self.dataPointID,
            //     changes: changes,
            //     viewType: self.viewType,
            // });

            var action = {
                name: 'Buscar RUC',
                type: 'ir.actions.act_window',
                res_model: 'tqc.searchruc',
                views: [[false, 'form']],
                view_type: 'form',
                target: 'new'
            }
            var options = {}
            options.on_close = function () {
                var self = this;
                // $("input[name='ruc']").val($('#result').text())
                // $("input[name='ruc']").trigger("change");
                // self.trigger_up('reload')
            }
            self.do_action(action, options).then(function () {
                var self = this
                console.log("SELF GAAA ; ", self)
            });

            //    return this.do_action(action, { on_close: function () {
            //        self.trigger_up('reload', { keepChanges: true });
            // } });


            // new view_dialogs.FormViewDialog(this, {
            //     res_model: 'sale.order', // the model name
            //     res_id: 1, // the primary key of the model
            //     title: "Sale Order with ID of 1", // dialog title, optional
            //     on_saved: function (record) { // the action that will be executed if user clicks the Save button
            //         console.log("The user clicks the Save button");
            //     }
            // }).open();
        },
        _onClickClient: function () {
            var self = this;
            var action = {
                name: 'Buscar Cliente',
                type: 'ir.actions.act_window',
                res_model: 'tqc.searchclient',
                views: [[false, 'form']],
                view_type: 'form',
                target: 'new'
            }
            var options = {}
            options.on_close = function () {
                var self = this;
                // $("input[name='ruc']").val($('#result').text())
                // $("input[name='ruc']").trigger("change");
                // self.trigger_up('reload')
            }
            self.do_action(action, options).then(function () {
                var self = this
            });
        }
    })

    var One2Manyble = FieldOne2Many.extend({
        template: 'One2ManySelectable',
        supportedFieldTypes: ['one2many'], // multi_selection: true,
        //button click
        events: _.extend({}, fields.FieldOne2Many.prototype.events, {
            "click .button_delete_order_lines": "delete_selected_lines",
            "click .button_select_order_lines": "selected_lines",
        }),
        init: function () {
            this._super.apply(this, arguments);
        },
        // start: function () {
        // 	this._super.apply(this, arguments);
        // 	// $('.o_field_x2many_list_row_add').hide()
        // },
        delete_selected_lines: function () {
            var self = this;
            var current_model = this.recordData[this.name].model;
            var selected_lines = self.find_deleted_lines();

            if (selected_lines.length === 0) {
                this.do_warn(_t("Please Select at least One Record."));
                return false;
            }

            var w_response = confirm("¿Seguro que deseas rechazar los documentos seleccionados?");
            if (w_response) {
                rpc.query({
                    'model': current_model,
                    'method': 'write',
                    'args': [selected_lines, {
                        'revisado_state': 'rechazado_' + this.recordData.state
                    }],
                }).then(function (result) {
                    // console.log("VAMOS CON VAMOSS : ")
                    // console.log("VAMOS CON model : ", self.model)
                    // if (self.model === 'tqc.liquidaciones') {
                    //     rpc.query({
                    //         'model': self.model,
                    //         'method': 'write',
                    //         'args': [self.res_id, {
                    //             'habilitado_state': 'corregir'
                    //         }],
                    //     }).then(function (e) {
                    //         self.trigger_up('reload');
                    //     });
                    // }
                    self.trigger_up('reload');
                });
            }
        },
        selected_lines: function () {
            var self = this;
            var current_model = this.recordData[this.name].model;
            var selected_lines = self.find_selected_lines();
            if (selected_lines.length === 0) {
                this.do_warn(_t("Please Select at least One Record"));
                return false;
            }
            var w_response = confirm("Dou You Want to Select ?");
            if (w_response) {

                rpc.query({
                    'model': current_model, 'method': 'write', 'args': [selected_lines, {
                        'revisado_state': 'aprobado',
                    }],
                }).then(function (result) {
                    self.trigger_up('reload');
                });
            }
        },
        _getRenderer: function () {
            var self = this
            // console.log("data USER PRO : ", self.recordData.uid_create)
            // var state = self.recordData.state
            // var user = false
            if (self.view.arch.tag === 'kanban') {
                return One2ManyKanbanRenderer;
            }
            if (self.view.arch.tag === 'tree') {
                console.log("self.recordData.state : ", self.recordData)
                if ((self.recordData.state === 'jefatura' && self.recordData.uid_create === 3 && self.recordData.current_user == 1) || self.recordData.state === 'contable' && self.recordData.uid_create === 2) {
                    return ListRenderer.extend({
                        init: function (parent, state, params) {
                            var self = this
                            self._super.apply(self, arguments);
                            self.hasSelectors = self;
                        },
                    });
                }
            }
            return this._super.apply(this, arguments);
        },
        find_deleted_lines: function () {
            var self = this;
            var selected_list = [];
            this.$el.find('td.o_list_record_selector input:checked')
                .closest('tr').each(function () {
                selected_list.push(parseInt(self._getResId($(this).data('id'))));
            });
            return selected_list;
        },
        find_selected_lines: function () {
            var self = this;
            var selected_list = [];
            var selected_list1 = [];
            var selected_list2 = [];
            this.$el.find('td.o_list_record_selector input:checked')
                .closest('tr').each(function () {
                selected_list.push(parseInt(self._getResId($(this).data('id'))));
            });
            if (selected_list.length != 0) {
                this.$el.find('td.o_list_record_selector')
                    .closest('tr').each(function () {
                    selected_list1.push(parseInt(self._getResId($(this).data('id'))));
                });
                selected_list2 = selected_list1.filter(function (x) {
                    return selected_list.indexOf(x) < 0
                });
            }
            return selected_list2;
        },
        _getResId: function (recordId) {
            var record;
            utils.traverse_records(this.recordData[this.name], function (r) {
                if (r.id === recordId) {
                    record = r;
                }
            });
            return record.res_id;
        },
    });
    // register unique widget, because Odoo does not know anything about it
    //you can use <field name="One2many_ids" widget="x2many_selectable"> for call this widget
    field_registry.add("select_onemany", One2Manyble);
});
