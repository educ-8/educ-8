$(function() {

  console.log('main.js loaded');  

  $('#search-form').on('submit', function(e){
    e.preventDefault();
    search_term = $.trim($('#search-term').val())
    console.log("form submitted");
    console.log(search_term);
    $('#results').empty();
    $('#status').text('Searching for ' + search_term + '...');
    search()
  });

  function search() {
    console.log("search() is working!")
    $.ajax({
      url: "search/", //the endpoint
      data: { search_term: $.trim($('#search-term').val())},
      success: function(json) {
        $('#search-term').val('');
        console.log(json);
        if (json.hasError) {
            $('#status').empty().append(json.message);
        } else {
            showResults(json);
            $('#')
        }
      },
      error: function(xhr, errmsg, err) {
        console.log(xhr.status + ": " + xhr.responseText);
        $('#status').empty().append(errmsg);
      }
    });
  };

});

function showResults(results) {
    var resultsList = $('<ul></ul>').css('list-style-type', 'none');
    results.forEach(function (result){
        var resultsListItem = $('<li></li>').addClass('search-result');
        var image = $('<img src="' + result.url + '">');
        var user = $('<h4>' + result.username + '</h4>');
        var avatar = $('<img src="' + result.avatar + '"">').css('height', '50px');
        console.log(avatar);
        var location = $('<p>' + result.location_name + '</p>');
        var created = $('<p>' + result.created.substring(0,10) + '</p>');
        var caption = $('<p>' + result.caption + '</p>');
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
}

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
