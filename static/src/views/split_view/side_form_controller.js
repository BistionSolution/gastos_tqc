/** @odoo-module **/

import {useService} from '@web/core/utils/hooks';
import {FormController} from '@web/views/form/form_controller';
import {ListController} from "@web/views/list/list_controller";
import {SideFormStatusIndicator} from './side_form_status_indicator';
import {onSideFormBeforeChange} from "./hooks";
import {useSetupView} from "@web/views/view_hook";

const oldSetup = FormController.prototype.setup;
const oldonPagerUpdated = FormController.prototype.onPagerUpdate;
console.log("web_no_auto_save loaded");

export class SideFormController extends FormController {

    setup() {
        super.setup();
        this.actionService = useService('action');
        console.log("SideFormController")
        onSideFormBeforeChange(this.saveButtonClicked.bind(this))
    }

    open(inPopup = false) {
        console.log("Open ---------------")

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

const Formsetup = function () {
    console.log("setup from CIUSTOM");

    useSetupView({
        beforeLeave: () => {
            if (this.model.root.isDirty) {
                if (confirm("---------- Automatically beforeLeave?")) {
                    return this.model.root.save({noReload: true, stayInEdition: true});
                }
                this.model.root.discard();
                return true;

                // Return this.model.root.save({ noReload: true, stayInEdition: true });
            }
        },
        beforeUnload: (ev) => {
            console.log("beforeUnload .................")
            this.beforeUnload(ev)
        },

    });
    const result = oldSetup.apply(this, arguments);
    return result;
};

SideFormController.template = 'gastos_tqc.SideFormView';
FormController.prototype.setup = Formsetup;

const onPagerUpdate = async function () {
    console.log("onPagerUpdate .................")
    this.model.root.askChanges();

    if (this.model.root.isDirty) {
        if (confirm("---------- Automatically onPagerUpdate?")) {
            return oldonPagerUpdated.apply(this, arguments);
        }
        this.model.root.discard();
    }
    return oldonPagerUpdated.apply(this, arguments);
};

FormController.prototype.onPagerUpdate = onPagerUpdate;
const ListSuper = ListController.prototype.setup;
const Listsetup = function () {
    console.log("setup from List CIUSTOM");

    useSetupView({
        rootRef: this.rootRef,
        beforeLeave: () => {
            console.log("beforeLeave .................");
            const list = this.model.root;
            const editedRecord = list.editedRecord;
            console.log("editedRecord", editedRecord);
            if (editedRecord && editedRecord.isDirty) {
                if (confirm("---------- Automatically editedRecord?")) {
                    if (!list.unselectRecord(true)) {
                        throw new Error("View can't be saved");
                    }
                } else {
                    this.onClickDiscard();
                    return true;
                }
            }
        },
    });
    const result = ListSuper.apply(this, arguments);
    return result;
};
ListController.prototype.setup = Listsetup;

SideFormController.components = {
    ...FormController.components,
    SideFormStatusIndicator,
}