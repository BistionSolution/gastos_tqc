/** @odoo-module **/

import {registry} from "@web/core/registry";
import {listView} from "@web/views/list/list_view";
import {ListRenderer} from "@web/views/list/list_renderer";
// import { HeaderFlujo } from "./header_flujo";
import {HeaderFlujo} from '@gastos_tqc/views/header_flujo';
import {NewListView} from "@gastos_tqc/views/split_view/list_renderer";

// export class HeaderFlujoRenderer extends ListRenderer {
// }

// HeaderFlujoRenderer.template = 'gastos_tqc.headerFlujo';
// HeaderFlujoRenderer.components = Object.assign({}, ListRenderer.components, {HeaderFlujo})

// export const HeaderFlujoListView = {
//     ...listView,
//     Renderer: HeaderFlujoRenderer,
// };

export class HeaderFlujoRenderer extends NewListView {
}

HeaderFlujoRenderer.template = 'gastos_tqc.headerFlujo';
HeaderFlujoRenderer.components = Object.assign({}, ListRenderer.components, {HeaderFlujo})

export const HeaderFlujoListView = {
    ...listView,
    Renderer: HeaderFlujoRenderer,
};


// registry.category("views").add("header_gastos_approve", HeaderFlujoListView);
registry.category("views").add("header_gastos_approve", HeaderFlujoListView);


