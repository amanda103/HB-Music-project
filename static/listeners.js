"use strict";

function displayRelatedArtists(evt) {
    $.get('/account'), {}, function(data) {
        $('#form').on('click', function(evt) {
            let target = $(evt.target);
        })
    }
}


let form = $('form');

function getRelatedArtists(evt) {
    let target = $(evt.target);
    console.log(target.data('artist-id'));
    if (target.is(".main-artists-clickable")) { // and target does not have class clicked
        target.removeClass("main-artists-clickable");
        target.addClass("main-artists");
        // add class to target to indicate that it has been clicked
        let artistId = target.data('artist-id');
        $.get('/related-artists', {'artist_id': artistId}, function(data) {
            let parent = target.parent();
            parent.append(data);
        });
    }

}

form.on('click', getRelatedArtists);

// add zipcode validator on submit
// add border on hover to main-artist
// 