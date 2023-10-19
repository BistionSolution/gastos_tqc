/** @odoo-module **/
import {registry} from "@web/core/registry";
import {useInputField} from "@web/views/fields/input_field_hook";
import time from 'web.time';
import {useService} from "@web/core/utils/hooks";

const rpc = require('web.rpc');
var translation = require('web.translation');
var _t = translation._t;
const {onWillStart, Component, useRef, useState} = owl;

export class DomainSelectorTextField extends Component {
    static template = 'gastos_tqc.searchProveedor'

    setup() {
        super.setup();
        this.action = useService("action");
        this.input = useRef('inputdate')
        this.state = useState({value: false});
        this.modalState = useState({value: false});
        this.textSearch = useState({text: ""});
        this.readonlyMode = useState({value: false})
        this.data = useState({value: []});
        onWillStart(() => this._loadPro());
        useInputField({getValue: () => this.props.value || "", refName: "inputdate"});
    }

    async _loadPro() {
        const modeRecord = this.props.record.model.root.data.state
        const habilitado_state = this.props.record.model.root.data.habilitado_state
        const mode_view = this.props.record.context.mode_view

        if (modeRecord === "jefatura" || ((habilitado_state !== 'habilitado') && (mode_view !== "flujo"))) {
            this.readonlyMode.value = true
        }
    }

    _onSelectDateField(ev) {
        ev.stopPropagation();
        this.state.value = true
        console.log("entro")
        if (this.input.el) {
            this.state.value = true
        } else {
            console.log("cerardo2")
        }
    }

    _onClearDateField(ev) {
        // ev.stopPropagation();
        console.log("SALIO")
        setTimeout(() => {
            this.state.value = false
        }, 200);

        // this.props.update(null);
    }

    _onClickRuc(event) {
        // event.stopPropagation();
        // Abrir ventana modal de una tabla existente con do_action
        this.modalState.value = true
    }

    _onClickRucClose(event) {
        this.modalState.value = false
    }

    _onClickSearch(event) {
        // this.textSearch.text = $(this.input.el).val()
        let self = this;
        console.log("this.textSearch.text", this.textSearch.text)
        // this.data.value = []

        // llamar metodo search_ruc de la tabla tqc.detalle.liquidaciones
        rpc.query({
            model: 'tqc.detalle.liquidaciones',
            method: 'search_ruc',
            args: [{'ruc': this.textSearch.text}],
        }).then(function (data) {
            console.log("data es : ", data)
            self.data.value = data
        });
    }

    _onClickRow(event) {
        // evitar propagacion
        event.stopPropagation();
        this.input.el.value = event.currentTarget.cells[0].innerText
        this.props.update(event.currentTarget.cells[0].innerText);
        this.modalState.value = false
    }
}

registry.category("fields").add("search_supplier", DomainSelectorTextField);