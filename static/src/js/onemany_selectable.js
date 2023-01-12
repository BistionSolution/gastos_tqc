odoo.define('gastos_tqc.go_selectable', function (require) {
    "use strict";
    var utils = require('web.utils');
    var core = require('web.core');
    var QWeb = core.qweb;
    var _t = core._t;
    var rpc = require('web.rpc');
    var field_registry = require('web.field_registry');
    var ListRenderer = require('web.ListRenderer');
    var FieldOne2Many = require('web.relational_fields').FieldOne2Many;

    ListRenderer.include({
        init: function (parent, state, params) {
            this._super.apply(this, arguments);
        },
        _updateSelection: function () {
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
            this.trigger_up('selection_changed', {selection: this.selection});
            this._updateFooter();
        },
        _renderRows: function () {
            var $rows = this.state.data.map(this._renderRow.bind(this));
            console.log('VER TABLA : ', this.value)
            console.log('TABLA xd : ', this.mode)
            // console.log('TABLA model : ', this.recordData[this.name].model)
            console.log(this.model)
            console.log(this.__parentedParent.model)
            console.log(this.res_id)

            // permite quitar por estado de la solicitud para podequitar el editar
            if (this.__parentedParent.model === 'tqc.liquidaciones') {
                // if (this.addCreateLine && this.__parentedParent.recordData.habilitado_state !== ['proceso','corregir']) {
                let stado = ['proceso','corregir'];
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
    })

    var One2Manyble = FieldOne2Many.extend({
        template: 'One2ManySelectable',
        // supportedFieldTypes: ['one2many'],
        // multi_selection: true,
        //button click
        events: {
            "click .button_delete_order_lines": "delete_selected_lines",
            "click .button_select_order_lines": "selected_lines",
        },
        init: function () {
            this._super.apply(this, arguments);
        },
        start: function () {
            return this._super.apply(this, arguments);
            var self = this
            // let este = $(self.$el).find('.st2')
            $('.o_field_x2many_list_row_add').remove();
        },
        // start: function () {
        // 	this._super.apply(this, arguments);
        // 	// $('.o_field_x2many_list_row_add').hide()
        // },
        delete_selected_lines: function () {
            var self = this;
            var current_model = this.recordData[this.name].model;
            var selected_lines = self.find_deleted_lines();
            console.log("VAMOS CON TOD : ", this.res_id)
            console.log("VAMOS CON 2 : ", this.recordData)
            if (selected_lines.length === 0) {
                this.do_warn(_t("Please Select at least One Record."));
                return false;
            }
            var w_response = confirm("Dou You Want to modify ?");
            if (w_response) {
                rpc.query({
                    'model': current_model,
                    'method': 'write',
                    'args': [selected_lines, {
                        'revisado_state': 'rechazado',
                        'state': 'document'
                    }],
                }).then(function (result) {
                    // console.log("VAMOS CON VAMOSS : ")
                    // console.log("VAMOS CON model : ", self.model)
                    if (self.model === 'tqc.liquidaciones') {
                        rpc.query({
                            'model': self.model,
                            'method': 'write',
                            'args': [self.res_id, {
                                'habilitado_state': 'corregir'
                            }],
                        }).then(function (e) {
                            self.trigger_up('reload');
                        });
                    }
                    self.trigger_up('reload');
                });
            }
        },
        selected_lines: function () {
            var self = this;
            var current_model = this.recordData[this.name].model;
            var selected_lines = self.find_deleted_lines();
            console.log("VAMOS selecto : ", selected_lines)
            if (selected_lines.length === 0) {
                this.do_warn(_t("Please Select at least One Record"));
                return false;
            }
            var w_response = confirm("Dou You Want to Select ?");
            if (w_response) {

                rpc.query({
                    'model': current_model,
                    'method': 'write',
                    'args': [selected_lines, {
                        'revisado_state': 'aprobado',
                    }],
                }).then(function (result) {
                    self.trigger_up('reload');
                });
            }
        },
        _getRenderer: function () {
            if (this.view.arch.tag === 'kanban') {
                return One2ManyKanbanRenderer;
            }
            if (this.view.arch.tag === 'tree') {
                return ListRenderer.extend({
                    init: function (parent, state, params) {
                        this._super.apply(this, arguments);
                        this.hasSelectors = true;
                    },
                });
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
