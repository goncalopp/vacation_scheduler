function custom_post(url, data, other_options)
    {
    var csrftoken = $('meta[name=csrf_token]').attr('content')
    options=
        {
        type: "POST",
        url: url,
        data: data,
        beforeSend: function(xhr, settings) 
            {
            xhr.setRequestHeader("X-CSRFToken", csrftoken)
            }
        }
    options= $.extend(options, other_options)
    $.ajax(options)
    }

function post_or_fail(url, data)
    {
    options={
        error: function()
            {
            alert('An error occurred while sending data to the server. The page will be refreshed')
            location.reload()
            }
        }
    custom_post(url, data, options)
    }

function get_authenticated_user()
    {
    return $('meta[name=authenticated_user]').attr('content')
    }
    
function delete_user_events_in_date(date, callback)
    {
    deleted_any= false
    user= get_authenticated_user()
    function shall_delete(event)
        {
        same_date= (String(event.start)==String(date))
        same_user= (event.title==user)
        del= (same_date && same_user)
        if (del)
            {
            deleted_any=true
            callback(event)
            $("#available-vacations").text(Number($("#available-vacations").text())+1)
            }
        return del
        }
    $('#calendar').fullCalendar( 'removeEvents', shall_delete)
    return deleted_any
    }

function remote_event_delete( event )
        {
        date_string= $.fullCalendar.formatDate( event.start, 'u') //ISO8601
        post_or_fail('events', {date:date_string, delete:true})
        }
        
function click_day(date, allDay, jsEvent, view) 
    {
    if (!get_authenticated_user())
        return
    deleted_any= delete_user_events_in_date(date, remote_event_delete)
    if (!deleted_any)
        {
        newevent= {title: get_authenticated_user(), start: date, color: "#aa0000"}
        date_string= $.fullCalendar.formatDate( date, 'u') //ISO8601
        post_or_fail('events', {date:date_string})
        $('#calendar').fullCalendar('renderEvent', newevent)
        $("#available-vacations").text($("#available-vacations").text()-1)
        }
    }

function click_event(event)
    {
    click_day(event.start)
    }
