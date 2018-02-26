odoo.define('vph.tour', function(require) {
    "use strict";
    
    var core = require('web.core');
    var tour = require('web_tour.tour');
    
    var _t = core._t;
    
    tour.register('vph_tour', {
        url: "/web",
    }, [tour.STEPS.MENU_MORE, {
        trigger: '.o_app[data-menu-xmlid="modulos_registros.minsa_verificar_sobre_main_menu"]',
        content: _t('Want to <b>create customers</b>?<br/><i>Click on Contacts to start.</i>'),
        position: 'bottom',
        }
    ]);
});