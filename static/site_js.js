function get_authenticated_user()
    {
    return $('meta[name=authenticated_user]').attr('content')
    }

function get_csrf_token()
    {
    return $('meta[name=csrf_token]').attr('content')
    }

function get_username_id()
    {
    return $('meta[name=login_form_username_id]').attr('content')
    }

function get_password_id()
    {
    return $('meta[name=login_form_password_id]').attr('content')
    }

function custom_post(url, data, other_options)
    {
    options=
        {
        type: "POST",
        url: url,
        data: data,
        beforeSend: function(xhr, settings) 
            {
            xhr.setRequestHeader("X-CSRFToken", get_csrf_token())
            }
        }
    options= $.extend(options, other_options)
    $.ajax(options)
    }

function post_or_fail(url, data)
    {
    options={
        error: function(request)
            {
            alert('An error occurred while sending data to the server. The page will be refreshed\n'+request.responseText)
            location.reload()
            }
        }
    custom_post(url, data, options)
    }
    
function delete_user_events_in_date(date, callback)
    {
    deleted_any= false
    user= get_authenticated_user()
    function shall_delete(event)
        {
        same_date= (String(event.start)==String(date))
        same_user= (event.title.substr(0,user.length)==user)
        is_vacation= event.title==user
        del= (same_date && same_user)
        if (del)
            {
            deleted_any=true
            callback(event)
            if (is_vacation)
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
        type= $("#event-type").val()
        typestring= $("#event-type option:selected").text()
        title= get_authenticated_user()
        if (typestring!="")
            title+=" ("+typestring+")"
        newevent= {title: title, start: date, color: "#aa0000"}
        date_string= $.fullCalendar.formatDate( date, 'u') //ISO8601
        post_or_fail('events', {date:date_string, type:type})
        $('#calendar').fullCalendar('renderEvent', newevent)
        if (type==0)
            $("#available-vacations").text($("#available-vacations").text()-1)
        }
    }

function click_event(event)
    {
    click_day(event.start)
    }

function setup_login_dialog()
    {
    $( "#login-button" ).button()
    $( "#login-dialog" ).dialog({modal: true, autoOpen: false});
    $( "#"+get_password_id() ).keyup(
        function(event)
            {
            if(event.keyCode == 13)
                {
                $("#login-button").click();
                }
            }
        );
    $( "#login-button").click( post_login )
    }
    
function show_login_dialog()
    { 
    $( "#login-dialog" ).dialog( "open" );
    }

function post_login()
    {
    username = $( "#"+get_username_id() )[0].value
    password = $( "#"+get_password_id() )[0].value
    options={
        error: function(request)
            {
            tips = $( "#login-errors" );
            tips.text(request.responseText)
            },
        success: function(request)
            {
            tips = $( "#login-errors" );
            tips.text()
            location.reload()
            }
        }
    custom_post('login', {username:username, password:password}, options)
    }
