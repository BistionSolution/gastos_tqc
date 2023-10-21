/** @odoo-module **/
import {registry} from '@web/core/registry';
import {formView} from '@web/views/form/form_view';
import {FormController} from '@web/views/form/form_controller';
import {FormRenderer} from '@web/views/form/form_renderer';

const {Component, onMounted, onWillUnmount, onWillUpdateProps, useState} = owl;

export class PosFormController extends FormController {
    setup() {
        super.setup();
        console.log("CARGO CORRECTAMENTE")
    }

    onClickTestJavascript() {
        alert("Hello World");
    }
}

PosFormController.template = "gastos_tqc.buttonForm";

export class PosFormRenderer extends FormRenderer {
    setup() {
        super.setup();
        onMounted(() => {
            console.log("CARGO CORRECTAMENTE montado")
        });
        onWillUpdateProps(async (nextProps) => {
        });

    }

    _MoreOptions() {
        alert("Hello World");
    }
}

registry.category('views').add('button_form_view', {
    ...formView,
    Controller: PosFormController,
    Renderer: PosFormRenderer,
});

