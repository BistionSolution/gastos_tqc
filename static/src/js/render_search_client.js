odoo.define("gastos_tqc.js_search_client", function (require) {
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
        },
        events: {
            'click .button_search_client': '_onClickSearch',
            'click .aceptar_client_button': '_onClickAccept',
            'click .cancelar_client_button': '_onClickCancel',
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
            const elem = QWeb.render('search_client', {
                // expenses: result
            });
            self.$el.html(elem);
            self.$el.addClass('search_aument')
            $('.modal-footer').append('<button class="aceptar_ruc_button oe_highlight">Aceptar</button>')
            // $('.modal-footer').append('<button class="aceptar_ruc_button oe_highlight">Aceptar</button>')

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
        _onClickSearch: function () {
            var self = this
            let client = $(self.$el).find('#client').val()
            self._rpc({ //envia el modelo, parametos
                model: "tqc.detalle.liquidaciones",
                method: "search_client",
                args: [{'client': client}],
                kwargs: {}
            }).then(function (clientes) {
                _.each(clientes, function (client, key) {
                    console.log({client})
                    var addRows = [$('<td>', {
                            class: 'o_data_cell o_field_cell o_list_char',
                            tabindex: -1
                        }).attr('data-id', key).append(client.ruc.trimStart()),
                    $('<td>', {
                            class: 'o_data_cell o_field_cell o_list_char',
                            tabindex: -1
                        }).attr('data-id', key).append(client.razon.trimStart())]

                    var $rows = $('<tr/>', {class: 'o_data_row'}).attr('onselectstart',"return false").append(addRows)
                    $(self.$el).find('tbody').append($rows);
                })
            })
        },
        _onClickAccept: function () {
            $("input[name='cliente']").val($('#clickclient').val())
            $("input[name='cliente']").trigger("change")
            $('.modal').remove()
        },
        _onClickCancel: function () {
            $('.modal').remove()
        },
        _onOneClick: function (e) {
            $("#clickclient").val(e.currentTarget.cells[0].innerText)
        },
        _onDoubleClickRow: function (e) {
            $("input[name='cliente']").val(e.currentTarget.cells[0].innerText)
            $("input[name='cliente']").trigger("change");
            $('.modal').remove()
        }
    })

    field_registry.add("search_client", WidgetSeachruc);

    return WidgetSeachruc;
});