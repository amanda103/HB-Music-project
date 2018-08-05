let formShows = $('form#form-shows');

function getUsers(evt) {
    let target = $(evt.target);
    console.log(target.data('show-id'));
    if (target.is(".show-clickable")) {
        target.removeClass("show-clickable");
        target.addClass("show");
        let showId = target.data('show-id');
        $.get('/friends', {'show_id': showId}, function(data) {
            let parent = target.parent();
            parent.append(data);
        });
    }
}


formShows.on('click', getUsers);