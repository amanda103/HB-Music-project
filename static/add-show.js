// TODO: on toggle, remove button, say show has been added!


"use strict";

let button = $('button.add-show');

function addShow(evt) {
    let target = $(evt.target);
    console.log(target.data('event-id'));
    if (target.is(".add-show")) {
        let eventId = target.data('event-id');
        $.get("/add-show/"+eventId, function() {
            target.hide();
            $('#success-' + eventId).show();
        });

         // function(data) {
            // TODO: change to event added instead of button

        }
    }

button.on('click', addShow);