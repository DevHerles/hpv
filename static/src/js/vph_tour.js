odoo.define('vph.tour', function(require) {
    "use strict";
     
    var core = require('web.core');
    var tour = require('web_tour.tour');
     
    var _t = core._t;
     
    tour.register('vph_tour', {
        url: "/web",
    }, [tour.STEPS.MENU_MORE, {
        trigger: '.o_app[data-menu-xmlid="minsa_main_menu_cancer"], .oe_menu_toggler[data-menu-xmlid="minsa_main_menu_cancer"]',
        content: _t('Explore the information in smarter way...'),
        position: 'bottom',
    } 
    , {
        trigger: ".oe_link",
        extra_trigger: '.oe_highlight',
        content:  _t("Information for second step of tour."),
        position: "right"
    }
    , {
        trigger: ".o_form_required",
        extra_trigger: '.oe_highlight',
        content:  _t("Information for third step of tour."),
        position: "top"
    }
    , {
        trigger: ".o_address_street",
        extra_trigger: '.oe_highlight',
        content:  _t("Information for next and so on"),
        position: "left"
    }
     
     
    ]);
     
    });