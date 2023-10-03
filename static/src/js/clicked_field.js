/** @odoo-modules */
//import { Component, useState } from "@odoo/owl";
const {Component, useState} = owl;
import {standardFieldProps} from "@web/views/fields/standard_field_props";
import {registry} from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

export class MyTextField extends Component {
    static template = 'gastos_tqc.componentGlobal'

    setup() {
        this.action = useService("action");
        this.state = useState({value: 0});
        this.searchState = useState({value: false});
    }

    increment() {
        this.state.value++;
    }

    // onChange(newValue) {
    //     this.props.update(newValue);
    // }
    _onClickInput(event) {
        event.stopPropagation();
        this.searchState.value = !this.searchState.value
    }

    _onClickRuc(event) {
        event.stopPropagation();
        // Abrir ventana modal de una tabla existente con do_action

        console.log("CLICK RUC")
        var self = this;
        var action = {
            name: 'Buscar RUC',
            type: 'ir.actions.act_window',
            res_model: 'tqc.searchruc',
            views: [[false, 'form']],
            view_type: 'form',
            target: 'new'
        }
        this.action.doAction(action);
        var options = {}
        // options.on_close = function () {
        //     var self = this;
        //     // $("input[name='ruc']").val($('#result').text())
        //     // $("input[name='ruc']").trigger("change");
        //     // self.trigger_up('reload')
        // }
        this.action.doAction(action)
        // self.do_action(action, options).then(function () {
        //     var self = this
        //     console.log("SELF GAAA ; ", self)
        // });
    }
}

// MyTextField.props = {
//     ...standardFieldProps,
// };
// owl.utils.whenReady().then(() => {
//     const my_counter = new Counter();
//     my_counter.mount(document.body);
// });

registry.category("fields").add("counterMax", MyTextField)