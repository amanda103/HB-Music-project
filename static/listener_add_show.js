"use strict";


let button = $('button.add-show');

// function removeButton(evt) {
//     let target = $(evt.target);
//     console.log(target.data('show-id'));
//     if (target.is(".add-show")) {
//         let showId = target.data('show-id');
//         $.get('/', {'show_id': showId}, function(data) {
//             let parent = target.parent();
//             parent.append(data);
//         });
//     }
// }


button.on('click', function() {
    button.hide();
    $("#hidden-div").show()
});