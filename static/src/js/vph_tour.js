odoo.define('vph.tour', function(require) {
    "use strict";
     
    var core = require('web.core');
    var tour = require('web_tour.tour');
     
    var _t = core._t;
     
    tour.register('vph_tour', {
        url: "/web",
    }, [tour.STEPS.MENU_MORE, {
            trigger: '.o_app[data-menu-xmlid="modulos_registros.minsa_cancer_registros_main_menu"], .oe_menu_toggler[data-menu-xmlid="modulos_registros.minsa_cancer_registros_main_menu"]',
            content: _t('Quieres <b>distribuir Sobres</b>?<br/><i>Haga click aquí para empezar.</i>'),
            position: 'bottom',
        },
    ]);     
});