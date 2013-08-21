// A janky function that deletes subscriptions via ajax
;$(function() {
    var do_delete = function(e) {
	var row = $(this).parent().parent();
        var id = row.attr('id');

        $.ajax({
            type: 'DELETE',
            url: $SCRIPT_ROOT + '/_unsubscribe/' + id, 
            beforeSend: function() {
                row.animate({'backgroundColor':'#fb6c6c'},300);
            },
            success: function() {
                row.fadeOut(300,function() {
                    row.remove();
                    if ($('#subtable').find('#unsubscribe').length == 0) {
                        $('#subtable').parent().text('You have no active subscriptions.')
                    }
                });
		$("tr[data-group-id='" + id + "'] .alert-info").removeClass("alert-info").addClass("alert-warning").text("Canceled");
	    }
        }); 
	
    };

    $('#unsubscribe').bind('click', do_delete);
  });

// Auto close the flash alert after a few seconds
function createAutoClosingAlert(selector, delay) {
   selector.slideUp(delay);
};
createAutoClosingAlert($('#flash').parent(), 2000);

// Info Tooltip for error messages
$(document).ready(function () {
    $('#error-msg').popover({trigger: "hover",
    html: true});
});
