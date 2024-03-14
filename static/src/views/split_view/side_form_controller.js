/** @odoo-module **/

import {useService} from '@web/core/utils/hooks';
import {FormController} from '@web/views/form/form_controller';
import {SideFormStatusIndicator} from './side_form_status_indicator';
import {onSideFormBeforeChange} from "./hooks";

export class SideFormController extends FormController {

    setup() {
        super.setup();
        this.actionService = useService('action');
        console.log("SideFormController")
        onSideFormBeforeChange(this.saveButtonClicked.bind(this))
    }

    open(inPopup = false) {
        console.log("Contexto", context)
        const {params, ...context} = this.props.context;

        this.actionService.doAction({
            name: this.env._t(`View Record`),
            res_model: this.props.resModel,
            res_id: this.props.resId,
            views: [[false, 'form']],
            type: 'ir.actions.act_window',
            view_mode: 'form',
            target: inPopup ? 'new' : 'current',
            context: context,
        });
    }

}

SideFormController.template = 'gastos_tqc.SideFormView';

SideFormController.components = {
    ...FormController.components,
    SideFormStatusIndicator,
}