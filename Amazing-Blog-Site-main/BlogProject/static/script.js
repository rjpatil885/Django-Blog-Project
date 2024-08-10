document
    .querySelector('#searchButton')
    .addEventListener('click', function (event) {
        event.preventDefault(); // Prevent form submission

        document
            .querySelector('#searchInput')
            .classList
            .toggle('active');
        document
            .querySelector('#searchButton')
            .classList
            .toggle('active');
    });

    $('#desktopSearch').on('keyup', function (event) {
        event.preventDefault();
        var query = $('#searchInput').val();
        var resultsContainer = $('.searchResults');
    
        if (query !== "") {
            $.ajax({
                url: '/search/',
                data: {
                    'q': query
                },
                success: function (data) {
                    resultsContainer.empty();
    
                    if (data.length > 0) {
                        for (var i = 0; i < data.length; i++) {
                            var post = data[i];
                            var slug = post.title.toLowerCase().replace(/[^a-z0-9]/gi, '-');
                            var resultItem = $('<a>').text(post.title).attr('href','/detailed-blog/'+slug+'/').css({
                                'background-color': '#f2f2f2',
                                'padding': '10px',
                                'margin-bottom': '5px',
                                'display': 'block',
                                'text-decoration': 'none',
                                'color': '#000'
                            });
                            resultsContainer.append(resultItem);
                        }
                    } else {
                        var noResultsMessage = $('<div>').text('No results found.').css({
                            'background-color': '#f2f2f2',
                            'padding': '10px',
                            'margin-bottom': '5px'
                        });
                        resultsContainer.append(noResultsMessage);
                    }
                }
            });
        } else {
            resultsContainer.empty();
        }
    });
    
    $('.mobileSearch').on('keyup', function (event) {
        event.preventDefault();
        var query = $('.mobilesearchInput').val();
        var resultsContainer = $('.searchResults');
    
        if (query !== "") {
            $.ajax({
                url: '/search/',
                data: {
                    'q': query
                },
                success: function (data) {
                    resultsContainer.empty();
    
                    if (data.length > 0) {
                        for (var i = 0; i < data.length; i++) {
                            var post = data[i];
                            var slug = post.title.toLowerCase().replace(/[^a-z0-9]/gi, '-');
                            
                            var resultItem = $('<a>').text(post.title).attr('href','/detailed-blog/'+slug+'/').css({
                               
                                'background-color': '#f2f2f2',
                                'padding': '10px',
                                'margin-bottom': '5px',
                                'display': 'block',
                                'text-decoration': 'none',
                                'color': '#000'
                            });
                            resultsContainer.append(resultItem);
                        }
                    } else {
                        var noResultsMessage = $('<div>').text('No results found.').css({
                            'background-color': '#f2f2f2',
                            'padding': '10px',
                            'margin-bottom': '5px'
                        });
                        resultsContainer.append(noResultsMessage);
                    }
                }
            });
        } else {
            resultsContainer.empty();
        }
    });
    
    

function handleAction(url, slug, element) {
    $.ajax({
        type: 'GET',
        url: url,
        data: {
            'post_slug': slug
        },
        success: function (data) {
            if (data.success) {
                // Update the like count
                $('#like-count-total').text(data.like_count);
                   
                      var classValue = "btn btn-danger btn-sm";
                      if (element === "like") {
                        classValue = "btn btn-primary btn-sm";
                      }

                      var button = '<button id="' + element + '-button" class="' + classValue + '" name="' + slug + '">' + element + '</button>';
                      $('.like-dislike')
                      .empty().append(button)
                    
            } else {

                alert('You are not logged in. Please log in to like this button.');
            }
        },
        error: function (xhr, status, error) {
            console.log('AJAX Error:', status, error);
        }
    });
}

$('.likes').on('click', '#like-button', function () {
    var slug = $(this).attr('name');
    var url = "/like/";

    handleAction(url, slug, "dislike");
});

$('.likes').on('click', '#dislike-button', function () {
    var slug = $(this).attr('name');
    var url = "/dislike/";
    handleAction(url, slug, "like");
});

$(document).ready(function() {
    $('#comment-form').submit(function(event) {
      event.preventDefault();
  
      var form = $(this);
      var url = form.attr('action');
      var csrftoken = $('[name="csrfmiddlewaretoken"]').val();
  
      $.ajax({
        type: 'POST',
        url: url,
        data: form.serialize(),
        headers: {'X-CSRFToken': csrftoken},
        success: function(response) {
          if (response.success) {
            $('.errors').empty();
            $('.comment-message').html(`Comment submitted successfully.`);
            $('.comment-message').addClass('alert alert-success');
            setTimeout(function() {
              location.reload();
            }, 400);
          } else {
            if (response.login_required) {
              $('.errors').html("");
            } else {
              $('.errors').html(response.errors);
            }
            $('.comment-message').html("");
          }
        },
        error: function(xhr, status, error) {
          alert('Please log in to comment.');
        }
      });
    });
  });
  

  if ($('.messages').is(':visible')) {
    $('.messages').fadeOut('slow', function() {
      $(this).remove();
    });
  }

const currentYear = new Date().getFullYear();

document.getElementById('currentYear').textContent = currentYear;

// Get all elements with the 'mycategory' class
const categoryElements = document.querySelectorAll('.mycategory');

// Loop through each category element
categoryElements.forEach((element) => {
  const categoryID = element.id; // Get the ID of the category element

  // Generate a random color in hexadecimal format
  const randomColor = '#' + Math.floor(Math.random() * 16777215).toString(16);

  // Set the generated color as the background color of the category element
  element.style.backgroundColor = randomColor;
});
