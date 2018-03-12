var reference = document.querySelector('.oe_menu_leaf');
var popper = document.querySelector('.my-popper');
new Tooltip(reference, {
    placement: 'top', // or bottom, left, right, and variations
    title: "Top"
});