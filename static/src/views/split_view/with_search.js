/** @odoo-module **/

import { WithSearch, SEARCH_KEYS } from '@web/search/with_search/with_search';

SEARCH_KEYS.push('resId')

WithSearch.props.resId = { type: [Number, { value: null }, { value: false }], optional: true }