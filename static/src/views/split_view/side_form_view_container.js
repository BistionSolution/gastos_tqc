/** @odoo-module **/

import {Component} from '@odoo/owl';
import {useService} from '@web/core/utils/hooks';
import {FormView} from './form_view';
import {SideFormControlPanel} from './side_form_control_panel';
import {SideFormController} from "./side_form_controller";

const {useEffect, useRef, useChildSubEnv} = owl;

export class SideFormviewContainer extends Component {

    setup() {
        super.setup();
        console.log("AGREGADO SITE FORM")
        useChildSubEnv({
            config: {
                ...this.env.config,
                ControlPanel: SideFormControlPanel,
                Controller: SideFormController,
            },
        })

        this.actionService = useService('action');

        this.formviewPanel = useRef('formview-panel')
        this.formviewContainer = useRef('formview-container')

        useEffect(() => {
            this.onPatchedSideFormview();
            this.setResizeFormviewPanel();
        }, () => [this.props.resId])
    }

    setResizeFormviewPanel() {
        console.log("Interact INIT : ")
        if (!this.formviewPanel.el) {
            return
        }
        // Comprobar si llama a interact

        console.log("Interact INIT 2 : ")
        interact(this.formviewPanel.el).resizable({
            edges: {
                top: true,
                left: false,
                bottom: false,
                right: false,
            },
            listeners: {
                move: event => {
                    let {x, y} = event.target.dataset
                    console.log("xxxx : ", x)
                    console.log("yyy : ", y)
                    console.log("gaa : ", event.rect.width)
                    console.log("gaa : ", event.rect.height)
                    Object.assign(event.target.style, {
                        width: `${event.rect.width}px`,
                        height: `${event.rect.height}px`,
                        transform: `translate(${x}px, ${y}px)`
                    })

                    Object.assign(event.target.dataset, {x, y})
                },
            },
            modifiers: [
                interact.modifiers.restrictSize({min: {height: 400}}),
            ],
        })
        console.log("Interact INIT 3 : ")
    }

    onPatchedSideFormview() {
        const formViewEl = this.formviewContainer.el?.querySelector('.o_form_view')
        console.log("ACA POIBLE ERROR zero", formViewEl)
        // if (formViewEl) {
        //     console.log("ACA POIBLE ERROR 3")
        //     formViewEl.classList.remove('o_xxl_form_view')
        //     formViewEl.querySelector('.o_content > .flex-nowrap').classList.add('flex-column')
        // }
        console.log("ACA POIBLE ERROR 3")
    }

    get formViewProps() {
        const props = {
            resModel: this.props.resModel,
            resId: this.props.resId,
            viewId: this.props.viewId,
            display: {
                controlPanel: true,
            },
            context: {
                ...this.props.context,
            },
            className: 'o_xxs_form_view',
        }
        return props
    }

}

SideFormviewContainer.template = 'gastos_tqc.SideFormviewContainer';
SideFormviewContainer.props = {
    resModel: {
        type: String,
    },
    resId: {
        type: Number,
    },
    record: {
        type: Object,
    },
    viewId: {
        type: Number,
        optional: true,
    },
    context: {
        type: Object,
        optional: true,
    },
    mode: {
        type: String,
        optional: true,
    },
}
SideFormviewContainer.components = {
    FormView,
};
