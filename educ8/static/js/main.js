$(function() {

  $('#search-form').on('submit', function(e){
    e.preventDefault();
    var search_term = $.trim($('#search-term').val())
    $('#results').empty();
    var statusMessage = $('<p>Searching for ' + search_term + '...</p>').addClass('status-message');
    $('#status').append(statusMessage);
    $('.status-message').fadeIn(1000);
    search()
    var progress = setInterval(function(){
        $('.status-message').animate({
            opacity: 0.40
        }, 1000, function(){
            $('.status-message').animate({
                opacity: 1
            }, 1000)
        })
    }, 2200);
  });  
});

function search() {
$.ajax({
  url: "search/", //the endpoint
  data: { search_term: $.trim($('#search-term').val())},
  success: function(json) {
    $('#search-term').val('');
    if (json.hasError) {
        $('#status').empty().append(json.message);
    } else {
        showResults(json);
        $('#')
    }
  },
  error: function(xhr, errmsg, err) {
    $('.status-message').fadeOut();
    $('#status').empty().append(errmsg);
  }
});
};

function showResults(results) {
    var resultsList = $('<ul></ul>');
    results.forEach(function (result){
        var resultsListItem = $('<li></li>').addClass('search-result');
        var user = $('<h4>' + result.username + '</h4>').addClass('ig-username');
        var avatar = $('<img src="' + result.avatar + '"">').addClass('ig-avatar');
        var created = $('<p>' + result.created.substring(0,10) + '</p>').addClass('ig-created');
        var location = $('<p>' + result.location_name + '</p>').addClass('ig-location');
        var image = $('<img src="' + result.url + '">').addClass('ig-main-image');
        var caption = $('<p>' + result.caption + '</p>').addClass('ig-caption');

        // handler to confirm images loaded
        $(image, avatar).on('error', function(){
            console.log("main image didn't load");
            $(this).parent().remove();
        });

        resultsListItem.append(user)
            .append(avatar)
            .append(created)
            .append(location)
            .append(image)
            .append(caption);
        resultsList.append(resultsListItem);
    });
    $('#status').empty();
    $('#results').empty().append(resultsList);
};

// Form post security script
// This function gets cookie with a given name
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
var csrftoken = getCookie('csrftoken');

/*
The functions below will create a header with csrftoken
*/

function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}
function sameOrigin(url) {
    // test that a given url is a same-origin URL
    // url could be relative or scheme relative or absolute
    var host = document.location.host; // host + port
    var protocol = document.location.protocol;
    var sr_origin = '//' + host;
    var origin = protocol + sr_origin;
    // Allow absolute or scheme relative URLs to same origin
    return (url == origin || url.slice(0, origin.length + 1) == origin + '/') ||
        (url == sr_origin || url.slice(0, sr_origin.length + 1) == sr_origin + '/') ||
        // or any other URL that isn't scheme relative or absolute i.e relative.
        !(/^(\/\/|http:|https:).*/.test(url));
}

$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type) && sameOrigin(settings.url)) {
            // Send the token to same-origin, relative URLs only.
            // Send the token only if the method warrants CSRF protection
            // Using the CSRFToken value acquired earlier
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});
