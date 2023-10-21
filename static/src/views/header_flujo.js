/** @odoo-module */
import {useService} from "@web/core/utils/hooks";
// import {FormView} from "./split_view/form_view";
// import {SideFormviewContainer} from "./split_view/side_form_view_container";

const {Component, onWillStart, onRendered, onMounted} = owl;
var session = require('web.session');
export class HeaderFlujo extends Component {
    setup() {
        this.orm = useService("orm");
        this.action = useService("action");
        onWillStart(async () => {
            const module_name = this.env.searchModel.resModel
            console.log("module_name : ", module_name)
            this.countData = await this.orm.call(
                module_name,
                "get_count_states",
                [session.user_id[0]]
            );
            // this.select = 'HII'
            this.env.searchModel
            this.select = this.env.searchModel._domain[2][2]
        });
    }

    /**
     * This method clears the current search query and activates
     * the filters found in `filter_name` attibute from button pressed
     */

    setSearchContext(ev) {
        let filter_name = ev.currentTarget.getAttribute("filter_name");
        let filters = filter_name.split(',');

        this.select = filters[0]
        let searchItems = this.env.searchModel.getSearchItems((item) => filters.includes(item.name));
        this.env.searchModel.query = [];
        for (const item of searchItems) {
            this.env.searchModel.toggleSearchItem(item.id);
        }
    }
}

HeaderFlujo.template = 'gastos_tqc.headerChild'
