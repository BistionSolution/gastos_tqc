odoo.define('gastos_tqc.WebClient', function (require) {
    "use strict";

    var WebClient = require('web.WebClient');
    var config = require('web.config');
    var core = require('web.core');
    var data_manager = require('web.data_manager');
    var dom = require('web.dom');
    var Menu = require('web.Menu');
    var session = require('web.session');

    var myAbtractweb = WebClient.include({
        start: function () {
            return this._super.apply(this, arguments);
        },
        on_menu_clicked: function (ev) {
            var self = this;
            console.log("click here")
            // return this._super.apply(this, arguments);
            return this.menu_dp.add(data_manager.load_action(ev.data.action_id))
                .then(function (result) {
                    // if (result.model_name === 'tqc.liquidaciones' || result.res_model === 'tqc.liquidaciones') {
                    //     self._rpc({ //envia el modelo, parametos
                    //         model: "tqc.liquidaciones",
                    //         method: "importar_exactus"
                    //     }).then(function (e) {
                    //         // puede ser para desactivar boton
                    //         // self.$el.find('dropdown-menu')
                    //         self.trigger_up('reload');
                    //     })
                    // }

                    self.$el.removeClass('o_mobile_menu_opened');

                    return self.action_mutex.exec(function () {
                        var completed = new Promise(function (resolve, reject) {
                            Promise.resolve(self._openMenu(result, {
                                clear_breadcrumbs: true,
                            })).then(resolve).guardedCatch(reject);

                            setTimeout(function () {
                                resolve();
                            }, 2000);
                        });
                        return completed;
                    });
                }).guardedCatch(function () {
                    self.$el.removeClass('o_mobile_menu_opened');
                });
        },
    });

    return myAbtractweb;
});
