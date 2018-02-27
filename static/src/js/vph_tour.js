odoo.define('vph.tour', function(require) {
    "use strict";
     
    var core = require('web.core');
    var tour = require('web_tour.tour');
     
    var _t = core._t;
     
    tour.register('vph_tour', {
        url: "/web",
    }, [tour.STEPS.MENU_MORE, {
            trigger: '.o_app[data-menu-xmlid="modulos_registros.minsa_entrega_registros_menu"]',
            content: _t('Quieres <b>distribuir Sobres</b>?<br/><i>Haga click aquí para empezar.</i>'),
            position: 'bottom',
        }, {
            trigger: '.oe_menu_leaf[data-menu-xmlid="modulos_registros.minsa_registros_menu"]',
            content: _t('Quieres <b>ver los reportes</b>?<br/><i>Haga click aquí para empezar.</i>'),
            position: 'bottom',
        }, {
            trigger: '.oe_menu_leaf[data-menu-xmlid="modulos_registros.minsa_registros_pap_main_menu"]',
            content: _t('Quieres <b>registrar PAP</b>?<br/><i>Haga click aquí para empezar.</i>'),
            position: 'bottom',
        }, {
            trigger: '.oe_menu_leaf[data-menu-xmlid="modulos_registros.minsa_procedimientos_menu"]',
            content: _t('Quieres <b>registrar Procedimientos</b>?<br/><i>Haga click aquí para empezar.</i>'),
            position: 'bottom',
        }, {
            trigger: '.oe_menu_leaf[data-menu-xmlid="modulos_registros.minsa_verificar_sobre_main_menu"]',
            content: _t('Quieres <b>registrar Sobres</b>?<br/><i>Haga click aquí para empezar.</i>'),
            position: 'bottom',
        }, {
            trigger: '.oe_menu_leaf[data-menu-xmlid="modulos_registros.minsa_registros_sobre1_main_menu"]',
            content: _t('Quieres <b>registrar Sobres</b>?<br/><i>Haga click aquí para empezar.</i>'),
            position: 'bottom',
        }, {
            trigger: '.o_list_button_add',
            content: _t('Haga click para crear.'),
            position: 'bottom',
            width: 200,
        }, 
    ]);     
});