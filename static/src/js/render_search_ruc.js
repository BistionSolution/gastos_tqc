odoo.define("gastos_tqc.js_search_ruc", function (require) {
    "use strict";
    var AbtractAction = require("web.AbstractAction");
    var AbstractField = require("web.AbstractField");
    var core = require("web.core");
    var Widget = require('web.Widget');
    var rpc = require('web.rpc');
    var field_registry = require('web.field_registry');
    var Dialog = require('web.Dialog');
    var QWeb = core.qweb;

    var WidgetSeachruc = AbstractField.extend({
        // template: "gastos_tqc.table_depositos",
        supportedFieldTypes: ['html'],
        init: function (parent, name, record, options) {
            this._super(parent, name, record, options)

            // console.log('VER TABLA : ', this.value)
            // console.log('TABLA PRO : ', this.mode)
            // console.log(this.model)
            // console.log(this.res_id)
            // console.log(this.recordData)
            // this.vali = "jajajaa";
        },
        events: {
            'click .button_search_ruc': '_onClickSearch',
            'click .aceptar_ruc_button': '_onClickAccept',
            'click .cancelar_ruc_button': '_onClickCancel',
            'click .o_data_row': '_onOneClick',
            'dblclick .o_data_row': '_onDoubleClickRow'
        },
        start: function () {
            return this._super.apply(this, arguments);
            // this._drawTeeth()
        },
        isSet: function () {
            return true;
        },
        // _renderEdit:function () {
        //     console.log("render function agaaa")
        //     var self = this
        //
        // },
        _render: async function () {
            var self = this;
            await this._super(...arguments);
            // const result = await this._rpc({
            //     model: 'tqc.detalle.liquidaciones',
            //     method: 'search_read',
            //     domain:[['liquidacion_id','=',self.res_id],['state','=','historial']],
            // });
            const elem = QWeb.render('search_ruc', {
                // expenses: result
            });
            self.$el.html(elem);

            self.$el.addClass('search_aument')
            $('.modal-footer').append('<button class="aceptar_ruc_button oe_highlight">Aceptar</button>')

            // var $row = this._super(record);
            // // Add progress bar widget at the end of rows
            // var $td = $('<td/>', {class: 'o_data_cell o_skill_cell'});
            // var progress = new FieldProgressBar(this, 'level_progress', record, {
            //     current_value: record.data.level_progress,
            //     attrs: this.arch.attrs,
            // });
            // progress.appendTo($td);
            // return $row.append($td);
        },
        _renderReadonly: function () {
            // console.log("RENDER READONLY")
        },
        _onClickSearch: async function () {
            var self = this
            let ruc = $(self.$el).find('#ruc').val()
            $(self.$el).find('tbody').find('tr').remove();
            await self._rpc({ //envia el modelo, parametos
                model: "tqc.detalle.liquidaciones",
                method: "search_ruc",
                args: [{'ruc': ruc}],
                kwargs: {}
            }).then(function (proveedores) {
                _.each(proveedores, function (prob, key) {
                    console.log({prob})
                    var addRows = [$('<td>', {
                            class: 'o_data_cell o_field_cell o_list_char',
                            tabindex: -1
                        }).attr('data-id', key).append(prob.ruc.trimStart()),
                    $('<td>', {
                            class: 'o_data_cell o_field_cell o_list_char',
                            tabindex: -1
                        }).attr('data-id', key).append(prob.razon.trimStart())]

                    var $rows = $('<tr/>', {class: 'o_data_row'}).attr('onselectstart',"return false").append(addRows)
                    $(self.$el).find('tbody').append($rows);
                })
            })
        },
        _onClickAccept: function () {
            $("input[name='ruc']").val($('#clickruc').val())
            $("input[name='ruc']").trigger("change");
            $('.modal').remove()
        },
        _onClickCancel: function () {
            $('.modal').remove()
        },
        _onOneClick: function (e) {
            $("#clickruc").val(e.currentTarget.cells[0].innerText)
        },
        _onDoubleClickRow: function (e) {
            $("input[name='ruc']").val(e.currentTarget.cells[0].innerText)
            $("input[name='ruc']").trigger("change");
            $('.modal').remove()
        }
    })

    field_registry.add("search_ruc", WidgetSeachruc);

    return WidgetSeachruc;
});