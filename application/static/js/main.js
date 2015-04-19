$(document).ready(function(){
    namespace = ""; // change to an empty string to use the global namespace

    // the socket.io documentation recommends sending an explicit package upon connection
    // this is specially important when using the global namespace
    var socket = io.connect("http://" + document.domain + ':' + location.port);
    
    socket.on("connect", function() {
        socket.emit("join_user", { room: $("#room_id").val(), 
                                  user_name: document.getElementById("username").innerHTML
                                });
    });

    socket.on("new_user", function(msg) {
        if (document.getElementById("username").innerHTML != msg["user"]) {
            $("#users").append("<span>"+msg["user"]+"</span>");
        }
    });
    socket.on("new_message", function(msg) {
        $("#message_list").append("<tr><td>"+msg["user"]+"</td><td>"+msg["data"]+"</td><td>"+msg["time"]+"</td></tr>");
    });

    $("form#post_content").submit(function(event) {
        if ($("#message_content").val()) { 
            socket.emit("post_message", {room: $("#room_id").val(), 
                                        data: $("#message_content").val(),
                                        user: document.getElementById("username").innerHTML});
        }
        return false;
    })

    $("form#leave").submit(function(event) {
        socket.emit("leave", {room: $("#room_id").val()});
        return false;
    });
});
